# Function 1.1 Check uploaded image
import streamlit as st
from pathlib import Path
import cv2
import numpy as np
import json
import os

from functions.crop_image import YOLOModel

from utils import getFileName, listROI, sanitize_file_name
from utils import removeDuplicate

# Function 1.1: check upload image
def U_checkUploadImage(upload_file,
                       upload_tab,
                       PARA):
    if upload_file is not None:
        upload_tab.write('Successfully Upload Image')
        # Save image input
        img_name = getFileName(upload_file.name)
        img_save_dir = Path(f'{PARA['SAVE_DIR']}/{img_name}')
        img_save_dir.mkdir(parents=True,
                           exist_ok=True)

        # Convert the uploaded file to a format cv2 can handle
        file_bytes = np.asarray(bytearray(upload_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Save file to local
        img_path = f'{str(img_save_dir)}/{img_name}.png'
        cv2.imwrite(filename=img_path,
                    img=image)
        
        # # Create a json file for image
        # img_dict = {}
        # with open(f'{img_save_dir}/{img_name}.json', 'w') as f:
        #     json.dump(img_dict, f, indent=6, ensure_ascii=False)

        st.write(img_save_dir)

        # Append to st.session_state.upload_img_name
        st.session_state.upload_img_name.append(img_name)

    else:
        st.write('You must upload the Image first !!')


# Function 1.2: Show image on the right
def U_showImage(PARA,
                visual_container,
                upload_file):
    '''
        upload_file: st.upload_file or np.array
    '''
    
    if upload_file is not None:
        file_name = getFileName(upload_file.name)
        img_save_path = PARA['SAVE_DIR'] + f'/{file_name}/{file_name}.png'
        visual_image = cv2.imread(img_save_path)
        if visual_image is None:
            visual_container.write('Load Image Failed !!')
            return
        visual_container.write('***THIS IS YOUR IMAGE***',)
        visual_container.image(visual_image)

# Function All: detach ROI
def detachROI(PARA, 
              upload_file):
    # Load YOLOModel
    if 'YOLOModel' not in st.session_state:
        st.session_state.YOLOModel = YOLOModel(PARA)

    # Load image path that need to detach ROI
    img_name = getFileName(upload_file.name) 
    img_path = PARA['SAVE_DIR'] + f'/{img_name}/{img_name}.png'

    # Load json_file
    img_json_path = PARA['SAVE_DIR'] + f'/{img_name}/{img_name}.json'
    # Create a json file for image
    img_json = {}

    # with open(img_json_path, 'r') as file:
    #     img_json = json.load(file)


    if 'list_rois' not in img_json.keys():
        # Load model
        model = st.session_state.YOLOModel
        
        # Detach ROI
        list_cropped_image = model.detachROI(img_path)

        # Save crop image
        # list_cropped_image = removeDuplicate(list_cropped_image)
        
        save_crop_dir = f'{PARA['SAVE_DIR']}/{PARA['CROP_DIR']}'

        roi_paths = []
        for i, cropped_image in enumerate(list_cropped_image):
            filename = f'{img_name}_{i}.png'
            roi_path = f'{save_crop_dir}/{filename}'

            success = cv2.imwrite(f'{str(roi_path)}', cropped_image)
            if not success:
                print(f'Failed to save {roi_path}')
            else:
                roi_paths.append(roi_path)

            # Create a ROI slide and add elements - thêm file mà user upload lên
            img_json[roi_path] = {
                'pdf': [],
                'vid': [],
                'img': []
            }

        # Save json_file
        img_json['list_rois'] = roi_paths
        with open(img_json_path, 'w') as file:
            json.dump(img_json, file, indent=6)
    

### Add layout: Save pdf, vid, image to local
def A_save_upload_file(file_contents: list, 
                       save_dir: str, 
                       file_type: str):
    save_file_paths = []
    exist_files = os.listdir(save_dir)
            
    
    if file_type=='pdf':
        for file_content in file_contents:
            file_name = sanitize_file_name(getFileName(file_content.name))
            save_file_path = f'{save_dir}/{file_name}.pdf'
            
            if f'{file_name}.pdf' not in exist_files:
                with open(save_file_path, 'wb') as file:
                    file.write(file_content.getvalue())
                    file.close()
            save_file_paths.append(save_file_path)
               
    
    elif file_type=='vid':
        # https://www.youtube.com/watch?v=2RLjY5Drvpw https://www.youtube.com/watch?v=oYbldfGTJ1o

        for file_content in file_contents.split():
            save_file_paths.append(file_content)
        return save_file_paths

    elif file_type=='img':
        for file_content in file_contents:
            file_name = getFileName(file_content.name)
            save_file_path = f'{save_dir}/{file_name}.png'
            if f'{file_name}.png' not in exist_files:
                print('Img Not In Saved')
                print(f'save_file_path: {save_file_path}, file_content: {file_content}')
                # Convert the uploaded file to a format cv2 can handle
                file_bytes = np.asarray(bytearray(file_content.read()), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

                # Save upload file
                save_ok = cv2.imwrite(save_file_path, image)
                print(f'Save_ok: {save_ok}')
            save_file_paths.append(save_file_path)

    return save_file_paths