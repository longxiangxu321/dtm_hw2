import sys
from datetime import datetime
from pytz import timezone
import suncalc  # -- https://pypi.org/project/suncalc/
import pyproj
import math
import numpy as np
import rasterio
from rasterio import features
import time

def is_sunny(dataset, px, py, dt):
    data = dataset.read(1)
    row, col = dataset.index(px, py)
    try:
        val = data[row][col]
    except Exception:
        raise Exception("Outside of the bounding box")
    if val == dataset.nodatavals:
        raise Exception("No data value for input point")

    px, py = dataset.xy(row, col)[0], dataset.xy(row,col)[1]
    ams_tz = timezone('Europe/Amsterdam')
    dto = ams_tz.localize(datetime.fromisoformat(dt))
    time_utc = dto.astimezone(timezone('UTC'))
    # breakpoint()
    transfo = pyproj.Transformer.from_crs("EPSG:28992", "EPSG:4326")
    lat, long = transfo.transform(px, py)  # return tuple
    possun = suncalc.get_position(time_utc, lat= lat, lng= long)  # return object sun with altitude and azimuth
    az, al = possun['azimuth'], possun['altitude']
    resolution = (dataset.bounds.top - dataset.bounds.bottom) / dataset.height
    left = dataset.bounds.left + resolution/2
    right = dataset.bounds.right - resolution/2
    top = dataset.bounds.top - resolution/2
    bottom = dataset.bounds.bottom + resolution/2
    if az == math.pi / 2:
        sun_r = left, py
    elif az == - (math.pi / 2):
        sun_r = right, py
    else:
        llx, lly = left, bottom
        ulx, uly = left, top
        urx, ury = right, top
        lrx, lry = right, bottom

        ll_a = math.atan((llx - px) / (lly - py))
        ul_a = math.atan((ulx - px) / (uly - py)) + math.pi
        ur_a = math.atan((urx - px) / (ury - py)) - math.pi
        lr_a = math.atan((lrx - px) / (lry - py))

        # breakpoint()
        if ll_a < az <= ul_a:
            sun_r = llx,  (llx - px) / math.tan(az) + py
        elif az > ul_a or az <= ur_a:
            sun_r = (uly - py) * math.tan(az) + px, uly
        elif ur_a < az <= lr_a:
            sun_r = urx, (urx - px) / math.tan(az) + py
        elif lr_a < az <= ll_a:
            sun_r = (lly - py) * math.tan(az) + px, lly

    v = {}
    in_pt = px, py
    v["type"] = "LineString"
    v["coordinates"] = []
    v["coordinates"].append((sun_r[0], sun_r[1]))
    v["coordinates"].append((in_pt[0], in_pt[1]))
    # v["coordinates"].append(dataset.xy(sun_r[0], sun_r[1]))
    # v["coordinates"].append(dataset.xy(in_pt[0], in_pt[1]))
    shapes = [(v, 1)]
    re = features.rasterize(shapes,
                            out_shape=dataset.shape,
                            all_touched=True,
                            transform=dataset.transform)
    LoS = np.multiply(re, data)
    sun_row, sun_col = dataset.index(sun_r[0], sun_r[1])
    dist = math.dist(dataset.xy(row, col),dataset.xy(sun_row, sun_col))
    sun_h = dist * math.tan(al) + data[row][col]
    LoS_filtered = np.where(LoS != dataset.nodatavals[0], LoS, -999)
    idx = np.where(re == 1)

    true_height = []
    for i in range(len(idx[0])):
        true_height.append(LoS_filtered[idx[0][i]][idx[1][i]])
    true_height = np.array(true_height)
    distance = np.sqrt(((idx[0] - row) * resolution) ** 2 + ((idx[1] - col) * resolution) ** 2)
    height_threshold = distance * np.tan(al) + data[row][col]
    comparison_result = height_threshold - true_height
    if data[row][col] <= sun_h:
        return np.min(comparison_result) >= 0
    else:
        return np.max(comparison_result) < 0
    # to compare if all true_height < threshold


def main():
    # -- this gives you a Rasterio dataset
    # -- https://rasterio.readthedocs.io/en/latest/quickstart.html
    d = rasterio.open('../ahn3_data/ahn3_dsm50cm_bk_small.tif')
    px, py, dt = 85221.213, 446869.490, '2022-11-30 12:40'
    start_time = time.time()
    re = is_sunny(d, px, py, dt)
    end_time = time.time()

    runtime = end_time - start_time

    print("The runtime of the project is: ", runtime, "seconds")
    print("YES it's sunny 😎") if re == True else print("NO it's not sunny 🔦")


main()
