import ssl
import urllib.request
import os
import streamlit as st
import cv2
import json
import re

from urllib.request import Request, urlopen
from copy import deepcopy
from PIL import Image

from streamlit_dimensions import st_dimensions
from streamlit_pdf_viewer import pdf_viewer

def configImageInput():
    return {
        'type': ['jpeg', 'png', 'jpg'] 
    }


def getFileName(raw_name):
    img_qualities = ['png', 'jpeg', 'jpg', 'pdf']
    for qual in img_qualities:
        qual = f'.{qual}'
        while qual in raw_name:
            raw_name = raw_name.replace(qual, '')
            return raw_name


# Load PARAMETERS
def load_PARA():
    PARA = {
        'class_name': {
            0: 'Caption',
            1: 'Footnote',
            2: 'Formula',
            3: 'List-item',
            4: 'Page-footer',
            5: 'Page-header',
            6: 'Picture',
            7: 'Section-header',
            8: 'Table',
            9: 'Text',
            10: 'Title'
        },
        'SAVE_DIR': 'save',
        'CROP_DIR': 'crop',
        'MODEL_PATH': 'yolo-doclaynet.pt',
    }
    return PARA

# load test image
def load_test_image():
    # Set up SSL context to allow legacy TLS versions
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT

    url = 'https://image.infographics.vn/media//1200/2024/7/14/img_8510.jpeg'
    req = Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req, context=ctx)
    image_content = response.read()

    ## Write the content to a file
    filename = 'demo1Img.jpeg'
    with open(filename, "wb") as file:
        file.write(image_content)
        print(f"Download successfully filename {filename}")


def load_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        img_json = json.load(file)
        return img_json
    

def save_json(json_path, json_dict):
    with open(json_path, 'w', encoding='utf-8') as file:
    # with open(json_path, 'w') as file:
        json.dump(json_dict, file, indent=6, ensure_ascii=False)

# Count number of ROI
def listROI(PARA,
            img_name):
    img_json_path = f'{PARA['SAVE_DIR']}/{img_name}/{img_name}.json'
    # Load json file
    # json_file = load_json(img_json_path)
    json_file = load_json(img_json_path)
    # with open(img_json_path, 'r') as file:
    #     json_file = json.load(file)

    list_rois = json_file['list_rois']
    return list_rois
# Remove duplicate image

def checkSimilarImage(img1, img2):
    image1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    image2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    shape1 = image1.shape
    shape2 = image2.shape

    if abs(sum(shape1) - sum(shape1)) >= 5:
        return False
    
    kernal = (
        min([shape1[0], shape2[0]]),
        min([shape1[1], shape2[1]]),
    )

    first_loop = (shape1[0] - kernal[0] + 1) * (shape1[1] - kernal[1] + 1)
    second_loop = (shape2[0] - kernal[0] + 1) * (shape2[1] - kernal[1] + 1)

    w11, w12, h11, h12 = 0, deepcopy(kernal[0]), 0, deepcopy(kernal[1])
    w21, w22, h21, h22 = 0, deepcopy(kernal[0]), 0, deepcopy(kernal[1])
    for i in range(first_loop):
        if w12 + 1 >= shape1[0]:
            w11 = 0
            w12 = kernal[0]
            add1 = 1
            if h12 + 1 >= shape1[1]:
                add1 = 0
            h11 += add1
            h12 += add1
        else:
            w11 += 1
            w12 += 1

        window1 = image1[w11:w12, h11:h12]
        for j in range(second_loop):
            if w22 + 1 >= shape2[0]:
                w21 = 0
                w22 = kernal[0]
                add2 = 1
                if h22 + 1 >= shape2[1]:
                    add2 = 0
                h21 += add2
                h22 += add2
            else:
                w21 += 1
                w22 += 1
            window2 = image2[w21:w22, h21:h22]

            if (window1 == window2).all():
                return True
    return False

def removeDuplicate(list_img):
    unique_list = []
    
    for arr in list_img:
        if all(not checkSimilarImage(uni, arr) for uni in unique_list):
            unique_list.append(arr)
    
    return unique_list

# Streamlit Upload image()
def st_upload_image(streamlit_layout,
                    accept_multiple_files,
                    key):
    uploaded_file = streamlit_layout.file_uploader(
        label='Enter Your Image',
        type=['png', 'jpeg', 'jpg'],
        accept_multiple_files=accept_multiple_files,
        key=key
    )
    return uploaded_file


# Streamlit upload pdf()
def st_upload_pdf(streamlit_layout,
                  accept_multiple_files,
                  key):
    uploaded_file = streamlit_layout.file_uploader(
        label='Enter Your PDF File',
        type=['pdf'],
        accept_multiple_files=accept_multiple_files,
        key=key
    )
    return uploaded_file


# Streamlit upload video
def st_upload_video_link(streamlit_layout,
                        #  label,
                        #  type,
                        #  accept_multiple_files,
                        key):
    text_input = streamlit_layout.text_input(
        label="Enter Video URL",
        label_visibility='visible',
        disabled=False,
        placeholder='Enter Video URL',
        key=key
    )
    return text_input

# Remove any characters that are not valid for file names (such as special Unicode characters)
def sanitize_file_name(file_name):
    return re.sub(r'[^\w\s-]', '', file_name).strip()

# Count number of uploaded images
def get_uploaded_images(save_dir):
    list_non_image_folders = ['crop', 'upload_img', 'upload_pdf', 'upload_vid']
    list_folders = os.listdir(f'{save_dir}')
    for folder in list_non_image_folders:
        list_folders.remove(folder)
    return list_folders


# Show pdf
def show_pdf(input, key):
    pdf_viewer(
        input=input,
        key=key
    )

# Show vid
def show_vid(url):
    st.video(
        url
    )

# Show Image
def show_img(path):
    image = Image.open(path)
    st.image(image)

# Insert Number
def insert_number(title='Insert a number'):
    # Set the minimum value to 2 to restrict input greater than 1
    number = st.number_input(
        title, 
        value=2, 
        min_value=2
    )
    
    # Return the absolute, rounded integer value
    number = abs(int(round(number)))
    return number

# preprocessing text
def preprocess_text(text):
    # Step 1: Remove markdown symbols (** for bold, \n for newlines)
    text = text.replace('*', '')
    text = text.replace('#', '')
    
    # Step 2: Normalize multiple spaces to a single space
    text = re.sub(' +', ' ', text).strip()  # Replace multiple spaces with a single space and strip leading/trailing spaces
    
    return text