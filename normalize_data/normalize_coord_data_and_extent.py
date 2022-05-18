import os
import glob
import rasterio
import numpy as np

from osgeo import gdal
from rasterio.warp import reproject, Resampling


def reproject_image(src_path, dst_path, dst_crs='EPSG:4326'):
    with rasterio.open(src_path) as ds:
        nodata = ds.nodata or 0
    temp_path = dst_path.replace('.tif', 'temp.tif')
    option = gdal.TranslateOptions(gdal.ParseCommandLine("-co \"TFW=YES\""))
    gdal.Translate(temp_path, src_path, options=option)
    option = gdal.WarpOptions(gdal.ParseCommandLine("-t_srs {} -dstnodata {}".format(dst_crs, nodata)))
    gdal.Warp(dst_path, temp_path, options=option)
    os.remove(temp_path)
    return True


def window_from_extent(xmin, xmax, ymin, ymax, aff):
        col_start, row_start = ~aff * (xmin, ymax)
        col_stop, row_stop = ~aff * (xmax, ymin)
        return ((int(row_start), int(row_stop)), (int(col_start), int(col_stop)))


def convert_profile(src_path, dst_path, out_path):
    _info = gdal.Info(dst_path, format='json')
    xmin, ymin = _info['cornerCoordinates']['lowerLeft']
    xmax, ymax = _info['cornerCoordinates']['upperRight']

    with rasterio.open(dst_path) as dst:
        dst_transform = dst.transform
        kwargs = dst.meta
        kwargs['transform'] = dst_transform
        dst_crs = dst.crs
    with rasterio.open(src_path) as src:
        window = window_from_extent(xmin, xmax, ymin, ymax, src.transform)
        src_transform = src.window_transform(window)
        data = src.read()

        with rasterio.open(out_path, 'w', **kwargs) as dst:
            for i, _ in enumerate(data, 1):
                _band = src.read(i, window=window)
                dest = np.zeros_like(_band) 
                reproject(
                    _band, dest,
                    src_transform=src_transform,
                    src_crs=src.crs,
                    dst_transform=src_transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)
                dst.write(dest, indexes=i)