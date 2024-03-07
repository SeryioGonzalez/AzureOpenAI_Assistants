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
    st.session_state['logger'].log(f"THREADS - New session {st.session_state['session_id']}", verbose=VERBOSE)

st.session_state['logger'].log(f"THREADS - Session id is {st.session_state['session_id']}", verbose=VERBOSE)

st.title(content.MAIN_TITLE_TEXT)

# Check if OPENAI IS RUNNING
openai_status = st.session_state['manager'].llm_helper.check_openai_endpoint_from_settings()
if openai_status:
    if st.session_state['manager'].are_there_assistants():
        # GET ASSISTANT INFO
        assistants = st.session_state['manager'].get_assistant_data_tuple_list()
        assistant_ids, assistant_names, assistant_descriptions = [id for id, _, _ in assistants], [name for _, name, _ in assistants], [description for _, _, description in assistants]

        assistant_name = st.selectbox(content.MAIN_ASSISTANT_SELECT_TEXT,  assistant_names)
        assistant_id = assistant_ids[assistant_names.index(assistant_name)]
        assistant_description = assistant_descriptions[assistant_names.index(assistant_name)]

    # DISPLAY - NO ASSISTANTS CREATED
    else:
        st.write(content.MAIN_NO_ASSISTANT_TEXT)
else:
    st.markdown(f"<DIV style='color: red;'><H2>{content.MAIN_NO_AZ_OPEN_AI_CONNECTION}</H2></DIV>", unsafe_allow_html=True)