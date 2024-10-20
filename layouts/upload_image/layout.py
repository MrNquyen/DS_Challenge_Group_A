import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
import joblib
import cv2
import json

from streamlit_image_coordinates import streamlit_image_coordinates as im_coordinates

from utils import configImageInput, listROI, getFileName
from utils import st_upload_image, st_upload_pdf, st_upload_video_link
from utils import load_json, save_json, preprocess_text, show_img, insert_number

from functions.upload_image.function import A_save_upload_file
from functions.retrieval import generate_documents, generate_caption, generate_questions

INPUT_CONFIG = configImageInput()

### Tab layout
# Upload tab
def U_leftSidePageLayout(streamlit_col):
    '''
        Upload File
        - Detach Information
        - Generate Supported Documents
    '''

    pageLayoutObject = {}

    # Upload file buttons
    uploaded_file = streamlit_col.file_uploader('Choose and Upload File', 
                                                type=INPUT_CONFIG['type'],
                                                accept_multiple_files=False,
                                                key='U_file_upload')

    streamlit_col1, streamlit_col2 = streamlit_col.columns(2)
    
    if uploaded_file is None:
        if streamlit_col1==True or streamlit_col2==True:
            st.write('You must upload an IMAGE')

    # pageLayoutObject dictionary
    pageLayoutObject['uploaded_file'] = uploaded_file

    return pageLayoutObject

def U_rightSidePageLayout(streamlit_col):
    '''
        Show Input image
    '''
    pageLayoutObject = {}

    visual_container = streamlit_col.container(border=True)

    # pageLayoutObject dictionary
    pageLayoutObject['visual_container'] = visual_container

    return pageLayoutObject

def upload_tab_layout(PARA,
                      upload_tab,
                      layout_dict):
    with upload_tab:
        U_col1, col2 = st.columns(2) # create page columns
        U_col1_layout = U_leftSidePageLayout(U_col1)
        col2_layout = U_rightSidePageLayout(col2)
        
        # col2
        layout_dict['uploaded_file'] = U_col1_layout['uploaded_file']
        
        # col2
        layout_dict['visual_container'] = col2_layout['visual_container']

### Adding tab
# Build container to show ROI
def build_container_ROI(img_path,
                        add_tab,
                        container_name=''):
    '''
        Two expander in 2 columns
        - Left expander: Show ROI image
        - Right columns: 
            + Show method input file and link (Upload file)
            + Expander to show content of the input link
    
        Index: The index of ROI: 1, 2, 3

        col2: Use for custom - Vì sử dụng layout này cho hai tab Adding và Documents nên layout sẽ khác nhau
    '''
    # Load Image
    visual_image = cv2.imread(img_path)
    container = add_tab.container(height=500,
                                     border=True)

    con_col1, con_col2 = container.columns(2)

    # Left column
    con_col1.subheader(container_name,
                       divider="gray")
    left_expander = con_col1.expander('Show detach image')
    if visual_image is None:
        left_expander.write('Load Image Failed !!')
        return
    left_expander.image(visual_image)
    
    # Custom Right column
    # ...

    return con_col1, con_col2

def A_right_column_layout(PARA,
                          streamlit_col,
                          key):
    '''
        - Upload file and link
        - Show file and link content
    '''
    streamlit_col.subheader('Choose and Upload Your Files',
                            divider="gray")

    # Allow user to modify nummber of file type to upload
    container = streamlit_col.container(border=True)
    upload_pdf = st_upload_pdf(
        streamlit_layout=container,
        accept_multiple_files=True,
        key=f'{key}_pdf'
    )

    upload_vid = st_upload_video_link(
        streamlit_layout=container,
        key=f'{key}_vid'
    )

    upload_img = st_upload_image(
        streamlit_layout=container,
        accept_multiple_files=True,
        key=f'{key}_img'
    )

    pdf_save_dir = f'{PARA['SAVE_DIR']}/upload_pdf'
    img_save_dir = f'{PARA['SAVE_DIR']}/upload_img'
    vid_save_dir = f'{PARA['SAVE_DIR']}/upload_vid'

    return {
        'pdf': {
            'file_content': upload_pdf,
            'save_dir': pdf_save_dir
        },
        'vid': {
            'file_content': upload_vid,
            'save_dir': vid_save_dir
        },
        'img': {
            'file_content': upload_img,
            'save_dir': img_save_dir
        },
    }


def add_tab_layout(upload_file,
                   PARA,
                   add_tab,):
    img_name = getFileName(upload_file.name)
    img_json_path = f'{PARA['SAVE_DIR']}/{img_name}/{img_name}.json'
    roi_paths = listROI(PARA, img_name)

    # Load json file
    img_json = load_json(img_json_path)

    for i, roi_path in enumerate(roi_paths):
        _, A_col2 = build_container_ROI(img_path=roi_path,
                                        add_tab=add_tab,
                                        container_name=f'PIC_{i}')
        save_info_dict = A_right_column_layout(PARA,
                                               streamlit_col=A_col2,
                                               key=roi_path)
    
        # Save update json
        if A_col2.button('Save Upload File', key=roi_path):
            for upload_type, save_info in  save_info_dict.items():
                save_dir = save_info['save_dir']
                file_contents = save_info['file_content']

                save_file_paths = A_save_upload_file(file_contents, save_dir, upload_type)
                img_json[roi_path][upload_type] += save_file_paths
                img_json[roi_path][upload_type] = list(set(img_json[roi_path][upload_type]))
            # print(img_json)
            save_json(img_json_path, img_json)

# Document tab
def D_right_column_layout(
        PARA,
        streamlit_col,
        org_img_name,
        roi_path,
    ):
    '''
        - Show the external-knowledge information of the image
    '''
    streamlit_col.subheader(
        'Extra Information',
        divider="gray",
    )
    container = streamlit_col.container(border=True)
    
    # Load json file for image
    # roi_name = roi_path.split('/')[-1]
    json_path = f'{PARA['SAVE_DIR']}/{org_img_name}/{org_img_name}.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        img_json = json.load(f)
    if 'external_infomation' not in img_json[roi_path]:
        list_paragraphs = generate_documents(
            img_path=roi_path,
            model=st.session_state.generate_docs_model,
        )

        # Ensure the generated text is valid and encoded properly
        if isinstance(list_paragraphs, str):
            img_json[roi_path]['external_infomation'] = preprocess_text(list_paragraphs)
        else:
            img_json[roi_path]['external_infomation'] = preprocess_text(str(list_paragraphs))
        # img_json[roi_path]['external_infomation'] = str(list_paragraphs).encode('utf-8')

    else:
        list_paragraphs = img_json[roi_path]['external_infomation']
    
    # Dump json
    with open(f"{PARA['SAVE_DIR']}/{org_img_name}/{org_img_name}.json", 'w', encoding='utf-8') as f:
        json.dump(img_json, f, ensure_ascii=False, indent=5)  # Corrected arguments

    container.write(list_paragraphs)
    
def documents_tab_layout(
        upload_file,
        PARA,
        documents_tab
    ):
    img_name = getFileName(upload_file.name)
    roi_paths = listROI(PARA, img_name)
    for i, roi_path in enumerate(roi_paths):
        D_col1, D_col2 = build_container_ROI(img_path=roi_path,
                                             add_tab=documents_tab,
                                             container_name=f'PIC_{i+1}')
        D_right_column_layout(
            PARA,
            streamlit_col=D_col2, 
            org_img_name=img_name,
            roi_path=roi_path,
        )


# QA tab
def QA_layout(
        PARA,
        streamlit_col,
        img_path,
    ):
    '''
        Show the question and the answer of the question
    '''
    model = st.session_state.generate_docs_model
    # Image Block
    image_container = streamlit_col.container(border=True)
    with image_container:
        show_img(img_path)

    # Caption Container
    streamlit_col.subheader(
        'Caption for Infographic',
        divider="gray",
    )
    caption_container = streamlit_col.container(border=True)
    
    ## Load and save caption
    img_name = getFileName(img_path.split('/')[-1])
    json_path = f'{PARA['SAVE_DIR']}/{img_name}/{img_name}.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        img_json = json.load(f)
    if 'caption' not in img_json:
        caption = generate_caption(img_path, model)

        # Ensure the generated text is valid and encoded properly
        if isinstance(caption, str):
            img_json['caption'] = preprocess_text(caption)
        else:
            img_json['caption'] = preprocess_text(str(caption))
        # Dump json
        with open(f"{PARA['SAVE_DIR']}/{img_name}/{img_name}.json", 'w', encoding='utf-8') as f:
            json.dump(img_json, f, ensure_ascii=False, indent=5)  # Corrected arguments

    else:
        caption = img_json['caption']
    ## Write caption
    with caption_container:
        st.write(caption)
    
    # QA block
    streamlit_col.subheader(
        'QAs for Infographic',
        divider="gray",
    )
    # Input number of question:
    with streamlit_col:
        print('Input Number')
        num_qa = insert_number('Select number of questions that you want to generate !!!')
    
    # Show qa
    print(num_qa)
    list_questions, list_ans, org_text = generate_questions(
        img_path=img_path,
        num_of_qa=num_qa,
        model=model,
    )
    
    for i, (question, ans) in enumerate(zip(list_questions, list_ans)):
        print('Generate')
        question, ans = preprocess_text(question), preprocess_text(ans)
        container = streamlit_col.container(border=True)
        col1, col2 = container.columns(2)
        
        # Expander for question
        expander_ques = col1.expander(f'Question number {i+1}')
        ques_container =  expander_ques.container(border=True)
        ques_container.write(question)

        # Expander for answer
        expander_ans = col2.expander(f'Answer number {i+1}')
        expander_ans.write(ans)