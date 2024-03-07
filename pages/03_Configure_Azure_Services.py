"""Page for Configuring Azure services."""
from streamlit.runtime.scriptrunner import get_script_run_ctx
import streamlit as st

from manager import Manager
from utilities.observability_helper import ObservabilityHelper
import utilities.page_content as content

VERBOSE = True


def check_openai_config():
    """Check OpenAI Config."""
    try:
        st.session_state['manager'].llm_helper.check_openai_endpoint(
            st.session_state['manager'].env_helper.OPENAI_API_BASE,
            st.session_state['manager'].env_helper.OPENAI_API_KEY,
            st.session_state['manager'].env_helper.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME,
            st.session_state['manager'].env_helper.AZURE_OPENAI_API_VERSION
        )
        return True
    except Exception:
        return False


def on_change_aoai_resource_name():
    """Change OpenAI Config. API Endopint."""
    st.session_state['logger'].log(f"CONF AZURE - Updating AOAI RES NAME TO  {st.session_state['aoai_resource_name']}", verbose=VERBOSE)
    st.session_state['manager'].update_env_variable("AZURE_OPENAI_RESOURCE_NAME", st.session_state['aoai_resource_name'])
    

def on_change_aoai_key():
    """Change OpenAI Config. API key."""
    st.session_state['logger'].log(f"CONF AZURE - Updating AOAI KEY TO  {st.session_state['aoai_key']}", verbose=VERBOSE)
    st.session_state['manager'].update_env_variable("AZURE_OPENAI_KEY", st.session_state['aoai_key'])
    st.session_state['status'] = check_openai_config()
    

def on_change_aoai_deployment_name():
    """Change OpenAI Config. Deployment."""
    st.session_state['logger'].log(f"CONF AZURE - Updating AOAI DEP NAME TO  {st.session_state['aoai_deployment_name']}", verbose=VERBOSE)
    st.session_state['manager'].update_env_variable("AZURE_OPENAI_MODEL_DEPLOYMENT_NAME", st.session_state['aoai_deployment_name'])
    

def on_change_aoai_api_version():
    """Change OpenAI Config. API VERSION."""
    st.session_state['logger'].log(f"CONF AZURE - Updating AOAI API VER TO  {st.session_state['aoai_api_version']}", verbose=VERBOSE)
    st.session_state['manager'].update_env_variable("AZURE_OPENAI_API_VERSION", st.session_state['aoai_api_version'])


if 'session_id' not in st.session_state:
    ctx = get_script_run_ctx()
    st.session_state['session_id'] = ctx.session_id
    st.session_state['manager'] = Manager(st.session_state['session_id'])

    st.session_state['logger'] = ObservabilityHelper()
    st.session_state['logger'].log(f"CONF AZURE - New session created with id {st.session_state['session_id']}", verbose=VERBOSE)

if 'status' not in st.session_state:
    st.session_state['status'] = check_openai_config()

st.session_state['logger'].log(f"CONF AZURE - Session id is {st.session_state['session_id']}", verbose=VERBOSE)

# GUI

st.header(content.VARIABLE_PAGE_HEADER)

col1, col2, col3 = st.columns([0.25, 0.5, 0.25])
with col1:
    st.write(' ')

with col2:
    if st.session_state['status'] is True:
        st.success(content.VARIABLE_CONFIG_PAGE_OPENAI_OK, icon="✅")
    elif st.session_state['status'] is False:
        st.error(content.VARIABLE_CONFIG_PAGE_OPENAI_KO, icon="🚨")
with col3:
    st.write(' ')

st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_RESOURCE_NAME,
                                             st.session_state['manager'].env_helper.AZURE_OPENAI_RESOURCE_NAME,
                                             on_change=on_change_aoai_resource_name,
                                             key="aoai_resource_name")
st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_KEY_FIELD,
                                             st.session_state['manager'].env_helper.OPENAI_API_KEY,
                                             on_change=on_change_aoai_key,
                                             key="aoai_key")
st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_DEPLOYMENT_FIELD,
                                             st.session_state['manager'].env_helper.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME,
                                             on_change=on_change_aoai_deployment_name,
                                             key="aoai_deployment_name")
st.text_input(content.VARIABLE_CONFIG_PAGE_OPENAI_API_VERSION,
                                             st.session_state['manager'].env_helper.AZURE_OPENAI_API_VERSION,
                                             on_change=on_change_aoai_api_version,
                                             key="aoai_api_version")