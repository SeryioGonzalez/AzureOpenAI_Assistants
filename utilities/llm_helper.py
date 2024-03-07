"""Module managing LLM interaction."""
import json
import io
import openai
from openai import AzureOpenAI
from openai.pagination import SyncCursorPage
from openai.types.beta.assistant import ToolFunction
from openai.types.beta.assistant import ToolCodeInterpreter

from utilities.env_helper   import EnvHelper
from utilities.observability_helper import ObservabilityHelper

class LLMHelper:
    """Class managing LLM interaction."""

    conversation_starter_prefix = "conversation_starter_"

    def __init__(self):
        """Initialize the LLM Helper."""
        self.env_helper = EnvHelper()
        self.observability_helper = ObservabilityHelper()
        self.llm_client = AzureOpenAI(
            azure_endpoint=self.env_helper.OPENAI_API_BASE,
            api_key=self.env_helper.OPENAI_API_KEY,
            api_version=self.env_helper.AZURE_OPENAI_API_VERSION
        )
        self.openai_deployment = self.env_helper.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME
        self.verbose = True

    def update_env_related_attributes(self):
        self.env_helper = EnvHelper()

        self.llm_client = AzureOpenAI(
            azure_endpoint=self.env_helper.OPENAI_API_BASE,
            api_key=self.env_helper.OPENAI_API_KEY,
            api_version=self.env_helper.AZURE_OPENAI_API_VERSION
        )
        self.openai_deployment = self.env_helper.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME

    def is_duplicated_assistant(self, new_assistant_name):
        """Check if the assistant is duplicated."""
        existing_assistant_names = [assistant.name for assistant in self.get_assistants()]

        return new_assistant_name in existing_assistant_names

    def create_assistant(self, assistant_name, assistant_description, assistant_instructions):
        """Crate assistants. Public."""
        self._create_assistant(assistant_name, assistant_description, assistant_instructions, [])

    def _create_assistant(self, assistant_name: str, description: str, instructions: str, tools: list):
        """Crate assistants. Private."""
        assistant = self.llm_client.beta.assistants.create(
            name=assistant_name,
            description=description,
            instructions=instructions,
            tools=tools,
            model=self.openai_deployment
        )

        return assistant

    def get_assistant_conversation_starter_values(self, assistant, assistant_id=None):
        """Get assistant conversation starters."""
        # In some scenarios, we do not have the assistant object
        if assistant_id is not None:
            assistant = self.get_assistant(assistant_id)
        # Values from metadata keys starting wiht prefix and non empty values
        this_assistant_conv_starter_values = [value for key, value in assistant.metadata.items()
                                              if key.startswith(self.conversation_starter_prefix) and
                                                value != ""]
        return this_assistant_conv_starter_values

    def get_assistant_conversation_starters(self, assistant):
        """Get assistant conversation starters."""
        # Metadata key-pairs starting with prefix
        this_assistant_conv_starters = {key:value for key, value in assistant.metadata.items() if key.startswith(self.conversation_starter_prefix)}
        return this_assistant_conv_starters

    def update_conv_starter(self, assistant_id, conv_starter_id, conv_starter_text):
        """Update conversation starter."""
        assistant = self.get_assistant(assistant_id)
        conv_starters = self.get_assistant_conversation_starters(assistant)

        if conv_starter_id == "new":
            first_empty_key = [key for key, value in conv_starters.items() if value == ""]
            if len(first_empty_key) == 0:
                key = f"{self.conversation_starter_prefix}{len(conv_starters)}"
            else:
                key = first_empty_key[0]
        else:
            key = f"{self.conversation_starter_prefix}{conv_starter_id}"
        conv_starters[key] = conv_starter_text

        self.modify_assistant_metadata(assistant_id, conv_starters)

    def create_assistant_file(self, assistant_id, file_id):
        """Upload the file to OpenAI."""
        file_upload_to_assistant_response = self.llm_client.beta.assistants.files.create(
            assistant_id, file_id=file_id
        )

        if file_upload_to_assistant_response.id is not None:
            self.observability_helper.log("LLM HELPER - Uploading file to assistant OK", self.verbose)
            return True

        self.observability_helper.log("LLM HELPER - Uploading file to assistant failed", self.verbose)
        return False

    def get_assistants(self):
        """List Assistants."""
        try:
            assistant_list = self.llm_client.beta.assistants.list().data
            return assistant_list
        except:
            return None

    def get_assistant_files(self, assistant_id):
        """List Assistants files."""
        assistant_list = self.llm_client.beta.assistants.files(assistant_id)

        return assistant_list

    def get_assistant(self, assistant_id):
        """Get Assistants."""
        assistant = self.llm_client.beta.assistants.retrieve(assistant_id)
        return assistant

    def get_assistant_file(self, assistant_id, file_id):
        """To be done."""
        return None

    def modify_assistant_metadata(self, assistant_id, assistant_medatata):
        """Modify assistant medatata."""
        self.observability_helper.log(f"LLM HELPER - For assistant {assistant_id}, update conv starter {assistant_medatata}", self.verbose)

        self.llm_client.beta.assistants.update(
            assistant_id,
            metadata=assistant_medatata
        )

    def delete_assistant(self, assistant_id):
        """Delete assistant."""
        try:
            self.observability_helper.log(f"LLM HELPER - Deleting assistant {assistant_id}", self.verbose)
            self.llm_client.beta.assistants.delete(assistant_id)
        except openai.NotFoundError:
            self.observability_helper.log(f"LLM HELPER - Assistant {assistant_id} does not exist", self.verbose)

    def delete_assistant_file(self, assistant_id, file_id):
        """To be done."""
        return None

    def create_assistant_thread(self):
        """Create Assistant Thread."""
        thread = self.llm_client.beta.threads.create()

        return thread.id

    def get_assistant_thread(self, thread_id):
        """To be done."""
        return None

    def modify_assistant_thread(self, thread_id):
        """To be done."""
        return None

    def delete_assistant_thread(self, thread_id):
        """To be done."""
        return None

    def add_message_to_assistant_thread(self, thread_id, message_role, message_content, file_ids):
        """Add message to Assistant thread."""
        self.observability_helper.log(f"LLM HELPER - Message, content: {message_content} role: {message_role} to thread {thread_id}, file ids:  {file_ids}", self.verbose)

        self.llm_client.beta.threads.messages.create(
            thread_id=thread_id,
            role=message_role,
            content=message_content,
            file_ids=file_ids
        )

    def get_messages_in_assistant_thread(self, thread_id):
        """List messages in thread."""
        messages = self.llm_client.beta.threads.messages.list(thread_id=thread_id)

        return messages

    def get_files_in_assistant_thread_message(self, thread_id, message_id):
        """To be done."""
        return None

    def get_assistant_thread_message(self, thread_id, message_id):
        """To be done."""
        return None

    def get_file_in_assistant_thread_message(self, thread_id, message_id, file_id):
        """To be done."""
        return None

    def modify_assistant_thread_message(self, thread_id, message_id, metadata):
        """To be done."""
        return None

    def create_assistant_thread_run(self, thread_id, assistant_id):
        """Run Assistant."""
        assistant_data  = self.get_assistant(assistant_id)
        assistant_tools = self._tools_to_json(assistant_data.tools)

        run = self.llm_client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            #instructions=run_instructions, #Mind this would override Assistant instructions. use carefully. Need to change the method signature
            tools=assistant_tools
        )

        return run

    def create_assistant_thread_run_and_run_it(self, metadata):
        """To be done."""
        return None

    def get_assistant_thread_runs(self, thread_id):
        """To be done."""
        return None

    def get_assistant_thread_run_steps(self, thread_id, run_id):
        """To be done."""
        return None

    def get_assistant_thread_run(self, thread_id, run_id):
        """Create Thread run."""
        run = self.llm_client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )

        return run

    def get_assistant_thread_run_step(self, thread_id, run_id, step_id):
        """To be done."""
        return None

    def modify_assistant_thread_run(self, thread_id, run_id, metadata):
        """To be done."""
        return None

    def submit_tool_outputs_to_assistant_thread_run(self, thread_id, run_id, tool_output_list):
        """Submit tool output to thread run."""
        self.llm_client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_output_list
            )

    def cancel_assistant_thread_runs(self, thread_id, run_id):
        """To be done."""
        return None

    def get_assistant_thread_messages(self, thread_id):
        """Get assistant thread messages."""
        try:
            messages = self.llm_client.beta.threads.messages.list(thread_id=thread_id)
            if isinstance(messages, SyncCursorPage):
                return messages.data
            else:
                return messages
        except Exception:
            return []

# INSTRUCTIONS
    def update_assistant_instructions(self, assistant_id, updated_instructions):
        """Update instructions."""
        self.llm_client.beta.assistants.update(assistant_id, instructions=updated_instructions)

# DESCRIPTION
    def update_assistant_description(self, assistant_id, updated_description):
        """Update description."""
        self.llm_client.beta.assistants.update(assistant_id, description=updated_description)

# FUNCTIONS
    def _tools_to_json(self, assistant_tools):
        """Transform tools to JSON."""
        tool_list = []
        for assistant_tool in assistant_tools:
            if assistant_tool.type == "function":
                this_tool = {"type": "function", "function": assistant_tool.function.__dict__}
            elif assistant_tool.type == "code_interpreter":
                this_tool = {"type": "code_interpreter"}
            else:
                self.observability_helper.log(f"LLM HELPER - ERROR - NOT CONSIDERED TOOL TYPE {assistant_tool.type}", self.verbose)

            tool_list.append(this_tool)
        return tool_list

    def delete_assistant_function(self, assistant_id, function_name_to_delete):
        """Delete assistant function."""
        assistant_data  = self.get_assistant(assistant_id)
        assistant_tools = self._tools_to_json(assistant_data.tools)
        updated_tools = [tool for tool in assistant_tools if 'function' in tool and tool['function']['name'] != function_name_to_delete]
        self.observability_helper.log(f"LLM HELPER - Deleting function {function_name_to_delete} in assistant {assistant_id}", self.verbose)
        self.update_assistant_tools(assistant_id, updated_tools)

    def create_assistant_function(self, assistant_id, new_function_data):
        """Create assistant function."""
        assistant_data  = self.get_assistant(assistant_id)
        existing_assistant_tools = self._tools_to_json(assistant_data.tools)

        # Excluded existing fuction with same name
        existing_assistant_tools = [tool for tool in existing_assistant_tools if 'function' in tool and tool['function']['name'] != new_function_data['name']]

        new_tool = {"type": "function", "function": new_function_data}
        existing_assistant_tools.append(new_tool)

        self.observability_helper.log(f"LLM HELPER - Adding a tool {new_tool['function']} to assistant {assistant_id}", self.verbose)
        self.update_assistant_tools(assistant_id, existing_assistant_tools)

    def update_assistant_function(self, assistant_id, updated_function_json):
        """Update assistant function."""
        assistant_data  = self.get_assistant(assistant_id)
        assistant_tools = self._tools_to_json(assistant_data.tools)

        function_name_to_update = updated_function_json['name']
        existing_tools = [tool for tool in assistant_tools if 'function' in tool and tool['function']['name'] != function_name_to_update]

        updated_tool = {"type": "function", "function": updated_function_json}
        existing_tools.append(updated_tool)

        existing_tool_names = [tool['function']['name'] for tool in existing_tools]

        self.observability_helper.log(f"LLM HELPER - Adding a tool {updated_tool['function']} to assistant {assistant_id} with tools {existing_tool_names}", self.verbose)
        self.update_assistant_tools(assistant_id, existing_tools)

    def update_assistant_code_interpreter_tool(self, assistant_id, is_code_interpreter_enabled):
        """Update assistant code interpreter function."""
        assistant_data  = self.get_assistant(assistant_id)
        assistant_tools = [tool for tool in self._tools_to_json(assistant_data.tools) if tool['type'] != "code_interpreter"]

        if is_code_interpreter_enabled:
            assistant_tools.append({"type": "code_interpreter"})

        self.update_assistant_tools(assistant_id, assistant_tools)

    def update_assistant_tools(self, assistant_id, assistant_tools):
        """Update assistant tools."""
        self.llm_client.beta.assistants.update(assistant_id, tools=assistant_tools)

    def is_duplicated_function(self, assistant_id, new_function_body):
        """Check if an assistant is duplicated."""
        this_assistant = self.get_assistant(assistant_id)
        assistant_function_names = [tool_function.function.__dict__['name'] for tool_function in self.get_functions_from_assistant(this_assistant)]
        new_function_name = json.loads(new_function_body)['name']

        return new_function_name in assistant_function_names

# FILES
    def upload_file(self, file_byte_data):
        """Upload the file to OpenAI."""
        file_upload_response = self.llm_client.files.create(
            file=io.BytesIO(file_byte_data),
            purpose='assistants'
        )
        if file_upload_response.status == 'processed':
            return True, file_upload_response.id
        else:
            self.observability_helper.log(f"LLM HELPER - Uploading failed with status {file_upload_response.status}", self.verbose)
            return False, None

    def delete_all_files(self):
        """Delete all files."""
        print("Listing assistants")
        for assistant_data in self.llm_client.beta.assistants.list().data:
            if len(assistant_data.file_ids) == 0:
                print(f"Assistant {assistant_data.name} with id {assistant_data.id} has no files ")
            else:
                print(f"Assistant {assistant_data.name} with id {assistant_data.id} has files {assistant_data.file_ids} ")
                for file_id in assistant_data.file_ids:
                    self.llm_client.beta.assistants.files.delete(file_id, assistant_id=assistant_data.id, )
                    print(f"Deleting file {file_id} for Assistant {assistant_data.name} with id {assistant_data.id} ")

        file_list = self.llm_client.files.list()
        file_data = [file.id for file in file_list.data]
        for file_id in file_data:
            print(f"Deleting file  with id {file_id}")
            self.llm_client.files.delete(file_id)

    def get_completion(self, messages):
        """Get completion."""
        completion = self.llm_client.chat.completions.create(
            model=self.openai_deployment,
            messages=messages
        )

        completion_text = completion.choices[0].message.content

        return completion_text

    def check_openai_endpoint_from_settings(self):
        """Check OpenAI endpoint."""
        try:
            self.llm_client.chat.completions.create(
                model=self.openai_deployment,
                messages=[{"role": "assistant", "content": "ping"}]
            )
            return True
        except:
            return False


    def check_openai_endpoint(self, az_openai_service_endpoint, az_openai_service_key, az_openai_service_deployment, az_openai_api_version):
        """Check OpenAI endpoint."""
        llm_client = AzureOpenAI(
            azure_endpoint=az_openai_service_endpoint,
            api_key=az_openai_service_key,
            api_version=az_openai_api_version
        )

        llm_client.chat.completions.create(
            model=az_openai_service_deployment,
            messages=[{"role": "assistant", "content": "ping"}]
        )

    def get_file(self, file_id):
        """Get a file."""
        file = self.llm_client.files.retrieve(file_id)
        return file

# OBJECT OPERATIONS
    def get_functions_from_assistant(self, assistant_instance):
        """Get function from assistant."""
        tool_functions = [tool for tool in assistant_instance.tools if isinstance(tool, ToolFunction)]
        return tool_functions

    def assistant_has_code_interpreter(self, assistant_id):
        """Check if an assistant has code interpreter."""
        assistant_instance = self.get_assistant(assistant_id)
        tool_code_interpreter = [tool for tool in assistant_instance.tools if isinstance(tool, ToolCodeInterpreter)]
        return len(tool_code_interpreter) > 0

    def get_files_from_assistant(self, assistant_instance):
        """Get files from assistant."""
        assistant_files = [self.get_file(file_id) for file_id in assistant_instance.file_ids]
        return assistant_files

    def validate_function_json(self, function_text):
        """Validate the JSON of a function."""
        try:
            # Attempt to parse the string as JSON
            json.loads(function_text)
            return True  # Parsing succeeded, the string is valid JSON
        except json.JSONDecodeError:
            return False  # Parsing failed, the string is not valid JSON
