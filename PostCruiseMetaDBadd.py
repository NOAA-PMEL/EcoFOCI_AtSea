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

#must be python 3.6 or greater
try:
  assert(sys.version_info >= (3,6))
except AssertionError:
  sys.exit("Must be running python 3.6 or greater")

#System Stack
import datetime
import os, socket

#DB Stack
import pymysql

#Science Stack
from netCDF4 import Dataset
import numpy as np

#User Packages
from io_utils import ConfigParserLocal


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 5, 22)
__modified__ = datetime.datetime(2014, 5, 22)
__version__  = "0.2.0"
__status__   = "Development"
__keywords__ = 'CTD', 'MetaInformation', 'Cruise', 'MySQL'

"""--------------------------------SQL Init----------------------------------------"""

def connect_to_DB(host, user, password, database, port):
    # Open database connection
    try:
        db = pymysql.connect(host, user, password, database, port)
    except:
        print("db error")
        
    # prepare a cursor object using cursor() method
    cursor = db.cursor(pymysql.cursors.DictCursor)
    return(db,cursor)    
    

def close_DB(db):
    # disconnect from server
    db.close()
    
def read_data(db, cursor, table, cruiseID, legNO=''):
    """Currently returns all entries from selected table for selected cruise"""
    
    sql = "SELECT * from `%s` WHERE `cruiseID`='%s' and `Project_Leg`='%s'" % (table, cruiseID, legNO)

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
            counter = counter +1 
        #print rowid
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            result_dic[row['id']] ={keys: row[keys] for val, keys in enumerate(row.keys())} 
        return (result_dic)
    except:
        print("Error: unable to fecth data")

"""------------------------------------- Main -----------------------------------------"""

def AddMeta_fromDB(user_in, user_out, cruiseID, server='pavlof'):
            
    table='cruisecastlogs'
    db_config = ConfigParserLocal.get_config('../EcoFOCI_Config/EcoFOCI_AtSea/db_config_cruises.yaml','yaml')
    if server == 'pavlof':
        host='pavlof'
    else:
        host='localhost'

    print("Host is {host}".format(host=host))

    (db,cursor) = connect_to_DB(db_config['systems'][host]['host'], 
        db_config['login']['user'], db_config['login']['password'], 
        db_config['database']['database'], db_config['systems'][host]['port'])
    data = read_data(db, cursor, table, cruiseID)
    close_DB(db)

    
    print("Adding Meta Information from {0}".format(cruiseID))
    ## exit if db is empty
    if (len(data.keys()) == 0):
        sys.exit("Sorry, this cruise is either not in the database or was entered "
                "incorrectly.  Please start the program and try again.")


    #epic flavored nc files
    nc_path = user_out
    nc_path = [nc_path + fi for fi in os.listdir(nc_path) if fi.endswith('.nc') and not fi.endswith('_cf_ctd.nc')]

    for ncfile in nc_path:
        
        ncfid = Dataset(ncfile,'a')
        if not leg:
            castxxx = ncfile.lower().split(cruiseID.lower())[-1].split('_')[0][1:]
        else:
            castxxx = ncfile.lower().split(cruiseID.lower())[-1].split('_')[0][1:]

        print('castxxx = ' + castxxx)
        castID = 'CTD' + castxxx
        print(castID)
        
        try:
            castmeta = [x for x in data.itervalues() if x['ConsecutiveCastNo'] == castID][0]
            ncfid.setncattr('CAST',castxxx)
            ncfid.setncattr('WATER_MASS',castmeta['WaterMassCode'])
            ncfid.setncattr('BAROMETER',int(castmeta['Pressure']))
            ncfid.setncattr('WIND_DIR',int(castmeta['WindDir']))
            ncfid.setncattr('WIND_SPEED',int(castmeta['WindSpd']))
            ncfid.setncattr('AIR_TEMP',float(castmeta['DryBulb']))
            ncfid.setncattr('WATER_DEPTH',int(castmeta['BottomDepth']))
            try:
                ncfid.setncattr('STATION_NAME',castmeta['StationNameID'])
            except:
                pass
            try:
                ncfid.setncattr('STATION_NO',castmeta['StationNo_altname'])
            except:
                pass

        except IndexError:
            print("{ncfile} doesn't have a compatible database entry (may be a 'b' file). Manually add metainfo".format(ncfile=ncfile))

        try:
            ### look for existing lat/lon and update if missing
            if ((ncfid.variables['lat'][:] == -999.9) or 
                    (ncfid.variables['lat'][:] == -999.9) or 
                    (ncfid.variables['lat'][:] == 1e35) or 
                    np.isnan(ncfid.variables['lat'][:])):
                print("updating location")
                ncfid.variables['lat'][:] = castmeta['LatitudeDeg'] + castmeta['LatitudeMin'] / 60.
                ncfid.variables['lon'][:] = castmeta['LongitudeDeg'] + castmeta['LongitudeMin'] / 60.
            else:
                print("I failed to update the lat/lon!!!")
                print(ncfid.variables['lat'][:])
        except:
            print("Couldn't update locations")
            
        ncfid.close()

    
    processing_complete = True
    return processing_complete
    
if __name__ == '__main__':

    user_in = input("Please enter the abs path to the .nc file: or \n path, file1, file2: ")
    user_out = user_in
    cruiseid = input("Please enter the cruiseid (eg. dy1702l1):  ")
    AddMeta_fromDB(user_in, user_out, cruiseid)