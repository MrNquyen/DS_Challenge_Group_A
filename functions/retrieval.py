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

def generate_documents(
        img_path, 
        model, 
        prompt='Giải thích thêm thông tin về hình ảnh sau bằng tiếng Việt trong 10 đoạn văn, mỗi đoạn có độ dài từ 5-7 câu',
    ):
    image = Image.open(img_path)
    response = model.generate_content([prompt, image])
    # Check if the response has a text attribute and return it
    if hasattr(response, 'text'):
        return response.text
    else:
        return str(response)
    # return decoded_text
    # return response.text

def generate_questions(img_path, num_of_qa, model):
    image = Image.open(img_path)

    prompt = f"Tạo {num_of_qa} cặp câu hỏi và trả lời về nội dung trong hình sau bằng tiếng Việt."

    response = model.generate_content([prompt, image])
    
    if hasattr(response, 'text'):
        text = response.text.strip()
        if not text:
            return [], []

        questions = []
        answers = []

        # Get QA lists
        text = text.split('\n')
        while('' in text):
            text.remove('')
        text = text[1:]

        # Get questions, answers
        questions = [text[i] for i in range(len(text)) if i % 2 == 0]
        answers = [text[i] for i in range(len(text)) if i % 2 != 0]
            
        return questions, answers, response.text
    else:
        return [], [], ''

def load_model(model_name='gemini-1.5-flash'):
    if 'generate_docs_model' not in st.session_state:
        st.session_state.generate_docs_model = None
    if st.session_state.generate_docs_model == None:
        st.session_state.generate_docs_model=genai.GenerativeModel(model_name)
