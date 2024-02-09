from manager import Manager
from utilities.env_helper   import EnvHelper
import utilities.page_content as content


import streamlit as st

if 'initialized' not in st.session_state:
    manager = Manager()
    st.session_state['manager'] = manager
    st.session_state['initialized'] = True

st.header("Azure OpenAI Config")
az_openai_service_endpoint   = st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_ENDPOINT_FIELD  , st.session_state['manager'].env_helper.OPENAI_API_BASE)
az_openai_service_key        = st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_KEY_FIELD       , st.session_state['manager'].env_helper.OPENAI_API_KEY)
az_openai_service_deployment = st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_DEPLOYMENT_FIELD, st.session_state['manager'].env_helper.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME)