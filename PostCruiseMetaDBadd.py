#!/usr/bin/env python

"""
Background:
===========

PostCruiseMetaDBadd.py

Adds MetaInformation from cruisecastlogs db to netcdf files

Input - filepath, CruiseID

History:
=======

2019-02-12: Migrate to python3 - breaks py27 via the raw_input() to input() update

 Compatibility:
 ==============
 python >=3.6 **tested**
 python 2.7 - not supported 


"""

import sys

# must be python 3.6 or greater
try:
    assert sys.version_info >= (3, 6)
except AssertionError:
    sys.exit("Must be running python 3.6 or greater")

# System Stack
import datetime
import os, socket

# DB Stack
import mysql.connector

# Science Stack
from netCDF4 import Dataset
import numpy as np

# User Packages
from io_utils import ConfigParserLocal


__author__ = "Shaun Bell"
__email__ = "shaun.bell@noaa.gov"
__created__ = datetime.datetime(2014, 5, 22)
__modified__ = datetime.datetime(2014, 5, 22)
__version__ = "0.2.0"
__status__ = "Development"
__keywords__ = "CTD", "MetaInformation", "Cruise", "MySQL"

"""--------------------------------SQL Init----------------------------------------"""


class NumpyMySQLConverter(mysql.connector.conversion.MySQLConverter):
    """ A mysql.connector Converter that handles Numpy types """

    def _float32_to_mysql(self, value):
        if np.isnan(value):
            return None
        return float(value)

    def _float64_to_mysql(self, value):
        if np.isnan(value):
            return None
        return float(value)

    def _int32_to_mysql(self, value):
        if np.isnan(value):
            return None
        return int(value)

    def _int64_to_mysql(self, value):
        if np.isnan(value):
            return None
        return int(value)


def connect_to_DB(**kwargs):
    # Open database connection
    try:
        db = mysql.connector.connect(use_pure=True, **kwargs)
    except mysql.connector.Error as err:
        """
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)
      """
        print("error - will robinson")

    db.set_converter_class(NumpyMySQLConverter)

    # prepare a cursor object using cursor() method
    cursor = db.cursor(dictionary=True)
    prepcursor = db.cursor(prepared=True)
    return (db, cursor)


def close_DB(db):
    # disconnect from server
    db.close()


def read_data(db, cursor, table, cruiseID, legNO=""):
    """Currently returns all entries from selected table for selected cruise"""

    sql = "SELECT * from `%s` WHERE `uniquecruiseID`='%s'" % (table, cruiseID)

    print(sql)

    result_dic = {}
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Get column names
        rowid = {}
        counter = 0
        for i in cursor.description:
            rowid[i[0]] = counter
            counter = counter + 1
        # print rowid
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            result_dic[row["id"]] = {
                keys: row[keys] for val, keys in enumerate(row.keys())
            }
        return result_dic
    except:
        print("Error: unable to fecth data")


"""------------------------------------- Main -----------------------------------------"""


def AddMeta_fromDB(user_in, user_out, cruiseID, server="pavlof"):

    table = "cruisecastlogs"
    db_config = ConfigParserLocal.get_config(
        "../EcoFOCI_Config/EcoFOCI_AtSea/db_config_cruises.yaml", "yaml"
    )
    if server == "pavlof":
        host = "pavlof"
    else:
        host = "localhost"

    print("Host is {host}".format(host=host))

    print(db_config["systems"][host]["port"])

    (db, cursor) = connect_to_DB(
        host=db_config["systems"][host]["host"],
        user=db_config["login"]["user"],
        password=db_config["login"]["password"],
        database=db_config["database"]["database"],
        port=db_config["systems"][host]["port"],
    )

    data = read_data(db, cursor, table, cruiseID)
    close_DB(db)

    print("Adding Meta Information from {0}".format(cruiseID))
    ## exit if db is empty
    if len(data.keys()) == 0:
        sys.exit(
            "Sorry, this cruise is either not in the database or was entered "
            "incorrectly.  Please start the program and try again."
        )

    # epic flavored nc files
    nc_path = user_out
    nc_path = [
        nc_path + fi
        for fi in os.listdir(nc_path)
        if fi.endswith(".nc") and not fi.endswith("_cf_ctd.nc")
    ]

    for ncfile in nc_path:

        ncfid = Dataset(ncfile, "a")
        castxxx = ncfile.lower().split(cruiseID.lower())[-1].split("_")[0][1:]

        print("castxxx = " + castxxx)
        castID = "CTD" + castxxx
        print(castID)

        try:
            castmeta = [x for x in data.values() if x["ConsecutiveCastNo"] == castID][0]
            ncfid.setncattr("CAST", castxxx)
            ncfid.setncattr("WATER_MASS", castmeta["WaterMassCode"])
            ncfid.setncattr("BAROMETER", int(castmeta["Pressure"]))
            ncfid.setncattr("WIND_DIR", int(castmeta["WindDir"]))
            ncfid.setncattr("WIND_SPEED", int(castmeta["WindSpd"]))
            ncfid.setncattr("AIR_TEMP", float(castmeta["DryBulb"]))
            ncfid.setncattr("WATER_DEPTH", int(castmeta["BottomDepth"]))
            try:
                ncfid.setncattr("STATION_NAME", castmeta["StationNameID"])
            except:
                pass
            try:
                ncfid.setncattr("STATION_NO", castmeta["StationNo_altname"])
            except:
                pass

        except IndexError:
            print(
                "{ncfile} doesn't have a compatible database entry (may be a 'b' file). Manually add metainfo".format(
                    ncfile=ncfile
                )
            )

        try:
            ### look for existing lat/lon and update if missing
            print((ncfid.variables["lat"][:]))
            if (
                (ncfid.variables["lat"][:] == -999.9)
                or (ncfid.variables["lat"][:] == -999.9)
                or (ncfid.variables["lat"][:] >= 1e35)
                or np.isnan(ncfid.variables["lat"][:])
            ):
                print("filling missing location")
                ncfid.variables["lat"][:] = (
                    castmeta["LatitudeDeg"] + castmeta["LatitudeMin"] / 60.0
                )
                ncfid.variables["lon"][:] = (
                    castmeta["LongitudeDeg"] + castmeta["LongitudeMin"] / 60.0
                )
            else:
                print("updating location")
                ncfid.variables["lat"][:] = (
                    castmeta["LatitudeDeg"] + castmeta["LatitudeMin"] / 60.0
                )
                ncfid.variables["lon"][:] = (
                    castmeta["LongitudeDeg"] + castmeta["LongitudeMin"] / 60.0
                )
        except:
            print("Couldn't update locations")

        ncfid.close()

    processing_complete = True
    return processing_complete


if __name__ == "__main__":

    user_in = input(
        "Please enter the abs path to the .nc file: or \n path, file1, file2: "
    )
    user_out = user_in
    cruiseid = input("Please enter the cruiseid (eg. dy1702l1):  ")
    AddMeta_fromDB(user_in, user_out, cruiseid)
