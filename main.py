import os

from ultils import get_name_file_from_dir, print_note

from crop_image_by_aoi.crop_img_by_aoi import main_crop_aoi


def crop_image_and_normalize(dir_img, fp_aoi, base_img, out_dir_cut):
    list_names = get_name_file_from_dir(dir_img)

    print_note(f'Bat dau cat {dir_img} and normalize')
    """out_dir_cut_cut_aoi chinh la folder out_dir_cut them '_cut'"""
    dir_name = os.path.basename(os.path.dirname(dir_img))
    out_dir_cut_aoi = main_crop_aoi(dir_img, fp_aoi, out_dir_cut)





if __name__ == "__main__":

    dir_img = r"/home/skm/SKM_OLD/data_ml_mount/DucAnh/WORK/GreenCover_World/TayGiang_QuangNam/1_Image/2021/T2"
    fp_aoi = r"/home/skm/SKM_OLD/public/Cuong/TayGiang_QuangNam.shp"
    base_img = None
    out_dir_cut = r"/home/skm/SKM/Tmp_xoa/xoa_luon"
    crop_image_and_normalize(dir_img, fp_aoi, base_img, out_dir_cut)

    


