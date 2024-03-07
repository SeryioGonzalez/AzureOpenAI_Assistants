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
    st.session_state['logger'].log(f"MAIN - New session {st.session_state['session_id']}", verbose=VERBOSE)

st.session_state['logger'].log(f"MAIN - Session id is {st.session_state['session_id']}", verbose=VERBOSE)

st.title(content.MAIN_TITLE_TEXT)

# Check if OPENAI IS RUNNING
assistant_data_list = st.session_state['manager'].get_assistant_data_tuple_list()
# Since calls to OpenAI API is slow, make a single one with all assistant data
openai_status = assistant_data_list is not None
st.session_state['logger'].log(f"MAIN - OpenAI status is OK: {openai_status}", verbose=VERBOSE)
if openai_status:
    
    if len(assistant_data_list) > 0:
        # GET ASSISTANT INFO
        st.session_state['logger'].log(f"MAIN - Num of assistants is {len(assistant_data_list)}", verbose=VERBOSE)
        assistant_ids, assistant_names, assistant_descriptions, assistant_created_at = zip(*assistant_data_list)
        #The user will select the assistant and from there we retrieve data
        assistant_name = st.selectbox(content.MAIN_ASSISTANT_SELECT_TEXT,  assistant_names)
        assistant_id = assistant_ids[assistant_names.index(assistant_name)]
        assistant_description = assistant_descriptions[assistant_names.index(assistant_name)]
        assistant_created_at  = assistant_created_at[assistant_names.index(assistant_name)]

        st.session_state['logger'].log(f"MAIN - Rendering assistant_id {assistant_id}", verbose=VERBOSE)
    # DISPLAY - Assistant description
        st.write(assistant_description)

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
        st.session_state['logger'].log(f"MAIN - Code Interpreter checked", verbose=VERBOSE)

        conv_starters = st.session_state['manager'].llm_helper.get_assistant_conversation_starter_values(None, assistant_id=assistant_id)
    # DISPLAY - CONVERSATION STARTERS
        if len(conv_starters) > 0 and ('has_user_input' not in st.session_state or st.session_state['has_user_input'] != assistant_id):
            st.markdown(f"<DIV style='text-align: center;'><H4>{content.MAIN_ASSISTANT_CONV_STARTERS}</H4></DIV>", unsafe_allow_html=True)
            for index, conv_starter in enumerate(conv_starters):
                st.markdown(f"<DIV><H5> - {conv_starter}</H5></DIV>", unsafe_allow_html=True)
        st.session_state['logger'].log(f"MAIN - Conv Starters checked", verbose=VERBOSE)
        st.divider() 
    # DISPLAY - USER PROMPT
        st.session_state['logger'].log(f"MAIN - Awaiting Input", verbose=VERBOSE)
        if user_prompt := st.chat_input(content.MAIN_ASSISTANT_CHAT_WELCOME):
            #We store if there has been user input for conv starters
            st.session_state['has_user_input'] = assistant_id
            # USER PROMPT
            st.chat_message("user").markdown(user_prompt)
            # THREAD COMPLETION
            thread_run_messages = st.session_state['manager'].run_thread(user_prompt, assistant_id)
            st.session_state['logger'].log(f"Thread messages {thread_run_messages}", verbose=VERBOSE)
            st.chat_message("assistant").markdown(thread_run_messages[0]['message_value'])

    # DISPLAY - NO ASSISTANTS CREATED
    else:
        st.write(content.MAIN_NO_ASSISTANT_TEXT)
else:
    st.markdown(f"<DIV style='color: red;'><H2>{content.MAIN_NO_AZ_OPEN_AI_CONNECTION}</H2></DIV>", unsafe_allow_html=True)