import streamlit as st
import sys
from pathlib import Path
import json

from utils import load_PARA
from functions.retrieval import load_model
sys.path.append('F:\\UNIVERSITY\\DS_CHALLENGE\\streamlit_v2')

# Global variables
PARA = load_PARA()
st.session_state.upload_img_name = []

# Load model for generating external_knowledge
load_model(model_name='gemini-1.5-flash')

# Create save directory of cropped images
save_crop = Path(f'{PARA['SAVE_DIR']}/{PARA['CROP_DIR']}')
save_crop.mkdir(parents=True,
                exist_ok=True)

# Create save upload file by user (pdf, vid, img)
save_pdf = Path(f'{PARA['SAVE_DIR']}/upload_pdf')
save_vid = Path(f'{PARA['SAVE_DIR']}/upload_vid')
save_img = Path(f'{PARA['SAVE_DIR']}/upload_img')

save_pdf.mkdir(parents=True,
               exist_ok=True)

vid_dic = {}
save_vid.mkdir(parents=True,
               exist_ok=True)
with open(f'{save_vid}/vid_upload.json', 'w') as file:
    json.dump(vid_dic, file, ensure_ascii=True, indent=True)

save_img.mkdir(parents=True,
               exist_ok=True)

# Setting pages
pages = {
    "Upload Image": [
        st.Page("pages/load_image/run_load_layout.py", title="Upload Your Image"),

    ],
    "Select Image": [
        st.Page("pages/select_image/run_select_image.py", title="Choose Your Upload Image")
    ],
}

pg = st.navigation(pages)
pg.run()