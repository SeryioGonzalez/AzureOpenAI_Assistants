import utilities.page_content as content
from manager import Manager

import streamlit as st

if 'initialized' not in st.session_state:
    manager = Manager()
    st.session_state['manager'] = manager
    st.session_state['initialized'] = True

st.title(content.MANAGE_TITLE_TEXT )

if st.session_state['manager'].are_there_assistants():
    selected_assistant_name = st.selectbox(content.MAIN_ASSISTANT_SELECT_TEXT, st.session_state['manager'].get_assistant_name_list())
    assistant_description = st.session_state['manager'].get_assistant_field(selected_assistant_name, "description")

    if assistant_description is not None:
        st.write(assistant_description)

else:
    st.write(content.MAIN_NO_ASSISTANT_TEXT)


