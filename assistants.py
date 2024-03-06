"""Main page."""
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
    st.session_state['logger'].log(f"New session {st.session_state['session_id']}", verbose=VERBOSE)

st.session_state['logger'].log(f"Session id is {st.session_state['session_id']}", verbose=VERBOSE)

st.title(content.MAIN_TITLE_TEXT)

if st.session_state['manager'].are_there_assistants():
    # GET ASSISTANT INFO
    assistants = st.session_state['manager'].get_assistant_id_name_tuple_list()
    assistant_ids, assistant_names = [id for id, _ in assistants], [name for _, name in assistants]

    assistant_name = st.selectbox(content.MAIN_ASSISTANT_SELECT_TEXT,  assistant_names)
    assistant_id = assistant_ids[assistant_names.index(assistant_name)]

# DISPLAY - Chat messages from history on app rerun
    for message in st.session_state['manager'].get_message_list(assistant_id):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# DISPLAY - GET FILE INFO
    # Code interpreter dependant
    if st.session_state['manager'].llm_helper.assistant_has_code_interpreter(assistant_id):
        file = st.file_uploader(content.MAIN_ASSISTANT_UPLOAD_DOCUMENT)
        if file is not None:
            st.session_state['logger'].log("New uploaded file", verbose=VERBOSE)
            if st.session_state['manager'].upload_file_for_assistant_messages(assistant_id, file):
                st.write(content.MAIN_FILE_UPLOAD_OK)
            else:
                st.write(content.MAIN_FILE_UPLOAD_KO)

    conv_starters = st.session_state['manager'].llm_helper.get_assistant_conversation_starter_values(None, assistant_id=assistant_id)

    if len(conv_starters) > 0 and ('has_threads' not in st.session_state or st.session_state['has_threads'] != assistant_id):
        st.markdown(f"<DIV style='text-align: center;'><H3>{content.MAIN_ASSISTANT_CONV_STARTERS}</H3></DIV>", unsafe_allow_html=True)
        for index, conv_starter in enumerate(conv_starters):
            st.markdown(f"<DIV><H5>{conv_starter}</H5></DIV>", unsafe_allow_html=True)

# DISPLAY - USER PROMPT
    if user_prompt := st.chat_input(content.MAIN_ASSISTANT_CHAT_WELCOME):
        # USER PROMPT
        st.chat_message("user").markdown(user_prompt)
        #We store if there has been threads for conv starters
        st.session_state['has_threads'] = assistant_id
        # THREAD COMPLETION
        thread_run_messages = st.session_state['manager'].run_thread(user_prompt, assistant_id)
        st.session_state['logger'].log(f"Thread messages {thread_run_messages}", verbose=VERBOSE)
        st.chat_message("assistant").markdown(thread_run_messages[0]['message_value'])

# DISPLAY - NO ASSISTANTS CREATED
else:
    st.write(content.MAIN_NO_ASSISTANT_TEXT)
