#-- geo1015_hw02.py
#-- Assignment 02 GEO1015.2022
#-- 2022-11-29

#------------------------------------------------------------------------------
# DO NOT MODIFY THIS FILE!!!
#------------------------------------------------------------------------------
# pip install suncalc 
# pip install pytz
# pip install pyproj
#------------------------------------------------------------------------------

import sys
import rasterio
import argparse

import my_code_hw02

def main():
    parser = argparse.ArgumentParser(description='Performs line-of-sight queries')
    parser.add_argument('inputfile', help='a GDAL-readable raster terrain')
    parser.add_argument('px', type=float, help='x-coord of a')
    parser.add_argument('py', type=float, help='y-coord of a')
    parser.add_argument('dt', type=str, help='ISO-formatted datetime, eg "2022-08-12 13:32"')
    args = parser.parse_args()

    #-- load in memory the input grid
    try:
        #-- this gives you a Rasterio dataset
        #-- https://rasterio.readthedocs.io/en/latest/quickstart.html
        d = rasterio.open(args.inputfile)
    except Exception as e:
        print(e)
        sys.exit()
    
    try:
        re = my_code_hw02.is_sunny(d, args.px, args.py, args.dt)
        print("YES it's sunny 😎") if re == True else print("NO it's not sunny 🔦")
    except Exception as e:
        print(e)
        sys.exit()

if __name__ == '__main__':
    main()