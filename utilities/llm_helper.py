"""Module managing LLM interaction"""
from openai import AzureOpenAI

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
        env_helper: EnvHelper = EnvHelper()
        self.observability_helper = ObservabilityHelper()
        self.llm_client = AzureOpenAI(
            azure_endpoint = env_helper.OPENAI_API_BASE,
            api_key        = env_helper.OPENAI_API_KEY,
            api_version    = env_helper.AZURE_OPENAI_API_VERSION
        )
        self.openai_deployment = env_helper.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME
        self.verbose = True

    def get_completion(self, messages):
        """Get completion"""
        completion = self.llm_client.chat.completions.create(
            model=self.openai_deployment,
            messages=messages
        )

        completion_text = completion.choices[0].message.content

        return completion_text

    def create_assistant(self, assistant_name : str, instructions : str, tools : list):
        """Create Assistant"""
        assistant = self.llm_client.beta.assistants.create(
            name=assistant_name,
            instructions=instructions,
            tools=tools,
            model=self.openai_deployment
        )

        return assistant
    
    def get_assistants(self):
        """List Assistants"""
        assistant_list = self.llm_client.beta.assistants.list().data

        return assistant_list

    def create_assistant_thread(self):
        """Create Assistant Thread"""
        thread = self.llm_client.beta.threads.create()

        return thread


    def add_message_to_assistant_thread(self, thread, message_role, message_content, file_ids):
        """Add message to Assistant thread"""

        self.observability_helper.log_message(f"Creating message to thread with file ids:  {file_ids}", self.verbose)

        self.llm_client.beta.threads.messages.create(
            thread_id=thread.id,
            role=message_role,
            content=message_content,
            file_ids=file_ids

            )

    def run_assistant(self, thread, assistant_id, run_instructions):
        """Run Assistant"""
        run = self.llm_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions=run_instructions,
            tools=[{"type": "code_interpreter"}]
        )

        return run

    def list_messages_in_assistant_thread(self, thread):
        """List messages in thread"""
        messages = self.llm_client.beta.threads.messages.list(thread_id=thread.id)

        return messages
    
    def retrieve_run(self, thread, run):
        run = self.llm_client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        return run
    
    def get_thread_messages(self, thread):
        messages = self.llm_client.beta.threads.messages.list(thread_id=thread.id)

        return messages
    
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


    def upload_file_to_assistant(self, assistant_id, file_id):
        # Upload the file to OpenAI
        file_upload_to_assistant_response = self.llm_client.beta.assistants.files.create(
            assistant_id, file_id=file_id
        )

        if  file_upload_to_assistant_response.id is not None:
            return True
        else: 
            self.observability_helper.log_message(f"Uploading file to assistant failed", self.verbose)
            return False

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

if __name__ == '__main__':
    llm_helper = LLMHelper()
    llm_helper.delete_all_files()