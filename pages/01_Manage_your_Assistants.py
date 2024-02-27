"""Page for managing Assistants in a page"""
import datetime
import json
import pandas as pd
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

import utilities.page_content as content
from utilities.observability_helper import ObservabilityHelper
from utilities.openapi_helper import OpenAPIHelper
from manager import Manager

verbose = True

def get_assistant_data(function_list):
    def get_function_definition_dict(function_definition):
        function_defitinion_dict = {}
        function_defitinion_dict['name'] = function_definition.name
        function_defitinion_dict['description'] = function_definition.description
        function_defitinion_dict['parameters'] = function_definition.parameters

        function_defitinion_json = json.dumps(function_defitinion_dict, indent=4)

        return function_defitinion_json
    
    filtered_function_data = [{'name': function.function.name, 'definition': get_function_definition_dict(function.function) } for function in function_list]

    return filtered_function_data

def get_file_data(file_list):
    filtered_file_data = [{'name': file.filename, 'size': f"{round(file.bytes/1024,1)} MB", 'created': datetime.datetime.utcfromtimestamp(file.created_at).strftime('%Y-%m-%d %H:%M:%S') } for file in file_list]

    return pd.DataFrame(filtered_file_data)

def update_function(function_data):
    assistant_id, function_name = function_data
    key = "function_definition_" + function_name
    new_spec_data = st.session_state[key]
    
    try:
        new_spec_json = json.loads(new_spec_data)
        st.session_state['logger'].log(f"Updating function {new_spec_json['name']}", verbose=verbose)
        st.session_state['manager'].llm_helper.update_assistant_function(assistant_id, new_spec_json)
    except json.JSONDecodeError:
            st.session_state['logger'].log(f"Not a valid function JSON", verbose=verbose)

def delete_function(function_data):
    assistant_id, function_name = function_data
    st.session_state['manager'].llm_helper.delete_assistant_function(assistant_id, function_name)

def update_instructions(assistant_data):
    assistant_id, previous_instructions = assistant_data
    if previous_instructions != st.session_state['updated_instructions']:
        st.session_state['logger'].log(f"For assistant {assistant_id} update instructions {st.session_state['updated_instructions']} from {previous_instructions}", verbose=verbose)
        st.session_state['manager'].llm_helper.update_assistant_instructions(assistant_id, st.session_state['updated_instructions'])
    else:
        st.session_state['logger'].log(f"No updated instructions for assistant {assistant_id}", verbose=verbose)

def update_code_interpreter(assistant_id):
    st.session_state['logger'].log(f"For {assistant_id} code interpreter is {st.session_state['code_interpreter']}", verbose=verbose)
    st.session_state['manager'].llm_helper.update_assistant_code_interpreter_tool(assistant_id, st.session_state['code_interpreter'])

def delete_assistant(assistant_id):
    st.session_state['logger'].log(f"Deleting {assistant_id} ", verbose=verbose)
    st.session_state['manager'].llm_helper.delete_assistant(assistant_id)   

if 'session_id' not in st.session_state:
    ctx = get_script_run_ctx()
    st.session_state['session_id'] = ctx.session_id
    st.session_state['manager'] = Manager(st.session_state['session_id'])

    st.session_state['logger'] = ObservabilityHelper()

st.session_state['logger'].log("Configuring assistants", verbose=verbose)

#DISPLAY - TITLE
st.title(content.MANAGE_TITLE_TEXT )

#DISPLAY - ASSISTANT PANEL
if st.session_state['manager'].are_there_assistants():
    #All Assitants
    assistant_id_name_list = st.session_state['manager'].get_assistant_id_name_tuple_list()
    assistant_id_list   = [ assistant[0] for assistant in assistant_id_name_list]
    assistant_name_list = [ assistant[1] for assistant in assistant_id_name_list]
    
#DISPLAY - CREATE ASSISTANT FORM
    with st.form("add_assistant_form"):
        with st.expander(content.MANAGE_CREATE_ASSISTANT):
            new_assistant_name         = st.text_input(content.MANAGE_CREATE_ASSISTANT_NAME, key="new_assistant_name")
            new_assistant_instructions = st.text_area(content.MANAGE_CREATE_ASSISTANT_INSTRUCTIONS, key="new_assistant_instructions")
            new_assistant_submit       = st.form_submit_button(content.MANAGE_CREATE_ASSISTANT_SUBMIT)

        #New function submitted
    if (new_assistant_submit):
        if new_assistant_name != "" and new_assistant_instructions != "":
            if st.session_state['manager'].llm_helper.is_duplicated_assistant(new_assistant_name) is False:
                st.session_state['manager'].llm_helper.create_assistant(new_assistant_name, new_assistant_instructions)
                st.session_state['logger'].log(f"New assistant {new_assistant_name} created - refreshing", verbose=verbose)
                st.rerun()
            else:
               st.session_state['logger'].log(f"Duplicated assistant {new_assistant_name}", verbose=verbose) 
               st.error(content.MANAGE_CREATE_ASSISTANT_DUPLICATED)
            
        else:
            st.session_state['logger'].log(f"Name {new_assistant_name} or instructions {new_assistant_instructions} not specified", verbose=verbose) 
            st.error(content.MANAGE_CREATE_ASSISTANT_NO_NAME_OR_INSTRUCTIONS)

#Selected Assistant
    selected_assistant_name  = st.selectbox(content.MANAGE_ASSISTANT_SELECT_TEXT, assistant_name_list)
    selected_assistant_index = assistant_name_list.index(selected_assistant_name)
    selected_assistant_id = assistant_id_list[selected_assistant_index]
    selected_assistant = st.session_state['manager'].get_assistant(selected_assistant_id)
    
    selected_assistant_files = st.session_state['manager'].llm_helper.get_files_from_assistant(selected_assistant)

    #Selected Assistant info
    assistant_description  = selected_assistant.description
    assistant_instructions = selected_assistant.instructions
    #assistant_conversation_starters = selected_assistant.metadata

#DISPLAY - ASSISTANT DISPLAY
    st.write(content.MANAGE_SELECTED_ASSISTANT_ID + f": {selected_assistant_id}")
    st.button(content.MANAGE_DELETE_ASSISTANT, on_click=delete_assistant, args=(selected_assistant_id,))
#DISPLAY - ASSISTANT Instructions
    st.text_area(content.MANAGE_SELECTED_ASSISTANT_INSTRUCTIONS, assistant_instructions, key="updated_instructions")
    st.button(content.MANAGE_UPDATE_ASSISTANT_INSTRUCTIONS, on_click=update_instructions, args=((selected_assistant_id,assistant_instructions),))
#DISPLAY - ASSISTANT TOOLS TITLE
    st.markdown(f"<div style='text-align: center;'>{content.MANAGE_SELECTED_ASSISTANT_TOOLS}</div>", unsafe_allow_html=True)
#DISPLAY - ASSISTANT Functions
    #Adding a function
    with st.form("add_action_form"):
        with st.expander(content.MANAGE_ASSISTANT_ACTION_ADD_EXPANDER):
            new_spec_body   = st.text_area(content.MANAGE_ASSISTANT_ACTION_ADD_BODY, key="manage_text_new_spec" , height=400)
            new_spec_submit = st.form_submit_button(content.MANAGE_ASSISTANT_ACTION_ADD_BUTTON)
    #New function submitted
    if (new_spec_submit):
        if OpenAPIHelper.validate_spec_json(new_spec_body):
            openai_functions = OpenAPIHelper.extract_openai_functions_from_spec(new_spec_body)
            for openai_function in openai_functions:
                st.session_state['manager'].llm_helper.create_assistant_function(selected_assistant_id, openai_function)
                st.session_state['logger'].log(f"New function added - refreshing", verbose=verbose)
            st.rerun()

        else:
            st.error(content.MANAGE_ASSISTANT_new_spec_NOT_VALID )
            st.session_state['logger'].log(f"Not a valid function", verbose=verbose)

    st.session_state['logger'].log(f"Listing functions", verbose=verbose)
    #Listing function
    selected_assistant_functions = st.session_state['manager'].llm_helper.get_functions_from_assistant(selected_assistant)
    functions_data_list = get_assistant_data(selected_assistant_functions)
    selected_assistant_has_code_interpreter = st.session_state['manager'].llm_helper.assistant_has_code_interpreter(selected_assistant)
    
    st.write(content.MANAGE_SELECTED_ASSISTANT_FUNCTIONS)
    for function_data in functions_data_list:
        with st.expander(function_data['name']):
            function_body = st.text_area(content.MANAGE_ASSISTANT_ACTION_BODY, key="function_definition_" + function_data['name'] , value=function_data['definition'], height=400)
            #Keys
            st.button(content.MANAGE_ASSISTANT_ACTION_UPDATE_BUTTON, key="update_" + function_data['name'], on_click=update_function, args=(((selected_assistant_id, function_data['name']),) ))
            st.button(content.MANAGE_ASSISTANT_ACTION_DELETE_BUTTON, key="delete_" + function_data['name'], on_click=delete_function, args=(((selected_assistant_id, function_data['name']),) ))

#DISPLAY - ASSISTANT OTHER TOOLS
    st.write(content.MANAGE_SELECTED_ASSISTANT_CAPABILITIES)
    st.toggle(content.MANAGE_SELECTED_ASSISTANT_CAPABILITIES_CODE_INTERPRETER, on_change=update_code_interpreter, key="code_interpreter", args=(selected_assistant_id,),  value=selected_assistant_has_code_interpreter)
#DISPLAY - ASSISTANT files
    st.markdown(f"<div style='text-align: center;'>{content.MANAGE_SELECTED_ASSISTANT_FILES}</div>", unsafe_allow_html=True)
    
    if len(selected_assistant_files) > 0:
        file_data_list = get_file_data(selected_assistant_files)
        st.write(file_data_list)
    else:
        st.write(content.MANAGE_NO_FILE_MESSAGE)

else:
    st.write(content.MAIN_NO_ASSISTANT_TEXT)


