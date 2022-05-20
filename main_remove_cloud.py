import os
import tensorflow as tf

from create_img_no_cloud import export_img_cloud_to_nodata
from ultils.ultil import print_note, get_name_file_from_dir
from normalize_data.percentile_data import create_img_01
from predict_cloud.predict_cloud import main_cloud_detect
from mosaic_img import mosaic_img_by_gdal
from crop_image_by_aoi.crop_img_by_aoi import main_crop_aoi 


def normalize_and_predict_cloud_from_dir(dir_img, out_dir_img, cnn_model):
    print_note(f'Bat dau chuan hoa 01 folder {os.path.basename(dir_img)}')
    out_dir_img_01_tmp = os.path.join(out_dir_img, 'tmp_01')
    list_name = get_name_file_from_dir(dir_img)

    if not os.path.exists(out_dir_img_01_tmp):
        os.makedirs(out_dir_img_01_tmp)
        if list_name:
            for name in list_name:
                print(name)
                fp_in =  os.path.join(dir_img, name + '.tif')
                fp_out = os.path.join(out_dir_img_01_tmp, name + '.tif')
                try:
                    create_img_01(fp_in, fp_out)
                except:
                    continue
        else:
            print_note(f'khong co anh trong {dir_img}')
    else:
        print_note(f'da chuan hoa tu truoc check folder: {os.path.basename(dir_img)}')
    

    print_note(f"Bat dau predict cloud folder {os.path.basename(dir_img)}")
    out_dir_cloud_mask = os.path.join(out_dir_img, 'tmp_cloud_mask')
    if not os.path.exists(out_dir_cloud_mask):
        os.makedirs(out_dir_cloud_mask)
    if list_name:
        for name in list_name:
            print(name)
            fp_in = os.path.join(out_dir_img_01_tmp, name + '.tif')
            fp_out = os.path.join(out_dir_cloud_mask, name + '.tif')
            main_cloud_detect(fp_in, cnn_model, fp_out)


    print_note(f"Bat dau xoa cloud cua anh goc folder {os.path.basename(dir_img)}")
    if list_name:
        for name in list_name:
            print(name)
            fp_in_img = os.path.join(dir_img, name + '.tif')
            fp_in_mask = os.path.join(out_dir_cloud_mask, name + '.tif')
            fp_out_rm = os.path.join(out_dir_img, name + '.tif')
            export_img_cloud_to_nodata(fp_in_img, fp_in_mask, fp_out_rm)



if __name__ =='__main__':
    list_nam = [2019,2020,2021,2022]
    fp_model = r'/home/skm/SKM_OLD/npark/greencover_api/weights/cloud_weights_cocautruc.h5'
    fp_shapefile = r"/home/skm/SKM_OLD/data_ml_mount/DucAnh/WORK/GreenCover_World/TayGiang_QuangNam/AOI/TayGiang_QuangNam.shp"
    in_dir_img_download =  r"/home/skm/SKM_OLD/data_ml_mount/DucAnh/WORK/GreenCover_World/TayGiang_QuangNam/1_Image"
    dir_img_cut = r"/home/skm/SKM/WORK/QuangNam_KhongGianXanh/2_img_cut"
    dir_predict_remove = r"/home/skm/SKM/WORK/QuangNam_KhongGianXanh/3_predict_remove_morphology"
    cnn_model = tf.keras.models.load_model(fp_model, custom_objects=None, compile=False)
    
    
    print_note('Bat dau cat anh')
    for nam in list_nam:
        dir_img_download = os.path.join(in_dir_img_download, str(nam))
        list_folder_in_folder_nam =  os.listdir(dir_img_download)
        print(list_folder_in_folder_nam)
        for name_folder in list_folder_in_folder_nam:
            dir_folder_img = os.path.join(dir_img_download, name_folder)
            out_dir_cut = os.path.join(dir_img_cut, str(nam), name_folder)
            if not os.path.exists(dir_folder_img):
                os.makedirs(dir_folder_img)
            main_crop_aoi(dir_folder_img, fp_shapefile, out_dir_cut)


    for nam in list_nam:
        """create folder thang"""
        dir_img = os.path.join(dir_img_cut, str(nam))
        list_folder_in =  os.listdir(dir_img) 
        print(list_folder_in)
        for month in list_folder_in:
            in_dir_img = os.path.join(dir_img, month)
            out_dir_img = os.path.join(dir_predict_remove, os.path.basename(dir_img), month)
            if not os.path.exists(out_dir_img):
                os.makedirs(out_dir_img)
            normalize_and_predict_cloud_from_dir(in_dir_img, out_dir_img, cnn_model)
        


