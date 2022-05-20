import os
import cv2
import gdal
import numpy as np
from tqdm import tqdm

import warnings
warnings.filterwarnings("ignore")

from classification_class.utils import get_img_coords, write_results, padded_for_org_img, \
                                convert_value_obj, get_im_by_coord


def predict(model, values, img_coords, num_band, h, w, padding, crop_size, 
            input_size, batch_size, thresh_hold):
    cut_imgs = []
    for i in range(len(img_coords)):
        im = get_im_by_coord(values, img_coords[i][0], img_coords[i][1],
                            num_band,padding, crop_size, input_size)
        cut_imgs.append(im)

    a = list(range(0, len(cut_imgs), batch_size))

    if a[len(a)-1] != len(cut_imgs):
        a[len(a)-1] = len(cut_imgs)

    y_pred = []
    for i in tqdm(range(len(a)-1)):
        x_batch = []
        x_batch = np.array(cut_imgs[a[i]:a[i+1]])
        y_batch = model.predict(x_batch)
        y_pred.extend(y_batch)
    big_mask = np.zeros((h, w)).astype(np.float16)
    for i in range(len(cut_imgs)):
        true_mask = y_pred[i].reshape((input_size,input_size))
        true_mask = (true_mask>thresh_hold).astype(np.uint8)
        true_mask = (cv2.resize(true_mask,(input_size, input_size), interpolation = cv2.INTER_CUBIC)>thresh_hold).astype(np.uint8)
        start_x = img_coords[i][1]
        start_y = img_coords[i][0]
        big_mask[start_x-padding:start_x-padding+crop_size, start_y-padding:start_y -
                    padding+crop_size] = true_mask[padding:padding+crop_size, padding:padding+crop_size]
    del cut_imgs
    return big_mask



def predict_green(image_path, weight_path, result_path, model, input_size_green, dil, 
        crop_size=100, batch_size=2, thresh_hold=0.15):
    print("*Init green model")
    model.load_weights(weight_path)

    print("*Predict image")
    thresh_hold = 1 - thresh_hold
    num_band = input_size_green[-1]
    input_size = input_size_green[0]
    
    dataset = gdal.Open(image_path)
    values = dataset.ReadAsArray()[0:num_band]
    h,w = values.shape[1:3]    
    padding = int((input_size - crop_size)/2)
    
    img_coords = get_img_coords(w, h, padding, crop_size)
    values = padded_for_org_img(values, num_band, padding)
    big_mask = predict(model, values, img_coords, num_band, h, w, padding, crop_size, 
                        input_size, batch_size, thresh_hold)

    mask_base = convert_value_obj(big_mask)
    
    if dil:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        mask_base = cv2.dilate(mask_base,kernel,iterations = 1)
    else:
        mask_base = mask_base

    write_results(mask_base, image_path, result_path)
    return mask_base

