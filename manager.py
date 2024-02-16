"""Manages Assistant flows"""
import time

from utilities.env_helper           import EnvHelper
from utilities.llm_helper           import LLMHelper
from utilities.observability_helper import ObservabilityHelper

class Manager:
    """App manager class"""

    def __init__(self):
        self.llm_helper = LLMHelper()
        self.env_helper= EnvHelper()
        self.observability_helper = ObservabilityHelper()
        self.observability_helper.log_message("New Manager created")
        self.uploaded_files = {}

    def are_there_assistants(self):
        """Checks if are the assistants"""
        return len(self.get_assistant_list()) > 0

    def get_assistant_list(self):
        """Get Assistant list"""
        assistant_list = self.llm_helper.get_assistants()
        return assistant_list

    def get_assistant_id_name_list(self):
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

    def run_thread(self, prompt, assistant_name):
        """Runs a thread with the assistant"""
        thread = self.llm_helper.create_assistant_thread()
        assistant_id = self.get_assistant_field(assistant_name, "id")
        assistant_file_ids = self.uploaded_files.get(assistant_id, [])
        self.llm_helper.add_message_to_assistant_thread(thread, "user", prompt, assistant_file_ids)

        run = self.llm_helper.create_assistant_thread_run_and_run_it(thread.id, assistant_id, "Be good")

        while run.status != "completed":
            time.sleep(1)
            run = self.llm_helper.get_assistant_thread_run(thread.id, run.id)

        messages = self.llm_helper.get_assistant_thread_messages(thread.id)

        return messages.data[0].content[0].text.value

    def upload_file(self, uploaded_file, verbose=False):
        """Uploads a file"""
        bytes_data = uploaded_file.getvalue()
        self.observability_helper.log_message(f"Uploading file {uploaded_file.name}", verbose)
        upload_success, file_id = self.llm_helper.upload_file(bytes_data)

        if upload_success:
            self.observability_helper.log_message(f"Uploading success. File id {file_id}", verbose)
        else:
            self.observability_helper.log_message(f"Uploading of file id {file_id} failed", verbose)


        return upload_success, file_id

    def track_assistant_file(self, assistant_id, file_id, verbose=True):
        """Adds assistant to file"""
        if assistant_id not in self.uploaded_files:
            self.uploaded_files[assistant_id] = []

        self.uploaded_files[assistant_id].append(file_id)
        self.observability_helper.log_message(f"File {file_id} to assist id {assistant_id} OK", verbose)

    def upload_file_to_assistant(self, assistant_name, uploaded_file, verbose=True):
        """Pushes file to assistants"""
        upload_success, file_id = self.upload_file(uploaded_file)

        upload_to_assistant = False

        if upload_success:
            self.observability_helper.log_message(f"Upload to AOAI OK. File id {file_id}", verbose)
            assistant_id = self.get_assistant_field(assistant_name, "id")
            if self.llm_helper.create_assistant_file(assistant_id, file_id):
                self.track_assistant_file(assistant_id, file_id)
                self.observability_helper.log_message(f"Uploading file {file_id} to assistant id {assistant_id} OK", verbose)
                upload_to_assistant = True
            else:
                self.observability_helper.log_message(f"Uploading file {file_id} to assistant id {assistant_id} KO", verbose)
        else:
            self.observability_helper.log_message(f"Uploading file {file_id} failed", verbose)


        return upload_success & upload_to_assistant
