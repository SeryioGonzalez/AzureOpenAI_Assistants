import json
import os

class AssistantFactory:
    assistant_folder = "assistant_data/"

    def __init__(self):
        self.assistant_list = self._load_assistant_files_as_dicts()

    def _load_assistant_files_as_dicts(self):
        assistant_dict_list = []
        for file_name in os.listdir(self.assistant_folder):
            if file_name.endswith('.json'):
                # Construct the full file path
                assistant_file_path = os.path.join(self.assistant_folder, file_name)
                # Open and read the JSON file
                with open(assistant_file_path, 'r', encoding='utf-8') as assistant_file:
                    assistant_data = json.load(assistant_file)
                    assistant_dict_list.append(assistant_data)   

        return assistant_dict_list      

    def get_assistant_field(self, assistant_name, assistant_field):
        this_assistant = [assistant for assistant in self.assistant_list if assistant['assistant_name'] == assistant_name][0]
    
        return this_assistant[assistant_field]

    #Reads assistant files and creates a list with all assistant names
    def get_assistant_name_list(self):
        assistant_dict_list = self.assistant_list
        assistant_name_list = [ assistant_data['assistant_name'] for assistant_data in assistant_dict_list]

        return assistant_name_list

    def is_there_assistants(self):
        if len(self.assistant_list) > 0:
            return True
        else:
            return False

class Assistant:
    def __init__(self, name, description, instructions, conversation_starters, capabilities):
        self.name = name
        self.description = description
        self.instructions = instructions
        self.conversation_starters = conversation_starters
        self.capabilities = capabilities




