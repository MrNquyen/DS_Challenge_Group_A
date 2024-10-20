# Import librabry
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch

import os
import json
import requests
import cv2
import time

# import ssl
# import urllib.request
# from urllib.request import Request, urlopen

from ultralytics import YOLO
from IPython.display import display, Image
from PIL import Image
from pathlib import Path

from utils import load_test_image, load_PARA

# Load model YOLO
def load_model(model_path):
    model = YOLO(f'{model_path}')
    return model


# Define YoloModel()
class YOLOModel():
    def __init__(self, PARA) -> None:
        self.PARA = PARA
        self.model = load_model(PARA['MODEL_PATH'])

    def getFileName(self, img_path: str, img_quality=['jpeg', 'png', 'jpg']):
        img_name = img_path.split('/')
        img_name = img_name[-1]
        for qual in img_quality:
            if qual in img_name:
                img_name = img_name.replace(f'.{qual}', '')
        return img_name


    def runPrediction(self, img_path):
        model = self.model

        pred = model(img_path)
        pred = pred[0]

        results = {}
        dic_result = {}
        ## Getting the prediction bbox results
        dic_result['cls'] = pred.boxes.cls             # classified label results
        dic_result['conf'] = pred.boxes.conf           # confident scores

        dic_result['label_names'] = [
            self.PARA['class_name'][i.item()] for i in pred.boxes.cls
        ]
        # dic_result['bboxes'] = pred.boxes.xywh
        dic_result['bboxes'] = pred.boxes.xyxyn
        dic_result['orig_shape'] = pred.orig_shape

        img_name = self.getFileName(img_path)

        # Assign to results['img_name']
        results[f'{img_name}'] = dic_result

        return results


    def detachROI(self, img_path):
        '''
            Tutorial: https://www.youtube.com/watch?v=NvtAYT1GIpg
        '''

        pred_results = self.runPrediction(img_path)
        
        img_name = self.getFileName(img_path)
        bboxes = pred_results[img_name]['bboxes']
        label_names = pred_results[img_name]['label_names']
        shape = pred_results[img_name]['orig_shape']

        # Create a directory for each image
        img_h, img_w = shape[0], shape[1]

        # Save a crop image using cv2
        list_cropped_image = []
        for i, (roi, label_name) in enumerate(zip(bboxes, label_names)):
            xA, yA, xB, yB = roi
            xA, yA, xB, yB = xA.item() , yA.item() , xB.item() , yB.item()

            x = round(img_w * xA)
            y = round(img_h * yA)
            w = round(img_w * (xB - xA))
            h = round(img_h * (yB - yA))

            image = cv2.imread(img_path)
            cropped_image = image[y:y+h, x:x+w]

            list_cropped_image.append(cropped_image)
        
        return list_cropped_image

def detachROI(PARA):
    model = YOLOModel(PARA)
    model.detachROI()