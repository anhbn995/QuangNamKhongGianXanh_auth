#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 4 19:42:36 2021

@author: ducanh
"""

import gdal
import glob, os
import rasterio
import numpy as np

import multiprocessing
from functools import partial
from multiprocessing.pool import Pool

LIST_VALUE_STRETCH = [  
    [1.0, 2177.0],
    [1.0, 2274.0],
    [1.0, 2197.0],
    [1.0, 3570.0]
    ]



"""
    Phan nay la chuan hoa 01 de predict cloud
"""
def write_image(data, height, width, numband, crs, tr, out):
    """
        Export numpy array to image by rasterio.
    """
    with rasterio.open(
                        out,
                        'w',
                        driver='GTiff',
                        height=height,
                        width=width,
                        count=numband,
                        dtype=data.dtype,
                        crs=crs,
                        transform=tr,
                        ) as dst:
                            dst.write(data)


def get_min_max_image(file_path):
    ds = gdal.Open(file_path,  gdal.GA_ReadOnly)
    numband =  ds.RasterCount
    dict_band_min_max = {1:0}
    for i in range(4):
        print(dict_band_min_max)
        band = ds.GetRasterBand(i + 1)
        min_train, max_train, _, _ = band.GetStatistics(True, True)
        dict_band_min_max.update({ i+1 : {"min": min_train, "max":max_train}})
    return dict_band_min_max, numband


def create_img_01(img_path, out_path):
    # get min max tat ca cac band va so band
    dict_min_max_full, numband = get_min_max_image(img_path)
    src = rasterio.open(img_path)
    img_float_01 = np.empty((numband, src.height, src.width))
    for i in range(numband):
        band = src.read(i+1)
        min_tmp = dict_min_max_full[i+1]['min']
        max_tmp = dict_min_max_full[i+1]['max']
        band = np.interp(band, (min_tmp, max_tmp), (0, 1))
        img_float_01[i] = band
    write_image(img_float_01, src.height, src.width, numband, src.crs, src.transform, out_path)


"""
    Phan nay la chuan hoa de co the view dep hon
"""
def create_list_id(path):
    list_image = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".tif"):
                list_image.append(os.path.join(root, file))
    return list_image


def cal_bancut(image_path,num_channel):
    dataset = gdal.Open(image_path)
    band_cut_th = {k: dict(max=0, min=0) for k in range(num_channel)}
    for i_chan in range(num_channel):
        values_ = dataset.GetRasterBand(i_chan+1).ReadAsArray().astype(np.float16)
        values_[values_==0] = np.nan
        band_cut_th[i_chan]['max'] = np.nanpercentile(values_, 98)
        band_cut_th[i_chan]['min'] = np.nanpercentile(values_, 2)
    return band_cut_th


def buil_3_band(image_path, out_dir_normalize_img, num_channel):
    image_name = os.path.basename(image_path)
    output_fp_tif = os.path.join(out_dir_normalize_img, image_name)

    band_cut_th = cal_bancut(image_path,num_channel)
    options_list = ['-ot UInt16','-a_nodata 0','-colorinterp_4 undefined']
    for i_chain in range(num_channel):
        options_list.append('-b {}'.format(i_chain+1))
    for i_chain, value in zip(range(num_channel),LIST_VALUE_STRETCH):
        options_list.append('-scale_{} {} {} {} {} -exponent_{} 1.0'.format(i_chain+1,band_cut_th[i_chain]['min'],band_cut_th[i_chain]['max'],value[0],value[1],i_chain+1))
    options_string = " ".join(options_list)
    gdal.Translate(output_fp_tif,
            image_path,
            options=options_string)
    return True


def norm_data_by_linh(dir_img, out_dir, num_channel):
    core = multiprocessing.cpu_count()//4
    list_id = create_list_id(dir_img)

    for image_path1 in list_id:
        dir_name = os.path.basename(os.path.dirname(image_path1))
        path_out = os.path.join(out_dir, dir_name)
        if not os.path.exists(path_out):
            os.makedirs(path_out)
            
    num_norm_data = len(glob.glob(os.path.join(path_out, '*.tif')))
    num_crop_data = len(list_id)
    if num_norm_data!=num_crop_data:
        p_cnt = Pool(processes=core)
        p_cnt.map(partial(buil_3_band, out_dir_normalize_img=path_out, num_channel=num_channel), list_id)
        p_cnt.close()
        p_cnt.join()
    return path_out

if __name__ == "__main__":
    dir_img = r"/home/skm/SKM_OLD/data_ml_mount/DucAnh/WORK/GreenCover_World/TayGiang_QuangNam/1_Image/2021/T2"
    out_dir = r"/home/skm/SKM/Tmp_xoa/xoa_luon"
    norm_data_by_linh(dir_img, out_dir, 4)