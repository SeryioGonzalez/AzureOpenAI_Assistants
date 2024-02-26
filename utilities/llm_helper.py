"""Module managing LLM interaction"""
from openai import AzureOpenAI
from openai.types.beta.assistant import ToolFunction        as ToolFunction
from openai.types.beta.assistant import ToolCodeInterpreter as ToolCodeInterpreter

if __name__ == '__main__':
    from env_helper   import EnvHelper
    from observability_helper import ObservabilityHelper
else:
    from utilities.env_helper   import EnvHelper
    from utilities.observability_helper import ObservabilityHelper

import json
import io
import openai

class LLMHelper:
    """Class managing LLM interaction"""
    def __init__(self):
        self.env_helper: EnvHelper = EnvHelper()
        self.observability_helper = ObservabilityHelper()
        self.llm_client = AzureOpenAI(
            azure_endpoint = self.env_helper.OPENAI_API_BASE,
            api_key        = self.env_helper.OPENAI_API_KEY,
            api_version    = self.env_helper.AZURE_OPENAI_API_VERSION
        )
        self.openai_deployment = self.env_helper.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME
        self.verbose = True

    def is_duplicated_assistant(self, new_assistant_name):
        existing_assistant_names = [assistant.name for assistant in self.get_assistants()]
        
        return new_assistant_name in existing_assistant_names

    def create_assistant(self, new_assistant_name, new_assistant_instructions):
        self._create_assistant(new_assistant_name, new_assistant_instructions, [])

    def _create_assistant(self, assistant_name : str, instructions : str, tools : list):
        assistant = self.llm_client.beta.assistants.create(
            name=assistant_name,
            instructions=instructions,
            tools=tools,
            model=self.openai_deployment
        )

        return assistant

    def create_assistant_file(self, assistant_id, file_id):
        # Upload the file to OpenAI
        file_upload_to_assistant_response = self.llm_client.beta.assistants.files.create(
            assistant_id, file_id=file_id
        )

        if  file_upload_to_assistant_response.id is not None:
            return True
        else: 
            self.observability_helper.log(f"Uploading file to assistant failed", self.verbose)
            return False

    def get_assistants(self):
        """List Assistants"""
        assistant_list = self.llm_client.beta.assistants.list().data

        return assistant_list

    def get_assistant_files(self, assistant_id):
        assistant_list = self.llm_client.beta.assistants.files(assistant_id)

        return assistant_list

    def get_assistant(self, assistant_id):
        assistant = self.llm_client.beta.assistants.retrieve(assistant_id)
        return assistant

    #TODO
    def get_assistant_file(self, assistant_id, file_id):
        return None

    #TODO
    def modify_assistant(self, assistant_id, assistant):
        return None
    
    def delete_assistant(self, assistant_id):
        try:
            self.observability_helper.log(f"Deleting assistant {assistant_id}", self.verbose)
            self.llm_client.beta.assistants.delete(assistant_id)
        except openai.NotFoundError:
            self.observability_helper.log(f"Assistant {assistant_id} does not exist", self.verbose)

    #TODO
    def delete_assistant_file(self, assistant_id, file_id):
        return None
    
    def create_assistant_thread(self):
        """Create Assistant Thread"""
        thread = self.llm_client.beta.threads.create()

        return thread

    #TODO
    def get_assistant_thread(self, thread_id):
        return None

    #TODO
    def modify_assistant_thread(self, thread_id):
        return None

    #TODO
    def delete_assistant_thread(self, thread_id):
        return None

    def add_message_to_assistant_thread(self, thread, message_role, message_content, file_ids):
        """Add message to Assistant thread"""

        self.observability_helper.log(f"Creating message with content {message_content} and role {message_role} to thread {thread.id} with file ids:  {file_ids}", self.verbose)

        self.llm_client.beta.threads.messages.create(
            thread_id=thread.id,
            role=message_role,
            content=message_content,
            file_ids=file_ids
        )

    def get_messages_in_assistant_thread(self, thread_id):
        """List messages in thread"""
        messages = self.llm_client.beta.threads.messages.list(thread_id=thread_id)

        return messages

    #TODO
    def get_files_in_assistant_thread_message(self, thread_id, message_id):
        return None
    
    #TODO
    def get_assistant_thread_message(self, thread_id, message_id):
        return None


        #TODO
   
    #TODO
    def get_file_in_assistant_thread_message(self, thread_id, message_id, file_id):
        return None

    #TODO
    def modify_assistant_thread_message(self, thread_id, message_id, metadata):
        return None

    def create_assistant_thread_run(self, thread, assistant_id, run_instructions):
        """Run Assistant"""
        assistant_data  = self.get_assistant(assistant_id)
        assistant_tools = self._tools_to_json(assistant_data.tools)
        
        run = self.llm_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions=run_instructions,
            tools=assistant_tools
        )

        return run

    #TODO
    def create_assistant_thread_run_and_run_it(self, metadata):
        return None

    #TODO
    def get_assistant_thread_runs(self, thread_id):
        return None

    #TODO
    def get_assistant_thread_run_steps(self, thread_id, run_id):
        return None

    def get_assistant_thread_run(self, thread_id, run_id):
        run = self.llm_client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )

        return run
    
    #TODO
    def get_assistant_thread_run_step(self, thread_id, run_id, step_id):
        return None

    #TODO
    def modify_assistant_thread_run(self, thread_id, run_id, metadata):
        return None

    def submit_tool_outputs_to_assistant_thread_run(self, thread_id, run_id, tool_output_list):
        run = self.llm_client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_output_list
            )

    #TODO
    def cancel_assistant_thread_runs(self, thread_id, run_id):
        return None

    def get_assistant_thread_messages(self, thread_id):
        messages = self.llm_client.beta.threads.messages.list(thread_id=thread_id)

        return messages

#INSTRUCTIONS
    def update_assistant_instructions(self, assistant_id, updated_instructions):
        self.llm_client.beta.assistants.update(assistant_id, 
            instructions        = updated_instructions
        )

#FUNCTIONS
    def _tools_to_json(self, assistant_tools):
        tool_list = []
        for assistant_tool in assistant_tools:
            if assistant_tool.type == "function":
                this_tool = {"type": "function", "function": assistant_tool.function.__dict__}
            elif assistant_tool.type == "code_interpreter":
                this_tool = {"type": "code_interpreter"}
            else:
               self.observability_helper.log(f"ERROR - NOT CONSIDERED TOOL TYPE {assistant_tool.type}", self.verbose) 
            
            tool_list.append(this_tool)
        return tool_list

    def delete_assistant_function(self, assistant_id, function_name_to_delete):
        assistant_data  = self.get_assistant(assistant_id)
        assistant_tools = self._tools_to_json(assistant_data.tools)
        updated_tools = [tool for tool in assistant_tools if 'function' in tool and tool['function']['name'] != function_name_to_delete]
        self.observability_helper.log(f"Deleting function {function_name_to_delete} in assistant {assistant_id}", self.verbose)
        self.update_assistant_tools(assistant_id, updated_tools)

    def create_assistant_function(self, assistant_id, new_function_data):
        assistant_data  = self.get_assistant(assistant_id)
        existing_assistant_tools = self._tools_to_json(assistant_data.tools)

        #Excluded existing fuction with same name
        existing_assistant_tools = [tool for tool in existing_assistant_tools if 'function' in tool and tool['function']['name'] != new_function_data['name'] ]
        
        new_tool = {"type": "function", "function": new_function_data}
        existing_assistant_tools.append(new_tool)
        
        self.observability_helper.log(f"Adding a tool {new_tool['function']} to assistant {assistant_id}", self.verbose)
        self.update_assistant_tools(assistant_id, existing_assistant_tools)

    def update_assistant_function(self, assistant_id, updated_function_json):
        assistant_data  = self.get_assistant(assistant_id)
        assistant_tools = self._tools_to_json(assistant_data.tools)
        
        function_name_to_update = updated_function_json['name']
        existing_tools = [tool for tool in assistant_tools if 'function' in tool and tool['function']['name'] != function_name_to_update]

        updated_tool = {"type": "function", "function": updated_function_json}
        existing_tools.append(updated_tool)
        
        existing_tool_names = [tool['function']['name'] for tool in existing_tools]

        self.observability_helper.log(f"Adding a tool {updated_tool['function']} to assistant {assistant_id} with tools {existing_tool_names}", self.verbose)
        self.update_assistant_tools(assistant_id, existing_tools)
        
    def update_assistant_code_interpreter_tool(self, assistant_id, is_code_interpreter_enabled):
        assistant_data  = self.get_assistant(assistant_id)
        assistant_tools = [tool for tool in self._tools_to_json(assistant_data.tools) if tool['type'] != "code_interpreter"]

        if is_code_interpreter_enabled:
            assistant_tools.append({"type": "code_interpreter"})

        self.update_assistant_tools(assistant_id, assistant_tools)

    def update_assistant_tools(self, assistant_id, assistant_tools):
        self.llm_client.beta.assistants.update(assistant_id, 
            tools        = assistant_tools
        )

    def is_duplicated_function(self, assistant_id, new_function_body):
        
        this_assistant = self.get_assistant(assistant_id)
        assistant_function_names = [tool_function.function.__dict__['name'] for tool_function in self.get_functions_from_assistant(this_assistant)]
        new_function_name = json.loads(new_function_body)['name']

        if new_function_name in assistant_function_names:
            return True
        else:
            return False

#FILES 
    def upload_file(self, file_byte_data):
        # Upload the file to OpenAI
        file_upload_response = self.llm_client.files.create(
            file=io.BytesIO(file_byte_data),
            purpose='assistants'
        )
        if  file_upload_response.status == 'processed':
            return True, file_upload_response.id
        else: 
            self.observability_helper.log(f"Uploading failed with status {file_upload_response.status}", self.verbose)
            return False, None

    def delete_all_files(self):
        # Upload the file to OpenAI
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
        file_data = [file.id for file in file_list.data ]
        for file_id in file_data:
            print(f"Deleting file  with id {file_id}")
            self.llm_client.files.delete(file_id)

    def get_completion(self, messages):
        completion = self.llm_client.chat.completions.create(
            model=self.openai_deployment,
            messages=messages
        )

        completion_text = completion.choices[0].message.content

        return 
    
    def check_openai_endpoint(self, az_openai_service_endpoint, az_openai_service_key, az_openai_service_deployment):
        llm_client = AzureOpenAI(
            azure_endpoint = az_openai_service_endpoint,
            api_key        = az_openai_service_key,
            api_version    = self.env_helper.AZURE_OPENAI_API_VERSION
        )

        completion = llm_client.chat.completions.create(
            model=az_openai_service_deployment,
            messages= [{"role": "assistant", "content": "ping"}]
        )

    def get_file(self, file_id):
        file = self.llm_client.files.retrieve(file_id)
        return file

################# OBJECT OPERATIONS
    def get_functions_from_assistant(self, assistant_instance):
        tool_functions = [tool for tool in assistant_instance.tools if isinstance(tool, ToolFunction)]
        return tool_functions

    def assistant_has_code_interpreter(self, assistant_instance):
        tool_code_interpreter = [tool for tool in assistant_instance.tools if isinstance(tool, ToolCodeInterpreter)]
        return len(tool_code_interpreter) > 0
    
    def get_files_from_assistant(self, assistant_instance):
        assistant_files = [self.get_file(file_id) for file_id in assistant_instance.file_ids ]
        return assistant_files

    def validate_function_json(self, function_text):
        try:
            # Attempt to parse the string as JSON
            json.loads(function_text)
            return True  # Parsing succeeded, the string is valid JSON
        except json.JSONDecodeError:
            return False  # Parsing failed, the string is not valid JSON

if __name__ == '__main__':
    llm_helper = LLMHelper()
    llm_helper.delete_all_files()
    