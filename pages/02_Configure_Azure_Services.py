"""Page for Configuring Azure services"""
from streamlit.runtime.scriptrunner import get_script_run_ctx
import streamlit as st

from manager import Manager
from utilities.observability_helper import ObservabilityHelper
import utilities.page_content as content

VERBOSE = True


def check_openai_config():
    try:
        st.session_state['manager'].llm_helper.check_openai_endpoint(
            st.session_state['manager'].env_helper.OPENAI_API_BASE,
            st.session_state['manager'].env_helper.OPENAI_API_KEY,
            st.session_state['manager'].env_helper.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME
        )
        st.success(content.VARIABLE_CONFIG_PAGE_OPENAI_OK)
    except Exception:
        st.error(content.VARIABLE_CONFIG_PAGE_OPENAI_KO)


def on_change_aoai_api_base():
    st.session_state['manager'].env_helper.OPENAI_API_BASE = st.session_state['aoai_api_base']
    check_openai_config()


def on_change_aoai_key():
    st.session_state['manager'].env_helper.OPENAI_API_KEY = st.session_state['aoai_key']
    check_openai_config()


def on_change_aoai_deployment():
    st.session_state['manager'].env_helper.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME = st.session_state['aoai_deployment']
    check_openai_config()


if 'session_id' not in st.session_state:
    ctx = get_script_run_ctx()
    st.session_state['session_id'] = ctx.session_id
    st.session_state['manager'] = Manager(st.session_state['session_id'])

    st.session_state['logger'] = ObservabilityHelper()
    st.session_state['logger'].log(f"New session created with id {st.session_state['session_id']}", verbose=VERBOSE)

st.session_state['logger'].log(f"Session id is {st.session_state['session_id']}", verbose=VERBOSE)


st.header(content.VARIABLE_PAGE_HEADER)
az_openai_service_endpoint   = st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_ENDPOINT_FIELD,   st.session_state['manager'].env_helper.OPENAI_API_BASE,                    on_change=on_change_aoai_api_base,   key="aoai_api_base")
az_openai_service_key        = st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_KEY_FIELD,        st.session_state['manager'].env_helper.OPENAI_API_KEY,                     on_change=on_change_aoai_key,        key="aoai_key")
az_openai_service_deployment = st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_DEPLOYMENT_FIELD, st.session_state['manager'].env_helper.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME, on_change=on_change_aoai_deployment, key="aoai_deployment")
