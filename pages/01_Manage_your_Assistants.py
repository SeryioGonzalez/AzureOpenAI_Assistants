import utilities.page_content as content
from utilities.observability_helper import ObservabilityHelper
from manager import Manager

import datetime
import json
import pandas as pd
import streamlit as st


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


if 'initialized' not in st.session_state:
    manager = Manager()
    st.session_state['manager'] = manager
    st.session_state['initialized'] = True

st.session_state['manager'].observability_helper.log_message("Configuring assistants", verbose=verbose)

st.title(content.MANAGE_TITLE_TEXT )

if st.session_state['manager'].are_there_assistants():
    #All Assitants
    assistant_id_name_list = st.session_state['manager'].get_assistant_id_name_list()
    assistant_id_list   = [ assistant[0] for assistant in assistant_id_name_list]
    assistant_name_list = [ assistant[1] for assistant in assistant_id_name_list]
    
    #Selected Assitant
    selected_assistant_name  = st.selectbox(content.MANAGE_ASSISTANT_SELECT_TEXT, assistant_name_list)
    selected_assistant_index = assistant_name_list.index(selected_assistant_name)
    selected_assistant_id = assistant_id_list[selected_assistant_index]
    selected_assistant = st.session_state['manager'].get_assistant(selected_assistant_id)
    
    selected_assistant_files = st.session_state['manager'].llm_helper.get_files_from_assistant(selected_assistant)

    #Selected Assistant info
    assistant_description  = selected_assistant.description
    assistant_instructions = selected_assistant.instructions
    #assistant_conversation_starters = selected_assistant.metadata

#ASSISTANT DISPLAY
    st.write(content.MANAGE_SELECTED_ASSISTANT_ID + f": {selected_assistant_id}")
#Assistant Instructions
    st.text_area(content.MANAGE_SELECTED_ASSISTANT_INSTRUCTIONS, assistant_instructions)
#Assistant Tools
    st.markdown(f"<div style='text-align: center;'>{content.MANAGE_SELECTED_ASSISTANT_TOOLS}</div>", unsafe_allow_html=True)
#Assistant Functions
    #Adding a function
    
    with st.form("add_function_form"):
        with st.expander("Add Function"):
            new_function_body   = st.text_area("New function", key="manage_text_new_function" , height=400)
            new_function_submit = st.form_submit_button("Save function")
    #New function submitted
    if (new_function_submit):
        if st.session_state['manager'].llm_helper.validate_function_json(new_function_body):
            st.session_state['manager'].llm_helper.update_assistant_functions(selected_assistant_id, new_function_body)
            st.session_state['manager'].observability_helper.log_message(f"New function added - refreshing", verbose=verbose)
            st.rerun()
        else:
            st.error(content.MANAGE_ASSISTANT_NEW_FUNCTION_NOT_VALID )
            st.session_state['manager'].observability_helper.log_message(f"Not a valid function", verbose=verbose)

    st.session_state['manager'].observability_helper.log_message(f"Listing functions", verbose=verbose)
    #Listing function
    selected_assistant_functions = st.session_state['manager'].llm_helper.get_functions_from_assistant(selected_assistant)
    functions_data_list = get_assistant_data(selected_assistant_functions)
    selected_assistant_has_code_interpreter = st.session_state['manager'].llm_helper.assistant_has_code_interpreter(selected_assistant)
    
    st.write(content.MANAGE_SELECTED_ASSISTANT_FUNCTIONS)
    for function_data in functions_data_list:
        with st.expander(function_data['name']):
            st.text_area("Function definition", key="function_definition_" + function_data['name'] , value=function_data['definition'], height=400)
            st.button("Delete", key="delete_" + function_data['name'])

    st.write(content.MANAGE_SELECTED_ASSISTANT_CAPABILITIES)
    st.toggle(content.MANAGE_SELECTED_ASSISTANT_CAPABILITIES_CODE_INTERPRETER, value=selected_assistant_has_code_interpreter)
#Assistant files
    st.markdown(f"<div style='text-align: center;'>{content.MANAGE_SELECTED_ASSISTANT_FILES}</div>", unsafe_allow_html=True)
    
    if len(selected_assistant_files) > 0:
        file_data_list = get_file_data(selected_assistant_files)
        st.write(file_data_list)
    else:
        st.write(content.MANAGE_NO_FILE_MESSAGE)

else:
    st.write(content.MAIN_NO_ASSISTANT_TEXT)


