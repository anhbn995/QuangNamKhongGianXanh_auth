import glob, os
from multiprocessing.pool import Pool
from functools import partial
import multiprocessing
import shutil
import rasterio
import rasterio.mask
import geopandas as gp

def cut(img_name, img_dir, fp_shapefile, img_cut_dir):
    image_path = os.path.join(img_dir,img_name+'.tif')
    with rasterio.open(image_path, mode='r+') as src:
        projstr = src.crs.to_string()
        check_epsg = src.crs.is_epsg_code
        if check_epsg:
            epsg_code = src.crs.to_epsg()
        else:
            epsg_code = None
    if epsg_code:
        out_crs = {'init':'epsg:{}'.format(epsg_code)}
    else:
        out_crs = projstr
    bound_shp = gp.read_file(fp_shapefile)
    bound_shp = bound_shp.to_crs(out_crs)

    for index2, row_bound in bound_shp.iterrows():
        geoms = row_bound.geometry
        img_cut = img_name+"_{}.tif".format(index2)
        img_cut_path = os.path.join(img_cut_dir, img_cut)
        try:
            if not os.path.exists(img_cut_path):
                with rasterio.open(image_path,BIGTIFF='YES') as src:
                    out_image, out_transform = rasterio.mask.mask(src, [geoms], crop=True)
                    out_meta = src.meta
                out_meta.update({"driver": "GTiff",
                        "height": out_image.shape[1],
                        "width": out_image.shape[2],
                        "transform": out_transform})
                with rasterio.open(img_cut_path, "w", **out_meta) as dest:
                    dest.write(out_image)
        except :
            pass

def create_list_id(path):
    list_id = []
    os.chdir(path)
    for file in glob.glob("*.tif"):
        list_id.append(file[:-4])
    return list_id

def main_crop_aoi(dir_img, fp_shapefile, out_dir): 
    core = multiprocessing.cpu_count()//4
    img_list = create_list_id(dir_img)

    # img_cut_dir = os.path.join(out_dir,'cut')
    img_cut_dir = out_dir
    # print("Run crop image with aoi ...")  
    if not os.path.exists(img_cut_dir):
        os.makedirs(img_cut_dir)    
    p_cnt = Pool(processes=core)    
    p_cnt.map(partial(cut,img_dir=dir_img, fp_shapefile=fp_shapefile, img_cut_dir=img_cut_dir), img_list)
    p_cnt.close()
    p_cnt.join()    
    # print("Done")
    return img_cut_dir


if __name__ == '__main__':
    dir_img =  r"/home/skm/SKM_OLD/data_ml_mount/DucAnh/WORK/GreenCover_World/TayGiang_QuangNam/1_Image/2021"
    fp_shapefile = r"/home/skm/SKM_OLD/data_ml_mount/DucAnh/WORK/GreenCover_World/TayGiang_QuangNam/AOI/TayGiang_QuangNam.shp"
    out_dir_cut = "/home/skm/SKM/WORK/QuangNam_KhongGianXanh/2_img_cut/2021"
    for i in range(1,13):
        name_folder = f"T{i}"
        dir_run = os.path.join(dir_img, name_folder)
        print(dir_run)
        out_dir = os.path.join(out_dir_cut, name_folder)
        main_crop_aoi(dir_run, fp_shapefile, out_dir)


