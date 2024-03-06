"""Page for managing Assistants in a page."""
from streamlit.runtime.scriptrunner import get_script_run_ctx
import datetime
import json
import pandas as pd
import streamlit as st

import utilities.page_content as content
from utilities.observability_helper import ObservabilityHelper
from utilities.openapi_helper import OpenAPIHelper
from utilities.llm_helper import LLMHelper

VERBOSE = True

def get_assistant_function_data(function_list):
    """Get function definition."""
    def get_function_definition_dict(function_definition):
        function_defitinion_dict = {}
        function_defitinion_dict['name'] = function_definition.name
        function_defitinion_dict['description'] = function_definition.description
        function_defitinion_dict['parameters'] = function_definition.parameters

        function_defitinion_json = json.dumps(function_defitinion_dict, indent=4)

        return function_defitinion_json

    filtered_function_data = [{
                                'name': function.function.name,
                                'definition': get_function_definition_dict(function.function)
                            } for function in function_list]

    return filtered_function_data


def get_file_data(file_list):
    """Get file data."""
    filtered_file_data = [{
                            'name': file.filename,
                            'size': f"{round(file.bytes/1024,1)} MB",
                            'created': datetime.datetime.utcfromtimestamp(file.created_at).strftime('%Y-%m-%d %H:%M:%S')
                        } for file in file_list]

    return pd.DataFrame(filtered_file_data)


def update_function(this_function_data):
    """Update function definition."""
    assistant_id, function_name = this_function_data
    key = "function_definition_" + function_name
    spec_data = st.session_state[key]

    try:
        spec_json = json.loads(spec_data)
        st.session_state['logger'].log("Updating function {new_spec_json['name']}", verbose=VERBOSE)
        st.session_state['llm_helper'].update_assistant_function(assistant_id, spec_json)
    except json.JSONDecodeError:
        st.session_state['logger'].log("Not a valid function JSON", verbose=VERBOSE)


def delete_function(this_function_data):
    """Delete function definition."""
    assistant_id, function_name = this_function_data
    st.session_state['llm_helper'].delete_assistant_function(assistant_id, function_name)


def update_instructions(assistant_data):
    """Update instructions."""
    assistant_id, previous_instructions = assistant_data
    if previous_instructions != st.session_state['updated_instructions']:
        st.session_state['logger'].log(f'''
                                       For assistant {assistant_id} update instructions {st.session_state['updated_instructions']} 
                                       from {previous_instructions}''', verbose=VERBOSE)
        st.session_state['llm_helper'].update_assistant_instructions(assistant_id, st.session_state['updated_instructions'])
    else:
        st.session_state['logger'].log(f"No updated instructions for assistant {assistant_id}", verbose=VERBOSE)


def update_code_interpreter(assistant_id):
    """Change code interpreter."""
    st.session_state['logger'].log(f"For {assistant_id} code interpreter is {st.session_state['code_interpreter']}", verbose=VERBOSE)
    st.session_state['llm_helper'].update_assistant_code_interpreter_tool(assistant_id, st.session_state['code_interpreter'])


def delete_assistant(assistant_id):
    """Delete Assistant."""
    st.session_state['logger'].log(f"Deleting {assistant_id} ", verbose=VERBOSE)
    st.session_state['llm_helper'].delete_assistant(assistant_id)

def update_conv_starters(assistant_id, conv_starter_id):
    """Update Conv Starter."""
    key=f"update_conv_starters_{conv_starter_id}"
    conv_starter_text =  st.session_state[key]

    st.session_state['llm_helper'].update_conv_starter(assistant_id, conv_starter_id, conv_starter_text)

if 'session_id' not in st.session_state:
    ctx = get_script_run_ctx()
    st.session_state['session_id'] = ctx.session_id
    st.session_state['llm_helper'] = LLMHelper()
    
    st.session_state['logger'] = ObservabilityHelper()
    st.session_state['logger'].log(f"New session created with id {st.session_state['session_id']}", verbose=VERBOSE)

st.session_state['logger'].log(f"Session id is {st.session_state['session_id']}", verbose=VERBOSE)
st.session_state['logger'].log("Configuring assistants", verbose=VERBOSE)

# DISPLAY - TITLE
st.title(content.MANAGE_TITLE_TEXT)

# DISPLAY - ASSISTANT PANEL
assistant_list = st.session_state['llm_helper'].get_assistants()
if len(assistant_list) > 0:
    # All Assitants
    assistant_id_name_list = [(assistant.id, assistant.name) for assistant in assistant_list]
    assistant_id_list   = [assistant[0] for assistant in assistant_id_name_list]
    assistant_name_list = [assistant[1] for assistant in assistant_id_name_list]

# DISPLAY - CREATE ASSISTANT FORM
    with st.form("add_assistant_form"):
        with st.expander(content.MANAGE_CREATE_ASSISTANT):
            new_assistant_name         = st.text_input(content.MANAGE_CREATE_ASSISTANT_NAME, key="new_assistant_name")
            new_assistant_instructions = st.text_area(content.MANAGE_CREATE_ASSISTANT_INSTRUCTIONS, key="new_assistant_instructions")
            new_assistant_submit       = st.form_submit_button(content.MANAGE_CREATE_ASSISTANT_SUBMIT)

        # New function submitted
    if new_assistant_submit:
        if new_assistant_name != "" and new_assistant_instructions != "":
            if st.session_state['llm_helper'].is_duplicated_assistant(new_assistant_name) is False:
                st.session_state['llm_helper'].create_assistant(new_assistant_name, new_assistant_instructions)
                st.session_state['logger'].log(f"New assistant {new_assistant_name} created - refreshing", verbose=VERBOSE)
                st.rerun()
            else:
                st.session_state['logger'].log(f"Duplicated assistant {new_assistant_name}", verbose=VERBOSE)
                st.error(content.MANAGE_CREATE_ASSISTANT_DUPLICATED)

        else:
            st.session_state['logger'].log(f"Name {new_assistant_name} or instructions {new_assistant_instructions} not specified", verbose=VERBOSE)
            st.error(content.MANAGE_CREATE_ASSISTANT_NO_NAME_OR_INSTRUCTIONS)

# Selected Assistant
    this_assistant_name  = st.selectbox(content.MANAGE_ASSISTANT_SELECT_TEXT, assistant_name_list)
    this_assistant_index = assistant_name_list.index(this_assistant_name)
    this_assistant_id = assistant_id_list[this_assistant_index]
    this_assistant = st.session_state['llm_helper'].get_assistant(this_assistant_id)

    this_assistant_conv_starters = st.session_state['llm_helper'].get_assistant_conversation_starter_values(this_assistant)
    this_assistant_files = st.session_state['llm_helper'].get_files_from_assistant(this_assistant)

    # Selected Assistant info
    assistant_description  = this_assistant.description
    assistant_instructions = this_assistant.instructions

# DISPLAY - ASSISTANT DISPLAY
    st.write(content.MANAGE_SELECTED_ASSISTANT_ID + f": {this_assistant_id}")
    st.button(content.MANAGE_DELETE_ASSISTANT, on_click=delete_assistant, args=(this_assistant_id,))
# DISPLAY - ASSISTANT Instructions
    st.text_area(content.MANAGE_SELECTED_ASSISTANT_INSTRUCTIONS, assistant_instructions, key="updated_instructions")
    st.button(content.MANAGE_UPDATE_ASSISTANT_INSTRUCTIONS, on_click=update_instructions, args=((this_assistant_id, assistant_instructions),))
# DISPLAY - ASSISTANT TOOLS TITLE
    st.markdown(f"<DIV style='text-align: center;'><H3>{content.MANAGE_SELECTED_ASSISTANT_TOOLS}</H3></DIV>", unsafe_allow_html=True)
# DISPLAY - ASSISTANT Functions
    # Adding a function
    with st.form("add_action_form"):
        with st.expander(content.MANAGE_ASSISTANT_ACTION_ADD_EXPANDER):
            new_spec_body   = st.text_area(content.MANAGE_ASSISTANT_ACTION_ADD_BODY, key="manage_text_new_spec", height=400)
            new_spec_submit = st.form_submit_button(content.MANAGE_ASSISTANT_ACTION_ADD_BUTTON)
    # New function submitted
    if new_spec_submit:
        if OpenAPIHelper.validate_spec_json(new_spec_body):
            openai_functions = OpenAPIHelper.extract_openai_functions_from_spec(new_spec_body)
            for openai_function in openai_functions:
                st.session_state['llm_helper'].create_assistant_function(this_assistant_id, openai_function)
                st.session_state['logger'].log("New function added - refreshing", verbose=VERBOSE)
            st.rerun()
        else:
            st.error(content.MANAGE_ASSISTANT_NEW_SPEC_NOT_VALID)
            st.session_state['logger'].log("Not a valid function", verbose=VERBOSE)

    st.session_state['logger'].log("Listing functions", verbose=VERBOSE)
    # Listing function
    this_assistant_functions = st.session_state['llm_helper'].get_functions_from_assistant(this_assistant)
    functions_data_list = get_assistant_function_data(this_assistant_functions)
    this_assistant_has_code_interpreter = st.session_state['llm_helper'].assistant_has_code_interpreter(this_assistant_id)

    st.write(content.MANAGE_SELECTED_ASSISTANT_FUNCTIONS)
    for function_data in functions_data_list:
        with st.expander(function_data['name']):
            function_body = st.text_area(content.MANAGE_ASSISTANT_ACTION_BODY,
                                         key="function_definition_" + function_data['name'],
                                         value=function_data['definition'], height=400)
            # Keys
            st.button(content.MANAGE_ASSISTANT_ACTION_UPDATE_BUTTON,
                      key="update_" + function_data['name'],
                      on_click=update_function,
                      args=(((this_assistant_id, function_data['name']),)))
            st.button(content.MANAGE_ASSISTANT_ACTION_DELETE_BUTTON,
                      key="delete_" + function_data['name'],
                      on_click=delete_function,
                      args=(((this_assistant_id, function_data['name']),)))

# DISPLAY - ASSISTANT OTHER TOOLS
    st.write(content.MANAGE_SELECTED_ASSISTANT_CAPABILITIES)
    st.toggle(content.MANAGE_SELECTED_ASSISTANT_CAPABILITIES_CODE_INTERPRETER,
              on_change=update_code_interpreter, key="code_interpreter",
              args=(this_assistant_id,),
              value=this_assistant_has_code_interpreter)
# DISPLAY - ASSISTANT files

    # st.markdown(f"<DIV style='text-align: center;'><H3>{content.MANAGE_SELECTED_ASSISTANT_FILES}</H3></DIV>", unsafe_allow_html=True)

    # if len(this_assistant_files) > 0:
    #     file_data_list = get_file_data(this_assistant_files)
    #     st.write(file_data_list)
    # else:
    #     st.write(content.MANAGE_NO_FILE_MESSAGE)
    #
else:
    st.write(content.MAIN_NO_ASSISTANT_TEXT)

st.markdown(f"<DIV style='text-align: center;'><H3>{content.MANAGE_SELECTED_ASSISTANT_CONV_STARTERS}</H3></DIV>", unsafe_allow_html=True)

st.text_input(content.MANAGE_SELECTED_ASSISTANT_NEW_CONV_STARTER, 
            key="update_conv_starters_new",
            on_change=update_conv_starters,
            args=(this_assistant_id, "new"))

if len(this_assistant_conv_starters) > 0:
    st.markdown(f"<DIV style='text-align: center;'><H4>{content.MANAGE_SELECTED_ASSISTANT_EXISTING_CONV_STARTERS}</H4></DIV>", unsafe_allow_html=True)
    for index, conv_starter in enumerate(this_assistant_conv_starters):
        if conv_starter != "":
            st.text_input(content.MANAGE_SELECTED_ASSISTANT_EXISTING_CONV_STARTER_LABEL, conv_starter,
                        key="update_conv_starters_" + str(index),
                        on_change=update_conv_starters,
                        args=(this_assistant_id, index))
