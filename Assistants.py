"""Main page"""
from streamlit.runtime.scriptrunner import get_script_run_ctx
import streamlit as st

import utilities.page_content as content
from manager import Manager

if 'initialized' not in st.session_state:
    manager = Manager()
    st.session_state['manager'] = manager
    ctx = get_script_run_ctx()
    st.session_state['session_id'] = ctx.session_id
    st.session_state['initialized'] = True
    st.session_state['messages'] = []
    st.session_state['manager'].log(f"New session created with id {st.session_state['session_id']}")

st.title(content.MAIN_TITLE_TEXT)

if st.session_state['manager'].are_there_assistants():
#GET ASSISTANT INFO
    available_assistants = st.session_state['manager'].get_assistant_id_name_list()
    assistant_ids, assistant_names = [id for id, name in available_assistants], [name for id, name in available_assistants]

    assistant_name = st.selectbox(content.MAIN_ASSISTANT_SELECT_TEXT,  assistant_names)
    assistant_id = assistant_ids[assistant_names.index(assistant_name)]

#GET FILE INFO
    uploaded_file = st.file_uploader(content.MAIN_ASSISTANT_UPLOAD_DOCUMENT)
    if uploaded_file is not None:
        upload_success = st.session_state['manager'].upload_file_to_assistant(assistant_id, uploaded_file)

        if upload_success:
            st.write(content.MAIN_FILE_UPLOAD_OK)
        else:
            st.write(content.MAIN_FILE_UPLOAD_KO)

# Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_prompt := st.chat_input(content.MAIN_ASSISTANT_CHAT_WELCOME):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        st.chat_message("user").markdown(user_prompt)
        thread_run_messages = st.session_state['manager'].run_thread(st.session_state['session_id'], user_prompt, assistant_id)
        st.session_state.messages.append({"role": "assistant", "content": thread_run_messages[0]['message_value']})
        st.chat_message("assistant").markdown(thread_run_messages[0]['message_value'])

else:
    st.write(content.MAIN_NO_ASSISTANT_TEXT)
