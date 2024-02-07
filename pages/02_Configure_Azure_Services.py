import utilities.page_content as content
from utilities.env_helper   import EnvHelper
from utilities.llm_helper           import LLMHelper
from utilities.observability_helper import ObservabilityHelper

import streamlit as st

if 'initialized' not in st.session_state:
    st.session_state['initialized'] = True

    env_helper = EnvHelper()
    st.session_state['env_helper'] = env_helper

    llm_helper = LLMHelper()
    st.session_state['llm_helper'] = llm_helper

    observability_helper = ObservabilityHelper()
    st.session_state['observability_helper'] = observability_helper



st.header("Azure OpenAI Config")
az_openai_service_endpoint   = st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_ENDPOINT_FIELD  , st.session_state['env_helper'].OPENAI_API_BASE)
az_openai_service_key        = st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_KEY_FIELD       , st.session_state['env_helper'].OPENAI_API_KEY)
az_openai_service_deployment = st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_DEPLOYMENT_FIELD, st.session_state['env_helper'].AZURE_OPENAI_MODEL_NAME)