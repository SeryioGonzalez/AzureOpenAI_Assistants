import utilities.page_content as content
from utilities.assistant_factory    import AssistantFactory
from utilities.llm_helper           import LLMHelper
from utilities.observability_helper import ObservabilityHelper

import venv

import streamlit as st

if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True

    assistant_factory = AssistantFactory()
    st.session_state['assistant_factory'] = assistant_factory

    llm_helper = LLMHelper()
    st.session_state['llm_helper'] = llm_helper

    observability_helper = ObservabilityHelper()
    st.session_state['observability_helper'] = observability_helper


st.title(content.MAIN_TITLE_TEXT)

if st.session_state['assistant_factory'].is_there_assistants():
    selected_assistant_name = st.selectbox(content.MAIN_ASSISTANT_SELECT_TEXT, st.session_state['assistant_factory'].get_assistant_name_list())
    assistant_description = st.session_state['assistant_factory'].get_assistant_field(selected_assistant_name, "assistant_description")

    st.write(assistant_description)

    if user_prompt := st.chat_input(content.MAIN_ASSISTANT_CHAT_WELCOME):
        st.chat_message("user").markdown(user_prompt)
        llm_completion = st.session_state['llm_helper'].get_completion(user_prompt)
        st.chat_message("assistant").markdown(llm_completion)

else:
    st.write(content.MAIN_NO_ASSISTANT_TEXT)


