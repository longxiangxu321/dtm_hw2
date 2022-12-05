import sys
from datetime import datetime
from pytz import timezone
import suncalc  # -- https://pypi.org/project/suncalc/
import pyproj
import math
import numpy as np
import rasterio
from rasterio import features


def is_sunny(dataset, px, py, dt):
    data = dataset.read(1)
    row, col = dataset.index(px, py)
    try:
        val = data[row][col]
    except Exception:
        raise Exception("Outside of the bounding box")
    if val == dataset.nodatavals:
        raise Exception("No data value for input point")

    ams_tz = timezone('Europe/Amsterdam')
    dto = ams_tz.localize(datetime.fromisoformat(dt))
    time_utc = dto.astimezone(timezone('UTC'))

    transfo = pyproj.Transformer.from_crs("EPSG:28992", "EPSG:4326")
    x0, y0 = transfo.transform(px, py)  # return tuple
    possun = suncalc.get_position(time_utc, x0, y0)  # return object sun with altitude and azimuth
    az, al = possun['azimuth'], possun['altitude']
    # (y - py) / (x - px) = tan(az)
    if az == math.pi / 2:
        sun_r = dataset.bounds.left, py
    elif az == 1.5 * math.pi:
        sun_r = dataset.bounds.right, py
    else:
        llx, lly = dataset.bounds.left, dataset.bounds.bottom
        ulx, uly = dataset.bounds.left, dataset.bounds.top
        urx, ury = dataset.bounds.right, dataset.bounds.top
        lrx, lry = dataset.bounds.right, dataset.bounds.bottom

        ll_a = math.atan((lly - py) / (llx - px))
        ul_a = math.atan((uly - py) / (ulx - px)) + math.pi
        ur_a = math.atan((ury - py) / (urx - px)) + math.pi
        lr_a = math.atan((lry - py) / (lrx - px)) + math.pi * 2

        if ll_a < az <= ul_a:
            sun_r = llx,  (llx - px) / math.tan(az) + py
        elif ul_a < az <= ur_a:
            sun_r = (uly - py) * math.tan(az) + px, uly
        elif ur_a < az <= lr_a:
            sun_r = urx, (urx - px) / math.tan(az) + py
        elif (0 <= az <= ll_a) or lr_a <= az <= math.pi * 2:
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
    # breakpoint()
    sun_h = data[sun_row, sun_col]
    LoS_filtered = np.where(LoS != dataset.nodatavals[0], LoS, -999)
    max_surface = np.max(LoS_filtered)
    if max_surface >= sun_h:
        return False
    else:
        return True


def main():
    # -- this gives you a Rasterio dataset
    # -- https://rasterio.readthedocs.io/en/latest/quickstart.html
    d = rasterio.open('../ahn3_data/ahn3_dsm50cm_bk_small.tif')
    px, py, dt = 85300, 446900, '2022-11-30 11:46'
    re = is_sunny(d, px, py, dt)
    print("YES it's sunny 😎") if re == True else print("NO it's not sunny 🔦")


main()
