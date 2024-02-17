from manager import Manager
from utilities.env_helper   import EnvHelper
import utilities.page_content as content

import streamlit as st

def check_openai_config():
    try:
        st.session_state['manager'].llm_helper.check_openai_endpoint(
            st.session_state['manager'].env_helper.OPENAI_API_BASE, 
            st.session_state['manager'].env_helper.OPENAI_API_KEY, 
            st.session_state['manager'].env_helper.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME
        )
        st.success(content.VARIABLE_CONFIG_PAGE_OPENAI_OK)
    except Exception as e:
        st.error(content.VARIABLE_CONFIG_PAGE_OPENAI_KO )

def on_change_aoai_api_base():
   st.session_state['manager'].env_helper.OPENAI_API_BASE = st.session_state['aoai_api_base']
   check_openai_config()

def on_change_aoai_key():
   st.session_state['manager'].env_helper.OPENAI_API_KEY = st.session_state['aoai_key']
   check_openai_config()

def on_change_aoai_deployment():
   st.session_state['manager'].env_helper.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME = st.session_state['aoai_deployment']
   check_openai_config()

if 'initialized' not in st.session_state:
    manager = Manager()
    st.session_state['manager'] = manager
    st.session_state['initialized'] = True

st.header("Azure OpenAI Config")
az_openai_service_endpoint   = st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_ENDPOINT_FIELD  , st.session_state['manager'].env_helper.OPENAI_API_BASE,                    on_change=on_change_aoai_api_base,   key="aoai_api_base")
az_openai_service_key        = st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_KEY_FIELD       , st.session_state['manager'].env_helper.OPENAI_API_KEY,                     on_change=on_change_aoai_key,        key="aoai_key")
az_openai_service_deployment = st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_DEPLOYMENT_FIELD, st.session_state['manager'].env_helper.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME, on_change=on_change_aoai_deployment, key="aoai_deployment")

