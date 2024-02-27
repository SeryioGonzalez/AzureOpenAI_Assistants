"""Main page"""
from streamlit.runtime.scriptrunner import get_script_run_ctx
import streamlit as st

import utilities.page_content as content
from utilities.observability_helper import ObservabilityHelper
from manager import Manager

VERBOSE = True

if 'session_id' not in st.session_state:
    ctx = get_script_run_ctx()
    st.session_state['session_id'] = ctx.session_id
    st.session_state['manager'] = Manager(st.session_state['session_id'])

    st.session_state['logger'] = ObservabilityHelper()
    st.session_state['logger'].log(f"New session created with id {st.session_state['session_id']}", verbose=VERBOSE)

st.session_state['logger'].log(f"Session id is {st.session_state['session_id']}", verbose=VERBOSE)

st.title(content.MAIN_TITLE_TEXT)

if st.session_state['manager'].are_there_assistants():
    # GET ASSISTANT INFO
    available_assistants = st.session_state['manager'].get_assistant_id_name_tuple_list()
    assistant_ids, assistant_names = [id for id, name in available_assistants], [name for id, name in available_assistants]

    assistant_name = st.selectbox(content.MAIN_ASSISTANT_SELECT_TEXT,  assistant_names)
    assistant_id = assistant_ids[assistant_names.index(assistant_name)]

# DISPLAY - Chat messages from history on app rerun
    for message in st.session_state['manager'].get_message_list(assistant_id):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# DISPLAY - GET FILE INFO
    # Placeholder. Issue in dealing with files
    # uploaded_file = st.file_uploader(content.MAIN_ASSISTANT_UPLOAD_DOCUMENT)
    uploaded_file = None
    if uploaded_file is not None:
        st.session_state['logger'].log("New uploaded file", verbose=VERBOSE)
        if st.session_state['manager'].upload_file_for_assistant_messages(assistant_id, uploaded_file):
            st.write(content.MAIN_FILE_UPLOAD_OK)
        else:
            st.write(content.MAIN_FILE_UPLOAD_KO)

# DISPLAY - USER PROMPT
    if user_prompt := st.chat_input(content.MAIN_ASSISTANT_CHAT_WELCOME):
        # USER PROMPT
        st.chat_message("user").markdown(user_prompt)

        # THREAD COMPLETION
        thread_run_messages = st.session_state['manager'].run_thread(user_prompt, assistant_id)
        st.session_state['logger'].log(f"Thread messages {thread_run_messages}", verbose=VERBOSE)
        st.chat_message("assistant").markdown(thread_run_messages[0]['message_value'])

# DISPLAY - NO ASSISTANTS CREATED
else:
    st.write(content.MAIN_NO_ASSISTANT_TEXT)
