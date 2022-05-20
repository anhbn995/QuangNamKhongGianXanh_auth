import numpy as np
import rasterio



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
                        nodata=0,
                        ) as dst:
                            dst.write(data)

def get_index_cloud_for_4band(path_mask_cloud):
    """
        get anotation cloud
    """
    src_mask = rasterio.open(path_mask_cloud)
    img_4band = np.empty((4, src_mask.height, src_mask.width))
    for i in range(4):
        img_4band[i] = src_mask.read(1)
    index_cloud = np.where(img_4band == 255)
    return index_cloud


def export_img_cloud_to_nodata(img_path, mask_cloud_path, out_path):
    """
        set cloud is nodata
    """
    # get index_cloud
    index_cloud = get_index_cloud_for_4band(mask_cloud_path)

    # Set nodata
    src = rasterio.open(img_path)
    img = src.read()
    img[index_cloud] = 0
    write_image(img, src.height, src.width, src.count, src.crs, src.transform, out_path)

