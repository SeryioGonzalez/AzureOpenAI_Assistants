from dotenv import load_dotenv
from openai import AzureOpenAI
from pathlib import Path
import os

load_dotenv()    

assistant_name = "file_eater_assistant"
assistant_instructions = "Respond based on the files provided"
assistant_description = assistant_instructions

assistant_tool_list = [
    {"type": "code_interpreter"},
]

DATA_FOLDER = "assistant_data/"

llm_client = AzureOpenAI(
  azure_endpoint=f"https://{os.getenv('AZURE_OPENAI_RESOURCE_NAME')}.openai.azure.com/",
  api_key=os.getenv("AZURE_OPENAI_KEY"),
  api_version="2024-02-15-preview"
)

print ("Deleting Assistants")
try:
  for assistant in llm_client.beta.assistants.list():
      print (f"Deleting Assistant {assistant.id}")
      llm_client.beta.assistants.delete(assistant.id)
except:
    pass

print ("Deleting Files")
for assistant_file in llm_client.files.list():
    print (f"Deleting File {assistant_file.id}")
    llm_client.files.delete(assistant_file.id)

created_assistant = llm_client.beta.assistants.create(
    name=assistant_name,
    description=assistant_description,
    instructions=assistant_instructions,
    tools=assistant_tool_list,
    model=os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT_NAME")
)

def upload_file(client: AzureOpenAI, path: str) :
    with Path(path).open("rb") as f:
        return client.files.create(file=f, purpose="assistants")

arr = os.listdir(DATA_FOLDER)
for file in arr:
    file_path = DATA_FOLDER + file
    print(f"Adding file {file_path} to assistant {created_assistant.id}")
    uploaded_file = upload_file(llm_client, file_path)
    llm_client.beta.assistants.files.create(created_assistant.id, file_id=uploaded_file.id)

print(f"Created Assistant with id {created_assistant.id} and name {created_assistant.name}")
for assistant_file in llm_client.beta.assistants.files.list(created_assistant.id):
    print(f"Assistant id {created_assistant.id} has file {assistant_file.id}")