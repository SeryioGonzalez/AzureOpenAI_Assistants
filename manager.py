"""Manages Assistant flows"""
import json
import time

from utilities.env_helper           import EnvHelper
from utilities.llm_helper           import LLMHelper
from utilities.observability_helper import ObservabilityHelper
from utilities.openapi_helper       import OpenAPIHelper

class Manager:
    """App manager class"""

    def __init__(self, session_id):
        self.session_id = session_id
        self.thread_container = {}
        #self.message_list = {}
        #self.uploaded_files = {}
        self.api_response_sleep_time = 1

        self.llm_helper = LLMHelper()
        self.env_helper= EnvHelper()
        self.observability_helper = ObservabilityHelper()
        self.verbose = True
        self.observability_helper.log(f"New Manager created for session id {self.session_id}", self.verbose)

        with open('ikea_openapi.json', 'r') as file:
            self.openapi_spec = json.load(file)

    def log(self, log):
        self.observability_helper.log(log, self.verbose)
        
    def get_message_list(self, assistant_id):
        if assistant_id in self.thread_container:
            thread_id = self.thread_container[assistant_id]
            return self.get_thread_messages(thread_id)
        else:
            return []

    def are_there_assistants(self):
        """Checks if are the assistants"""
        return len(self.get_assistant_list()) > 0

    def get_assistant_list(self):
        """Get Assistant list"""
        assistant_list = self.llm_helper.get_assistants()
        return assistant_list

    def get_assistant_id_name_tuple_list(self):
        """Get Assistant id and names"""
        assistant_list = self.get_assistant_list()
        assistant_name_id_list = [(assistant.id, assistant.name) for assistant in assistant_list]

        return assistant_name_id_list
    
    def get_assistant_name_list(self):
        """Get Assistant names"""
        assistant_list = self.get_assistant_list()
        assistant_name_list = [assistant.name for assistant in assistant_list]

        return assistant_name_list

    def get_assistant(self, assistant_id):
        """Get Assistant by id"""
        assistant = self.llm_helper.get_assistant(assistant_id)
        
        return assistant

    def get_assistant_field(self, assistant_name, assistant_field):
        """Gets a field of a given assistance"""
        assistant_list = self.get_assistant_list()
        assistant_field = [getattr(assistant, assistant_field, "") for assistant in assistant_list if assistant.name == assistant_name][0]

        return assistant_field

    def get_thread(self, assistant_id):
        """Runs a thread with the assistant"""
        if assistant_id not in self.thread_container:
            thread_id = self.llm_helper.create_assistant_thread()
            #Single thread per assistant. All files to be sent
            self.thread_container[assistant_id] = {}
            self.thread_container[assistant_id]['thread_id'] = thread_id 
            self.thread_container[assistant_id]['files']  = set()
        
        return self.thread_container[assistant_id]['thread_id']

    def get_thread_messages(self, thread_id):
        raw_messages = self.llm_helper.get_assistant_thread_messages(thread_id)
        if len(raw_messages) > 0:
            message_list = [{'message_value':message.content[0].text.value, 'message_role': message.role} for message in raw_messages.data ]

            return message_list
        else:
            return []

    def get_uploaded_files(self, assistant_id):
        return self.thread_container[assistant_id]['files']

    """
    def add_message_to_thread(self, assistant_id, message_content, message_role):
        message = {"role": message_role, "content": message_content}
        self.thread_container[assistant_id]['messages'].append(message)
    """
    def run_thread(self, prompt, assistant_id):
        """Runs a thread with the assistant"""
        #Get or create a thread
        thread_id = self.get_thread(assistant_id)
        #Get files in thread
        assistant_file_ids = self.get_uploaded_files(assistant_id)
        
        #Add message to thread (llm)
        self.llm_helper.add_message_to_assistant_thread(thread_id, "user", prompt, assistant_file_ids)

        run = self.llm_helper.create_assistant_thread_run(thread_id, assistant_id, "Do your best")
        
        while run.status != "completed":
            self.observability_helper.log(f"Run status is {run.status}", self.verbose)
            if run.status == 'requires_action':
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
        """Uploads a file"""
        bytes_data = uploaded_file.getvalue()
        self.observability_helper.log(f"Uploading file {uploaded_file.name}", verbose)
        upload_success, file_id = self.llm_helper.upload_file(bytes_data)

        if upload_success:
            self.observability_helper.log(f"Uploading success. File id {file_id}", verbose)
        else:
            self.observability_helper.log(f"Uploading of file id {file_id} failed", verbose)


        return upload_success, file_id

    def track_assistant_file_for_messages(self, assistant_id, file_id, verbose=True):
        """Adds assistant to file"""
        thread_id = self.get_thread(assistant_id)
        self.thread_container[assistant_id]['files'].add(file_id)
        self.observability_helper.log(f"File {file_id} to assistant id {assistant_id} OK", verbose)

    def upload_file_to_assistant(self, assistant_id, uploaded_file, verbose=True):
        """Pushes file to assistants"""
        upload_success, file_id = self.upload_file(uploaded_file)

        upload_to_assistant = False

        if upload_success:
            self.observability_helper.log(f"Upload to AOAI OK. File id {file_id}", verbose)
            if self.llm_helper.create_assistant_file(assistant_id, file_id):
                #self.track_assistant_file(assistant_id, file_id)
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
        """Pushes file to assistants"""
        upload_success, file_id = self.upload_file(uploaded_file)
        
        if upload_success:
            self.observability_helper.log(f"Upload to AOAI OK. File id {file_id}", verbose)
            self.track_assistant_file_for_messages(assistant_id, file_id)
            
        else:
            self.observability_helper.log(f"Uploading file {file_id} failed", verbose)
            
        return upload_success 
