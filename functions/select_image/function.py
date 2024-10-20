import streamlit as st

# Switch Layout
def switch_layout(
        target_content: str,
        path = None, doc_type = None):
    '''
        Layout: selection_layout, image_layout, doc_content
    '''
    st.session_state.target_layout = target_content
    st.session_state.current_variables = (path, doc_type)