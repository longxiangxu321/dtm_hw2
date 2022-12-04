#-- my_code_hw02.py
#-- hw02 GEO1015.2022
#-- [YOUR NAME]
#-- [YOUR STUDENT NUMBER] 

from datetime import datetime
from pytz import timezone
import suncalc #-- https://pypi.org/project/suncalc/
import pyproj
import math
import numpy
import rasterio
from rasterio import features


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





