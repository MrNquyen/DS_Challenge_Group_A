import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
import joblib
import cv2
import json

from streamlit_pdf_viewer import pdf_viewer
from utils import get_uploaded_images, load_PARA, listROI, getFileName, load_json
from layouts.upload_image.layout import U_rightSidePageLayout

from functions.select_image.function import switch_layout
from utils import show_pdf, show_vid, show_img

# Load PARA
PARA = load_PARA()

# Show document content
def show_doc_content(path, doc_type: str):
    container = st.container(
        border=True
    )

    if container.button('Move To Selection Page', use_container_width=True):
        switch_layout('image_layout')
    with container:
        if doc_type == 'pdf':
            with open(path, 'rb') as file:
                binary_data = file.read()
                show_pdf(
                    input=binary_data,
                    key=f'{path}'
                )
                file.close()
        elif doc_type == 'vid':
            show_vid(path)
        elif doc_type == 'img':
            show_img(path)
    

# Image layout
def image_layout(image_name):
    list_rois = listROI(PARA, image_name)
    tab_names = [f'ROI_{i}' for i in range(len(list_rois))] 

    # Create tabs
    tabs = st.tabs(tab_names)
    for i, tab in enumerate(tabs):
        roi_path = list_rois[i]

        # Load roi json file
        json_path = f'{PARA['SAVE_DIR']}/{image_name}/{image_name}.json'
        img_json = load_json(json_path)
        
        # Show ROI Image
        container = tab.container(
            border=True
        )

        with container:
            show_img(roi_path)

        # Create cols
        pdf_col, vid_col, img_col = tab.columns(3)
        
        # Pdf column
        pdf_paths = img_json[roi_path]['pdf']
        # Header
        pdf_col.subheader(
            'Select PDF For Presentation',
            divider="gray"
        )
        for pdf_path in pdf_paths:
            pdf_name = getFileName(pdf_path.split('/')[-1])
            # Create button
            if pdf_col.button(
                pdf_name, 
                key=f'{roi_path}_button_{pdf_name}',
                use_container_width=True,
            ):
                pdf_col.write('Switch content')
                switch_layout('doc_content', pdf_path, 'pdf')

        # Vid column
        vid_paths = img_json[roi_path]['vid']
        # Header
        vid_col.subheader(
            'Select PDF For Presentation',
            divider="gray"
        )
        # Create button
        for vid_path in vid_paths:
            if vid_col.button(
                vid_path, 
                key=f'{roi_path}_button_{vid_path}',
                use_container_width=True,
            ):
                vid_col.write('Switch content')
                switch_layout('doc_content', vid_path, 'vid')
                
        
        # Image column
        img_paths = img_json[roi_path]['img']
        # Header
        img_col.subheader(
            'Select PDF For Presentation',
            divider="gray"
        )
        # Create button
        for img_path in img_paths:
            img_name = getFileName(img_path.split('/')[-1])
            if img_col.button(
                img_name, 
                key=f'{roi_path}_button_{img_name}',
                use_container_width=True,
            ):
                switch_layout('doc_content', img_path, 'img')
    

    # st.write(col2_layout)

    # st.write(list_rois)
    if st.button('Back to Selection Images', use_container_width=True):
        switch_layout(target_content='selection_layout')

# Layout for Select Image to show
def select_img_layout():
    list_images = get_uploaded_images(PARA['SAVE_DIR'])
    num_uploaded_images = len(list_images)
    num_cols = num_uploaded_images if num_uploaded_images in [1, 2] else 3

    cols = st.columns(num_cols)
    # Create a bins for select image
    bins = np.linspace(0, num_uploaded_images - 1, num_cols + 1, dtype=int)
    bins[-1] = num_uploaded_images

    # Create the list of button to select image for each col
    img_per_cols = []
    for i, col in enumerate(cols):
        img_per_cols = list_images[bins[i]: bins[i+1]]
        for image_name in img_per_cols:
            if col.button(image_name, use_container_width=True):
                st.session_state.selected_img = image_name
                switch_layout(target_content='image_layout')

