import streamlit as st
import os
import json

from layouts.select_image.layout import image_layout, select_img_layout, show_doc_content

def main():
    if 'selected_img' not in st.session_state:
        st.session_state.selected_img = None
    if 'target_layout' not in st.session_state:
        st.session_state.target_layout = 'selection_layout'
    if st.session_state.target_layout == 'selection_layout':
        select_img_layout()
    elif st.session_state.target_layout == 'image_layout':
        image_layout(st.session_state.selected_img)
    elif st.session_state.target_layout == 'doc_content':
        path, doc_type = st.session_state.current_variables
        show_doc_content(path, doc_type)