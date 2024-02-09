"""Main page"""
import streamlit as st

import utilities.page_content as content
from manager import Manager

if 'initialized' not in st.session_state:
    manager = Manager()
    st.session_state['manager'] = manager
    st.session_state['initialized'] = True

st.title(content.MAIN_TITLE_TEXT)

if st.session_state['manager'].are_there_assistants():
    assistant_name = st.selectbox(content.MAIN_ASSISTANT_SELECT_TEXT, st.session_state['manager'].get_assistant_name_list())

    if user_prompt := st.chat_input(content.MAIN_ASSISTANT_CHAT_WELCOME):
        st.chat_message("user").markdown(user_prompt)
        thread_run_step = st.session_state['manager'].run_thread(user_prompt, assistant_name)
        st.chat_message("assistant").markdown(thread_run_step)

    uploaded_file = st.file_uploader(content.MAIN_ASSISTANT_UPLOAD_DOCUMENT)
    if uploaded_file is not None:
        upload_success = st.session_state['manager'].upload_file_to_assistant(assistant_name, uploaded_file)

        if upload_success:
            st.write(content.MAIN_FILE_UPLOAD_OK)
        else:
            st.write(content.MAIN_FILE_UPLOAD_KO)


else:
    st.write(content.MAIN_NO_ASSISTANT_TEXT)
