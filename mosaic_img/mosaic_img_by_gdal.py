import os
import rasterio
from rasterio.merge import merge


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


def mosaic_gdal(list_fp, out_fp_mosaic):
    src_files_to_mosaic = []
    for fp in list_fp:
        src = rasterio.open(fp)
        src_files_to_mosaic.append(src)
    mosaic_, out_trans = merge(src_files_to_mosaic)
    write_image(mosaic_, mosaic_.shape[1], mosaic_.shape[2], mosaic_.shape[0], src.crs, out_trans, out_fp_mosaic)
