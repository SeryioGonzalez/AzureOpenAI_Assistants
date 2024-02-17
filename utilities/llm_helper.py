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

import io

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


    def create_assistant(self, assistant_name : str, instructions : str, tools : list):
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
            self.observability_helper.log_message(f"Uploading file to assistant failed", self.verbose)
            return False

    def get_assistants(self):
        """List Assistants"""
        assistant_file_list = self.llm_client.beta.assistants.list().data

        return assistant_file_list

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
    def modify_assistant(self, assistant_id, assistant_data_model):
        return None

    #TODO
    def delete_assistant(self, assistant_id):
        return None

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

        self.observability_helper.log_message(f"Creating message with content {message_content} and role {message_role} to thread {thread.id} with file ids:  {file_ids}", self.verbose)


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
        run = self.llm_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions=run_instructions,
            tools=[{"type": "code_interpreter"}]
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

    #TODO
    def submit_tool_outputs_to_assistant_thread_run(self, thread_id, run_id, metadata):
        return None

    #TODO
    def cancel_assistant_thread_runs(self, thread_id, run_id):
        return None

    def get_assistant_thread_messages(self, thread_id):
        messages = self.llm_client.beta.threads.messages.list(thread_id=thread_id)

        return messages

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
            self.observability_helper.log_message(f"Uploading failed with status {file_upload_response.status}", self.verbose)
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


if __name__ == '__main__':
    llm_helper = LLMHelper()
    #llm_helper.delete_all_files()
    assistant = llm_helper.get_assistants()[0]
    #assistant = Assistant()

    print(assistant)
    