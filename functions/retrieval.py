import streamlit as st
import google.generativeai as genai
import os
from PIL import Image

genai.configure(api_key="AIzaSyDuWlJNIE0vCZqTrvxTamt4N9aLOhzF6q8")

def generate_caption(img_path, model):
    image = Image.open(img_path)
    response = model.generate_content(["Tóm tắt nội dung trong hình sau bằng tiếng Việt", image])
    if hasattr(response, 'text'):
        return response.text
    else:
        return str(response)

def generate_documents(img_path, model):
    image = Image.open(img_path)
    response = model.generate_content(["Giải thích thêm thông tin về hình ảnh sau bằng tiếng Việt với độ dài 5 đoạn văn", image])
    # Check if the response has a text attribute and return it
    if hasattr(response, 'text'):
        return response.text
    else:
        return str(response)
    # return decoded_text
    # return response.text

def load_model(model_name='gemini-1.5-flash'):
    if 'generate_docs_model' not in st.session_state:
        st.session_state.generate_docs_model = None
    if st.session_state.generate_docs_model == None:
        st.session_state.generate_docs_model=genai.GenerativeModel(model_name)
