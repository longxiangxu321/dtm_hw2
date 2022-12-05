#-- my_code_hw02.py
#-- hw02 GEO1015.2022
#-- [Longxiang Xu]
#-- [5722918]

from datetime import datetime
from pytz import timezone
import suncalc #-- https://pypi.org/project/suncalc/
import pyproj
import math
import numpy
import rasterio
from rasterio import features

# Image is read to a dataset object
# query xy to check if it is inside the dataset.bounds, if not, raise exception
# query xy and get its height value, if it equals dataset.nodatavals, raise exception
# use suncalc to obtain the altitude and azimuth of the sun
# Obtain the azimuth of the four bounding box point
# ll, ul, ur, lr, if the azimuth of the sun is between the azimuth of ll and ul,
# then the point representing the sun will be on the left bounding box edge
# (y - py) / (x - px) = tan(az), according to this function obtain the point represent the sun
# burn the point(x,y) and (px,py), obtain the output np array
# according to the image np array and the line of sight array, determine whether sun shines here

def is_sunny(dataset, px, py, dt):
    """
    !!! TO BE COMPLETED !!!
     
    Does the sun shine there at that moment?
     
    Input:
        dataset: the rasterio input dataset
        px:  x-coordinate of p
        py:  y-coordinate of p
        dt:  ISO-formatted datetime ('YYYY-MM-DD HH:MM'), eg '2022-08-12 13:32'
    Output:
        True/False: True = ground is illuminated; False = ground is not illuminated
           (raise Exception if p is outside the extent of the dataset)
           (raise Exception if p is no_data value)
    """
    # raise Exception("Point given is outside the extent of the dataset")
    # raise Exception("Point given has no_data value")
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
            sun_r = llx, (llx - px) / math.tan(az) + py
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


def some_code_to_help_with_rasterio(dataset, px, py, dt):
    """
    !!! USE THIS CODE !!!
     
    Example code that can be useful: use it for your function, 
    copy part of it, it's allowed.
    """
    #-- numpy of input
    n1  = dataset.read(1)
    #-- index of p in the numpy raster
    row, col = dataset.index(px, py)
    #-- an empty array with all values=0
    n2 = numpy.zeros(dataset.shape, dtype=numpy.int8)
    for i in range(n1.shape[0]):
        for j in range(n1.shape[1]):
            z = n1[i][j]
            if z == dataset.nodatavals:
                n2[i][j] = 50
    #-- put p with value=99
    n2[row , col] = 99
    #-- write this to disk
    output_file = 'testing.tiff'
    with rasterio.open(output_file, 'w', 
                       driver='GTiff', 
                       height=n2.shape[0],
                       width=n2.shape[1], 
                       count=1, 
                       dtype=rasterio.uint8,
                       crs=dataset.crs, 
                       transform=dataset.transform) as dst:
        dst.write(n2.astype(rasterio.uint8), 1)
    print("File written to '%s'" % output_file)




def some_code_to_help_with_suncalc():
    """
    !!! USE THIS CODE !!!
     
    Example code that can be useful: use it for your function, 
    copy part of it, it's allowed.
    """
    #-- define the timezone for where Delft is located
    ams_tz = timezone('Europe/Amsterdam')
    #-- get the datetime object for a given local time at a given date
    dt = '2022-11-12 13:37'
    dto = ams_tz.localize(datetime.fromisoformat(dt))
    print(dto) 
    #-- now let's get the time UTC time, which must be used with suncalc 
    #-- notice that this gives us either +01:00 in winter 
    #-- and +02:00 because of EU summer time the local time
    time_utc = dto.astimezone(timezone('UTC'))
    print(time_utc)

    #-- get the position of the sun 
    #-- to interpret the results https://github.com/mourner/suncalc#sun-position
    #-- suncalc.get_position(datetime_in_utc, latitude, longitude)
    possun = suncalc.get_position(time_utc, 4.0, 52.0)
    print(possun)

    #-- convert from EPSG:28992 to EPSG:4326
    transfo = pyproj.Transformer.from_crs("EPSG:28992", "EPSG:4326")
    l = transfo.transform(81687.0, 447480.0)
    print(l)


def bresenham_with_rasterio():
    """
    !!! USE THIS CODE !!!
     
    Example code that can be useful: use it for your function, 
    copy part of it, it's allowed.
    """
    #-- https://rasterio.readthedocs.io/en/latest/topics/features.html#burning-shapes-into-a-raster
    # d = rasterio dataset as read in geo1015_hw02.py
    a = (10, 10)
    b = (100, 50)
    #-- create in-memory a simple GeoJSON LineString
    v = {}
    v["type"] = "LineString"
    v["coordinates"] = []
    v["coordinates"].append(d.xy(a[0], a[1]))
    v["coordinates"].append(d.xy(b[0], b[1]))
    shapes = [(v, 1)]
    re = features.rasterize(shapes, 
                            out_shape=d.shape, 
                            # all_touched=True,
                            transform=d.transform)
    # re is a numpy with d.shape where the line is rasterised (values != 0)





