"""Manages Assistant flows."""
import json
import time

from utilities.env_helper           import EnvHelper
from utilities.llm_helper           import LLMHelper
from utilities.observability_helper import ObservabilityHelper
from utilities.openapi_helper       import OpenAPIHelper


class Manager:
    """App manager class."""

    def __init__(self, session_id):
        """Initialize a manager for a given session. It has a container for threads."""
        self.session_id = session_id
        self.thread_container = {}

        self.llm_helper = LLMHelper()
        self.env_helper = EnvHelper()
        self.observability_helper = ObservabilityHelper()

        self.api_response_sleep_time = 1
        self.verbose = True

        with open('ikea_openapi.json', 'r', encoding="utf-8") as file:
            self.openapi_spec = json.load(file)

    def get_message_list(self, assistant_id):
        """Get messages for current thread in assistant. Exposed to pages."""
        if assistant_id in self.thread_container:
            thread_id = self.thread_container[assistant_id]
            return self.get_thread_messages(thread_id)
        else:
            return []

    def are_there_assistants(self):
        """Check if are the assistants."""
        return len(self.get_assistant_list()) > 0

    def get_assistant_list(self):
        """Get Assistant list."""
        assistant_list = self.llm_helper.get_assistants()
        return assistant_list

    def get_assistant_id_name_tuple_list(self):
        """Get Assistant id and names."""
        assistant_list = self.get_assistant_list()
        assistant_name_id_list = [(assistant.id, assistant.name) for assistant in assistant_list]

        return assistant_name_id_list

    def get_assistant_name_list(self):
        """Get Assistant names."""
        assistant_list = self.get_assistant_list()
        assistant_name_list = [assistant.name for assistant in assistant_list]

        return assistant_name_list

    def get_assistant(self, assistant_id):
        """Get Assistant by id."""
        assistant = self.llm_helper.get_assistant(assistant_id)

        return assistant

    def get_assistant_field(self, assistant_name, assistant_field):
        """Get a field of a given assistance."""
        assistant_list = self.get_assistant_list()
        assistant_field = [getattr(assistant, assistant_field, "") for assistant in assistant_list if assistant.name == assistant_name][0]

        return assistant_field

    def get_thread(self, assistant_id):
        """Run a thread with the assistant."""
        if assistant_id not in self.thread_container:
            thread_id = self.llm_helper.create_assistant_thread()
            # Single thread per assistant. All files to be sent
            self.thread_container[assistant_id] = {}
            self.thread_container[assistant_id]['thread_id'] = thread_id
            self.thread_container[assistant_id]['files'] = set()

        return self.thread_container[assistant_id]['thread_id']

    def get_thread_messages(self, thread_id):
        """Initialize a manager for a given session. It has a container for threads."""
        raw_messages = self.llm_helper.get_assistant_thread_messages(thread_id)
        self.observability_helper.log(f"Returned raw messages of type {type(raw_messages)} in {thread_id} are {raw_messages}", self.verbose)
        if len(raw_messages) > 0:
            message_list = [{'message_value': message.content[0].text.value, 'message_role': message.role} for message in raw_messages]
            return message_list
        else:
            return []

    def get_uploaded_files(self, assistant_id):
        """Get uploaded files by the user for current thread in assistant."""
        return list(self.thread_container[assistant_id]['files'])

    def run_thread(self, prompt, assistant_id):
        """Run a thread with the assistant."""
        # Get or create a thread
        thread_id = self.get_thread(assistant_id)
        # Get files in thread
        file_ids = self.get_uploaded_files(assistant_id)

        # Add message to thread (llm)
        self.llm_helper.add_message_to_assistant_thread(thread_id, "user", prompt, file_ids)

        run = self.llm_helper.create_assistant_thread_run(thread_id, assistant_id, "Do your best")

        while run.status != "completed":
            self.observability_helper.log(f"Run status is {run.status}", self.verbose)
            if run.status == 'requires_action':
                self.observability_helper.log(f"Required action type is {run.required_action.type}", self.verbose)
                if run.required_action.type == 'submit_tool_outputs':
                    tool_output_list = []
                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        tool_id       = tool_call.id
                        function_name = tool_call.function.name
                        function_args = tool_call.function.arguments
                        self.observability_helper.log(f"Required calling function {function_name} with args {function_args}")
                        function_call_result = OpenAPIHelper.call_function(function_name, function_args, self.openapi_spec)
                        self.observability_helper.log(f"Function result is {function_call_result}", self.verbose)

                        tool_call_output = {
                            "tool_call_id": tool_id,
                            "output": function_call_result
                        }

                        tool_output_list.append(tool_call_output)

                    self.llm_helper.submit_tool_outputs_to_assistant_thread_run(thread_id, run.id, tool_output_list)

            time.sleep(self.api_response_sleep_time)

            run = self.llm_helper.get_assistant_thread_run(thread_id, run.id)

        message_list = self.get_thread_messages(thread_id)

        return message_list

    def upload_file(self, uploaded_file, verbose=False):
        """Upload a file."""
        bytes_data = uploaded_file.getvalue()
        self.observability_helper.log(f"Uploading file {uploaded_file.name}", verbose)
        upload_success, file_id = self.llm_helper.upload_file(bytes_data)

        if upload_success:
            self.observability_helper.log(f"Uploading success. File id {file_id}", verbose)
        else:
            self.observability_helper.log(f"Uploading of file id {file_id} failed", verbose)

        return upload_success, file_id

    def track_assistant_file_for_messages(self, assistant_id, file_id, verbose=True):
        """Add assistant to file."""
        self.thread_container[assistant_id]['files'].add(file_id)
        self.observability_helper.log(f"File {file_id} to assistant id {assistant_id} OK", verbose)

    def upload_file_to_assistant(self, assistant_id, uploaded_file, verbose=True):
        """Push file to assistants."""
        upload_success, file_id = self.upload_file(uploaded_file)

        upload_to_assistant = False

        if upload_success:
            self.observability_helper.log(f"Upload to AOAI OK. File id {file_id}", verbose)
            if self.llm_helper.create_assistant_file(assistant_id, file_id):
                self.observability_helper.log(f"Uploading file {file_id} to assistant id {assistant_id} OK", verbose)
                upload_to_assistant = True
            else:
                self.observability_helper.log(f"Uploading file {file_id} to assistant id {assistant_id} KO", verbose)
                return None
        else:
            self.observability_helper.log(f"Uploading file {file_id} failed", verbose)
            return None

        return upload_to_assistant, file_id

    def upload_file_for_assistant_messages(self, assistant_id, uploaded_file, verbose=True):
        """Push file to assistants."""
        upload_success, file_id = self.upload_file(uploaded_file)

        if upload_success:
            self.observability_helper.log(f"Upload to AOAI OK. File id {file_id}", verbose)
            self.track_assistant_file_for_messages(assistant_id, file_id)

        else:
            self.observability_helper.log(f"Uploading file {file_id} failed", verbose)

        return upload_success
