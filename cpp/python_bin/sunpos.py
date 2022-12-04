
import argparse
from datetime import datetime
from pytz import timezone
import suncalc #-- https://pypi.org/project/suncalc/
import pyproj



def main():
    parser = argparse.ArgumentParser(description='Get position (azimuth/altitude) of the sun')
    parser.add_argument('px', type=float, help='x-coord of p in ESPSG28992')
    parser.add_argument('py', type=float, help='y-coord of p in ESPSG28992')
    parser.add_argument('dt', type=str, help='ISO-formatted datetime, eg "2022-08-12 13:32"')
    args = parser.parse_args()

    #-- define the timezone for where Delft is located
    ams_tz = timezone('Europe/Amsterdam')
    #-- get the datetime object for a given local time at a given date
    dt = args.dt
    dto = ams_tz.localize(datetime.fromisoformat(dt))
    # print(dto) 
    #-- now let's get the time UTC time, which must be used with suncalc 
    #-- notice that this gives us either +01:00 in winter 
    #-- and +02:00 because of EU summer time the local time
    time_utc = dto.astimezone(timezone('UTC'))
    # print(time_utc)

    #-- convert from EPSG:28992 to EPSG:4326
    transfo = pyproj.Transformer.from_crs("EPSG:28992", "EPSG:4326")
    l = transfo.transform(args.px, args.py)
    # print(l)
    #-- get the position of the sun 
    #-- to interpret the results https://github.com/mourner/suncalc#sun-position
    #-- suncalc.get_position(datetime_in_utc, latitude, longitude)
    possun = suncalc.get_position(time_utc, l[0], l[1])
    # print(possun)
    print(possun["azimuth"], possun["altitude"])

if __name__ == '__main__':
    main()