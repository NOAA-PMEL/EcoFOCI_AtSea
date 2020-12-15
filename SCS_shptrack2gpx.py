#!/usr/bin/env python

"""
 SCS_shptrack2gpx.py

 History:
 --------

"""

import argparse
import datetime

import pandas as pd

from io_utils import ConfigParserLocal

__author__ = "Shaun Bell"
__email__ = "shaun.bell@noaa.gov"
__created__ = datetime.datetime(2017, 4, 12)
__modified__ = datetime.datetime(2017, 4, 12)
__version__ = "0.1.0"
__status__ = "Development"
__keywords__ = "gpx", "shiptrack"


def convert_dms_to_dec(value, dir):
    dPos = str(value).find(".")

    mPos = dPos - 2
    ePos = dPos

    main = float(str(value)[:mPos])
    min1 = float(str(value)[mPos:])

    # 	print "degrees:'%s', minutes:'%s'\n" % (main, min1)

    newval = float(main) + float(min1) / float(60)

    if dir == "W":
        newval = -newval
    elif dir == "S":
        newval = -newval

    return newval


"""------------------------------- MAIN------------------------------------------------"""

parser = argparse.ArgumentParser(
    description="Convert SCS GPGGA gps files to .gpx files"
)
parser.add_argument("-i", "--input", type=str, help="path to data files")
parser.add_argument("-o", "--output", type=str, help="path to save files")
parser.add_argument("-csv", "--csv", action="store_true",
                    help="save as csv instead")

args = parser.parse_args()

print(
    '<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.0" creator="nmea_conv"\nxmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/0"\nxsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">\n'
)
if args.input:
    print("<trk>")
    print("<name>{0}</name>").format(args.input)
    print("<trkseg>")
    data = pd.read_csv(args.input, header=None)
    for i, row in data.iterrows():
        lat = convert_dms_to_dec(row[4], row[5])
        lon = convert_dms_to_dec(row[6], row[7])
        timestamp = (
            (pd.to_datetime(row[0] + " " + row[1]
                            [:-4], format="%m/%d/%Y %H:%M:%S"))
            .to_pydatetime()
            .isoformat()
        )
        if args.csv:
            print("{lat},{lon},{time}").format(
                lat=lat, lon=lon, time=timestamp)
        else:
            print(
                '<trkpt lat="{lat}" lon="{lon}"><ele>0.0</ele><time>{time}Z</time></trkpt>'
            ).format(lat=lat, lon=lon, time=timestamp)
print("</trkseg>\n</trk>\n</gpx>\n")
