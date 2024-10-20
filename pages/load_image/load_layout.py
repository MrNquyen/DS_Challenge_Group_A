# Import pakage
import streamlit as st
import numpy as np
import pandas as pd
import json
import os
import joblib
import cv2

from PIL import Image
from utils import configImageInput, load_PARA, listROI, getFileName, load_json

from layouts.upload_image.layout import upload_tab_layout, add_tab_layout, documents_tab_layout, QA_layout

from functions.upload_image.function import U_checkUploadImage, U_showImage 
from functions.upload_image.function import detachROI
# Setup Input config
INPUT_CONFIG = configImageInput()

def load_layout_setup(PARA):
    layout_dict = {}
    ### Create a title for the web
    st.title('Wonderful Infographic')
    upload_tab, add_tab, documents_tab, qa_tab = st.tabs([
        'Upload', 
        'Add', 
        'Related Documents', 
        'QA'
    ])

    layout_dict['upload_tab'] = upload_tab
    layout_dict['add_tab'] = add_tab
    layout_dict['documents_tab'] = documents_tab
    layout_dict['qa_tab'] = qa_tab

    return layout_dict


def load_show_layout(PARA): 
    layout_dict = load_layout_setup(PARA)

    # Tab object
    upload_tab = layout_dict['upload_tab']
    add_tab = layout_dict['add_tab']
    documents_tab = layout_dict['documents_tab']
    qa_tab = layout_dict['qa_tab']

    ### Setup Upload layput
    upload_tab_layout(PARA=PARA,
                      upload_tab=upload_tab,
                      layout_dict=layout_dict)
    
    # Upload tab function
    upload_file = layout_dict['uploaded_file']
    visual_container = layout_dict['visual_container']

    # Function 1.1: check upload image
    U_checkUploadImage(upload_file,
                       upload_tab,
                       PARA)

    # Function 1.2: Show image on the right
    if upload_file is not None:
        U_showImage(PARA,
                    visual_container,
                    upload_file)
    
    # Function 2: Detach ROI (Crop image module)
    if upload_file is not None:
        filename = getFileName(upload_file.name)
        img_dir = f'{PARA['SAVE_DIR']}/{filename}'
        json_name = f'{filename}.json'
        if json_name not in os.listdir(img_dir):
            detachROI(PARA, upload_file)

    ## Setup add layout
    if upload_file is not None:
        add_tab_layout(
            upload_file=upload_file,
            PARA=PARA,
            add_tab=add_tab
        )

    ## Setup documents layout
    if upload_file is not None:
        documents_tab_layout(
            upload_file=upload_file,
            PARA=PARA,
            documents_tab=documents_tab
        )

    ## QA Layout
    if upload_file is not None:
        filename = getFileName(upload_file.name)
        img_path = f'{PARA['SAVE_DIR']}/{filename}/{filename}.png'
        QA_layout(
            PARA=PARA,
            streamlit_col=qa_tab,
            img_path=img_path,
        )
    
        
# Main
def main():
    PARA = load_PARA()
    st.set_page_config(layout='wide')
    load_show_layout(PARA)