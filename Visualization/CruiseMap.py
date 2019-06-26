#!/usr/bin/env python

"""
 CruiseMap.py

 Generates a cruise map of CTD locations from CruiseLog Database and 
 Mooring Locations for all available information

 Input - CruiseID
 Output - png map and kml map

 History
 =======
 
 2019-06-07: Switch basemap for cartopy
 2018-07-13: Make python3 compliant: WIP
 2016-09-09: Begin migration to classes for reused routines (db_io)

 Future
 ======
 Remove Basemap dependancy and replace with cartopy
 Full python 3.6 compatibility

 Compatibility:
 ==============
 python >=3.6 **Tested (with basemap)
 python 2.7 (failed - may be due to conda issues)

"""

from __future__ import (absolute_import, division, print_function)


import sys

#must be python 3.6 or greater
try:
  assert(sys.version_info >= (3,6))
except AssertionError:
  sys.exit("Must be running python 3.6 or greater")

#System Stack
import datetime
import os
import argparse

#DB Stack
import mysql.connector

#Science Stack
import numpy as np
from netCDF4 import Dataset

#Visual Packages
import matplotlib as mpl
mpl.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

import xarray as xa
import cmocean

#user stack
# Relative User Stack
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(1, parent_dir)
from io_utils import ConfigParserLocal

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 5, 22)
__modified__ = datetime.datetime(2014, 5, 22)
__version__  = "0.3.0"
__status__   = "Development"
__keywords__ = 'CTD', 'Cruise Map', 'Cruise', 'MySQL', 'cartopy'


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
        db = mysql.connector.connect(use_pure=True,**kwargs)
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
    return(db,cursor)

def close_DB(db):
    # disconnect from server
    db.close()
    
def read_data(db, cursor, table, cruiseID, dbvar='CruiseID', latvarname='LatitudeDeg'):
    """Currently returns all entries from selected table for selected cruise
        which have valide latitude variables"""
    
    sql = ("SELECT * from `{0}` WHERE `{1}`='{2}' AND `{3}` NOT LIKE '' AND `{3}` NOT LIKE 'NOT DEPLOYED' AND `{3}` NOT LIKE '-99'").format(table, dbvar, cruiseID, latvarname)
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

"""------------------------------------- MAPS -----------------------------------------"""
def make_map(projection=ccrs.PlateCarree()):
    fig, ax = plt.subplots(figsize=(8, 8),
                           subplot_kw=dict(projection=projection))
    if projection == ccrs.PlateCarree():
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=1., color='gray', alpha=0.25, linestyle='--')
        gl.xlabels_top = False
        gl.ylabels_left = False
        gl.xlocator = mticker.FixedLocator([-180, -170, -160, -150, -140, -130])
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.ylabel_style = {'size': 10, 'color': 'gray'}
        gl.xlabel_style = {'size': 10, 'color': 'gray'}
    return fig, ax

def find_nearest(a, a0):
    "Element in nd array `a` closest to the scalar value `a0`"
    idx = np.abs(a - a0).argmin()
    return idx
    
def sqldate2GEdate(castdate,casttime):

    try:
        outstr = datetime.datetime.strptime((castdate + ' ' + casttime), '%Y-%b-%d %H:%M').strftime('%Y-%m-%dT%H:%M:%SZ')
    except:
        outstr = '0000-00-00T00:00:00Z'
        

    return outstr

def convert_timedelta(duration):
    """converts date.timedelta object into hours and minutes string format HH:MM"""
    seconds = duration.seconds
    hours = seconds // 3600
    if hours < 10:
        hours = '0'+str(hours)
    else:
        hours = str(hours)
    minutes = (seconds % 3600) // 60
    if minutes < 10:
        minutes = '0'+str(minutes)
    else:
        minutes = str(minutes)    
    return hours+':'+minutes
        
def cartopy_plot(cast_lon,cast_lat,
                    mooring_lon,mooring_lat,
                    rmooring_lon,rmooring_lat,
                    data_argo_lon,data_argo_lat,
                    data_drifters_lon,data_drifters_lat, filetype):
    """
    To take the place of the basemap routine below
    """
    #using xarray for data read


    server_url = 'https://coastwatch.pfeg.noaa.gov/erddap/griddap/usgsCeSS111'
    bathy = xa.open_dataset(server_url) 

    if args.region in ['BS']:
        bathy_sub = bathy.sel(latitude=slice(66,51),longitude=slice(-180,-152))
    if args.region in ['GOA']:
        bathy_sub = bathy.sel(latitude=slice(60,51),longitude=slice(-160,-135))
    if args.region in ['CK']:
        bathy_sub = bathy.sel(latitude=slice(72,66),longitude=slice(-178,-155))
    if args.region in ['AK']:
        bathy_sub = bathy.sel(latitude=slice(73,50),longitude=slice(-180,-140))
    else:
        sys.exit("Region abrieviation not recognized.  See help (-h)")

    projection=ccrs.LambertConformal(central_longitude=-160.0)
    transformation=ccrs.PlateCarree()

   # Cruise Data
    x_cast, y_cast = -1. * cast_lon,cast_lat
    x_moor, y_moor = -1. * mooring_lon,mooring_lat
    xr_moor, yr_moor = -1. * rmooring_lon,rmooring_lat
    xa_moor, ya_moor = -1. * data_argo_lon,data_argo_lat
    xd_moor, yd_moor = -1. * data_drifters_lon,data_drifters_lat

    dx = dy = 0.5
    extent = [np.min(x_cast)-2.5,np.max(x_cast)+2.5, np.min(y_cast)-1.25,np.max(y_cast)+1.25]
    fig,ax = make_map(projection=projection)

    land_50m = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                            edgecolor='face',
                                            facecolor='1.0')

    ax.contourf(bathy_sub.longitude, bathy_sub.latitude, bathy_sub.topo, 
                levels=[-1000, -200, -100, -70, -50,], 
                colors=('#737373','#969696','#bdbdbd','#d9d9d9','#f0f0f0','#f8f8f8'), 
                extend='both', alpha=.75,
                transform=transformation)

    #plot points
    ax.scatter(x_cast,y_cast,10,marker='+',color='r', 
        transform=transformation)
    ax.scatter(x_moor,y_moor,12,marker='o',facecolors='none', edgecolors='k', 
        transform=transformation)
    ax.scatter(xr_moor,yr_moor,12,marker='o',facecolors='none', edgecolors='y', 
        transform=transformation)
    ax.scatter(xa_moor,ya_moor,12,marker='*',facecolors='none', edgecolors='b', 
        transform=transformation)
    ax.scatter(xd_moor,yd_moor,12,marker='o',facecolors='b', edgecolors='b', 
        transform=transformation)



    #add station labels
    for i,v in enumerate(x_cast):
        ax.text(x_cast[i],y_cast[i],cast_name[i], fontsize=3 , 
        transform=transformation) 
    #add station labels
    for i,v in enumerate(x_moor):
        ax.text(x_moor[i],y_moor[i],mooring_name[i], fontsize=3 , 
        transform=transformation) 
    for i,v in enumerate(xr_moor):
        ax.text(xr_moor[i],yr_moor[i],rmooring_name[i], fontsize=3 , 
        transform=transformation )
    for i,v in enumerate(xa_moor):
        ax.text(xa_moor[i],ya_moor[i],data_argo_name[i], fontsize=3 , 
        transform=transformation) 
    for i,v in enumerate(xd_moor):
        ax.text(xd_moor[i],yd_moor[i],data_drifters_name[i], fontsize=3 , 
        transform=transformation) 

    ax.add_feature(land_50m)
    ax.coastlines(resolution='50m')
    ax.set_extent(extent)

    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0]*1.5, DefaultSize[1]*1.5) )

    if filetype in ['png']:
        plt.savefig('images/' + cruiseID + '/' + cruiseID + '_map.png', bbox_inches='tight', dpi = (300))
    if filetype in ['svg']:
        plt.savefig('images/' + cruiseID + '/' + cruiseID + '_map.svg', bbox_inches='tight', dpi = (300))
    plt.close()



"""-------------------------------------  kml -----------------------------------------"""

def kml_description_box(kml,data):
    """ formating of kml station descriptor boxes using cruisecastlog database info"""

    #station info
    kml = kml + ('<description>\n'
                 '<h2>Project {0}</h2>\n'
                 '<br></br>\n'
                 '<h3>Station</h3>'
                 '<table>\n'
                 '<thead>\n'
                 '   <tr>\n'
                 '     <th></th>\n'
                 '     <th></th>\n'
                 '   </tr>\n'
                 ' </thead>\n'
                 ' <tbody>\n').format(data['Project'])
    kml = kml + ('<tr><td><strong>CTD:</strong> {0}</td>'
                 '<td>{1}</td></tr>\n').format(data['ConsecutiveCastNo'], data['StationNameID'])
    kml = kml + ('<tr><td><strong>Time (GMT):</strong> {0}-{1}-{2} {3}</td>'
                 '<td></td></tr>\n'
                 ).format(data['GMTYear'], data['GMTMonth'],\
                          data['GMTDay'], data['GMTTime'])
    kml = kml + ('<tr><td><strong>Lat (N):</strong> {0}\' {1}\'\'</td><td></td>'
                 '<td></td><td></td></tr>\n'
                 ).format(data['LatitudeDeg'], data['LatitudeMin'])
    kml = kml + ('<tr><td><strong>Lon (W):</strong> {0}\' {1}\'\'</td><td></td>'
                 '<td></td><td></td></tr>\n'
                 ).format(data['LongitudeDeg'], data['LongitudeMin'])
    #cast info
    kml = kml + ('</tbody></table>\n'
                 '<br></br>\n'
                 '<h3>Cast Info</h3>'
                 '<table>\n'
                 '<thead>\n'
                 '   <tr>\n'
                 '     <th></th>\n'
                 '     <th></th>\n'
                 '   </tr>\n'
                 ' </thead>\n'
                 ' <tbody>\n')
    kml = kml + ('<tr><td><strong>Bottom Depth:</strong> {0}</td><td></td></tr>\n'
                 ).format(data['BottomDepth'])
    kml = kml + ('<tr><td><strong>Max Depth:</strong> {0}</td><td></td></tr>\n'
                 ).format(data['MaxDepth'])
    kml = kml + ('<tr><td><strong>Estimated Niskin ID:</strong></td><td>{0}</td><td></td></tr>\n'
                 ).format(data['NutrientBtlNiskinNo'])
    kml = kml + ('<tr><td><strong>Estimated Oxygen Niskin ID:</strong></td><td>{0}</td><td></td></tr>\n'
                 ).format(data['OxygenBtlNiskinNo'])
    kml = kml + ('<tr><td><strong>Estimated Salinity Niskin ID:</strong></td><td>{0}</td><td></td></tr>\n'
                 ).format(data['SalinityBtlNiskinNo'])
    kml = kml + ('<tr><td><strong>Estimated Chlorophyll Niskin ID:</strong></td><td>{0}</td><td></td></tr>\n'
                 ).format(data['ChlorophyllBtlNiskinNo'])
    #met info
    kml = kml + ('</tbody></table>\n'
                 '<br></br>\n'
                 '<h3>Meteorology</h3>'
                 '<table>\n'
                 '<thead>\n'
                 '   <tr>\n'
                 '     <th></th>\n'
                 '     <th></th>\n'
                 '     <th></th>\n'
                 '     <th></th>\n'
                 '     <th></th>\n'
                 '   </tr>\n'
                 ' </thead>\n'
                 ' <tbody>\n')
    kml = kml + ('<tr><td><strong>T:</strong> {0}</td><td><strong>P:</strong> {1}</td>'
                 '<td><strong>RH:</strong> {2}</td><td><strong>WS:</strong> {3}</td><td><strong>WD:</strong> {4}</td></tr>\n'
                 ).format(data['DryBulb'], data['Pressure'],\
                          data['RelativeHumidity'], data['WindSpd'],\
                          data['WindDir'])
    #inst info
    kml = kml + ('</tbody></table>\n'
                 '<br></br>\n'
                 '<h3>Instrument Info</h3>'
                 '<table>\n'
                 '<thead>\n'
                 '   <tr>\n'
                 '     <th></th>\n'
                 '     <th></th>\n'
                 '   </tr>\n'
                 ' </thead>\n'
                 ' <tbody>\n')
    kml = kml + ('<tr><td><strong>CTD Type:</strong> {0}</td><td></td></tr>\n'
                 ).format(data['InstrumentType'])
    kml = kml + ('<tr><td><strong>Instrument SN:</strong> {0}</td><td></td></tr>\n'
                 ).format(data['InstrumentSerialNos'])
    kml = kml + ('<tr><td><strong>Notes:</strong> {0}</td><td></td><td></td></tr>\n'
                 ).format(data['Notes'])
    kml = kml + ('</tbody></table>\n'
                 '</description>\n')


    return kml
"""------------------------------------- Main -----------------------------------------"""


parser = argparse.ArgumentParser(description='KML and PNG maps from Cruise Log Database')
parser.add_argument('CruiseID', metavar='CruiseID', type=str,
               help='CruiseID (eg DY1405) or .txt file with multiple Cruises one per line')
parser.add_argument("-kml",'--kml', action="store_true", help=('Make KML Map') )
parser.add_argument("-png",'--png', action="store_true", help=('Make png Map') )
parser.add_argument("-svg",'--svg', action="store_true", help=('Make svg Map') )
parser.add_argument("-geojson",'--geojson', action="store_true", help=('Make GeoJSON Map') )
parser.add_argument("-csv",'--csv', action="store_true", help=('Output .csv file') )
parser.add_argument("-host",'--host', type=str, default='localhost', help=('local or pavlof') )
parser.add_argument("-reg",'--region', type=str, default='BS',help='BS,GOA,CK,AK')
####
# Data of interest resides in multiple databases on Pavlof
# Deployed Moorings and Recovered Moorings have independant tables in the ecofoci database
# CTD stations are in the ecofoci_cruises database / cruisecastlogs table
# drifter deployments are in the ecofoci_drifters database - argos tracked drifters are in the 
#   table - drifter_ids (and drifter_ids_pre2015)
#   Argo floats are in argofloat_drifters_ids
               
args = parser.parse_args()

cruiseID_input = args.CruiseID

if '.txt' in cruiseID_input:  #assume file hasone cruise per line with tab if Leg is identified
    with open(cruiseID_input,'r') as fid:
        mcruiseID = fid.read()
    fid.close()
    cruiseID_input = mcruiseID.split('\n')
else:
    cruiseID_input = [cruiseID_input,]
        
    
table='cruisecastlogs'
mtable='mooringdeploymentlogs'
rtable='mooringrecoverylogs'
drifter_table='drifter_ids'
argo_table='argofloat_drifter_ids'

for cruiseID in cruiseID_input:
    
    print('Working on Cruise: {}'.format(cruiseID))
    # ctd db
    #get information from local config file - a json formatted file
    db_config = ConfigParserLocal.get_config('../../EcoFOCI_Config/EcoFOCI_AtSea/db_config_cruises.yaml')

    #get db meta information for mooring
    ### connect to DB
    (db,cursor) = connect_to_DB(host=db_config['systems'][args.host]['host'], 
                                user=db_config['login']['user'], 
                                password=db_config['login']['password'], 
                                database=db_config['database']['database'], 
                                port=db_config['systems'][args.host]['port'])
    data = read_data(db, cursor, table, cruiseID, dbvar='UniqueCruiseID')
    close_DB(db)
    
    # mooring db
    db_config = ConfigParserLocal.get_config('../../EcoFOCI_Config/EcoFOCI_AtSea/db_config_mooring.yaml')

    #get db meta information for mooring
    ### connect to DB
    (db,cursor) = connect_to_DB(host=db_config['systems'][args.host]['host'], 
                                user=db_config['login']['user'], 
                                password=db_config['login']['password'], 
                                database=db_config['database']['database'], 
                                port=db_config['systems'][args.host]['port'])
    data_mooring = read_data(db, cursor, mtable, cruiseID, dbvar='CruiseNumber', latvarname='Latitude')
    if not data_mooring.keys():
        cruiseIDt = cruiseID[:4]+'-'+cruiseID[4:]
        data_mooring = read_data(db, cursor, mtable, cruiseIDt, dbvar='CruiseNumber', latvarname='Latitude')

    rdata_mooring = read_data(db, cursor, rtable, cruiseID, dbvar='CruiseNumber', latvarname='Latitude')
    if not rdata_mooring.keys():
        cruiseIDt = cruiseID[:4]+'-'+cruiseID[4:]
        rdata_mooring = read_data(db, cursor, rtable, cruiseIDt, dbvar='CruiseNumber', latvarname='Latitude')
    close_DB(db)
    
    #get db meta info for drifters and argo floats
    ### connect to DB
    # mooring db
    db_config = ConfigParserLocal.get_config('../../EcoFOCI_Config/EcoFOCI_AtSea/db_config_drifters.yaml')

    (db,cursor) = connect_to_DB(host=db_config['systems'][args.host]['host'], 
                                user=db_config['login']['user'], 
                                password=db_config['login']['password'], 
                                database=db_config['database']['database'], 
                                port=db_config['systems'][args.host]['port'])
    data_argo = read_data(db, cursor, argo_table, cruiseID, dbvar='CruiseID', latvarname='ReleaseLat')
    if not data_argo.keys():
        cruiseIDt = cruiseID[:4]+'-'+cruiseID[4:]
        data_argo = read_data(db, cursor, argo_table, cruiseIDt, dbvar='CruiseID', latvarname='ReleaseLat')

    data_drifters = read_data(db, cursor, drifter_table, cruiseID, dbvar='CruiseID', latvarname='ReleaseLat')
    if not data_drifters.keys():
        cruiseIDt = cruiseID[:4]+'-'+cruiseID[4:]
        data_drifters = read_data(db, cursor, drifter_table, cruiseIDt, dbvar='CruiseID', latvarname='ReleaseLat')
    close_DB(db)
    
    ## exit if db is empty
    if (len(list(data.keys())) == 0):
        sys.exit("Sorry, this cruise is either not in the database or was entered "
                 "incorrectly.  Please start the program and try again.")

    ########
        
    # build folder if not exist
    if not os.path.exists('images/' + cruiseID + '/'):
        os.makedirs('images/' + cruiseID)
    
    ## get relevant data for plotting
    cast_name = [data[a_ind]['ConsecutiveCastNo'] for a_ind in list(data.keys())]
    cast_lat = np.array([float(data[a_ind]['LatitudeDeg']) + float(data[a_ind]['LatitudeMin'])/60.0 for a_ind in list(data.keys())])
    cast_lon = np.array([float(data[a_ind]['LongitudeDeg']) + float(data[a_ind]['LongitudeMin'])/60.0 for a_ind in list(data.keys())])
    cast_date = [str(data[a_ind]['GMTYear'])+'-'+data[a_ind]['GMTMonth']+'-'+str(data[a_ind]['GMTDay']) for a_ind in list(data.keys())]
    cast_time = [convert_timedelta(data[a_ind]['GMTTime']) for a_ind in list(data.keys())]

    
    #deployed moorings
    mooring_name = [data_mooring[a_ind]['MooringID'] for a_ind in data_mooring.keys()]
    try:
        mooring_lat = np.array([float(data_mooring[a_ind]['Latitude'].split()[0]) + float(data_mooring[a_ind]['Latitude'].split()[1])/60.0 for a_ind in data_mooring.keys()])
        mooring_lon = np.array([float(data_mooring[a_ind]['Longitude'].split()[0]) + float(data_mooring[a_ind]['Longitude'].split()[1])/60.0 for a_ind in data_mooring.keys()])
    except ValueError: #or empty
        mooring_lat = np.array([float(data_mooring[a_ind]['Latitude'].split()[0]) for a_ind in data_mooring.keys()])
        mooring_lon = np.array([float(data_mooring[a_ind]['Longitude'].split()[0]) for a_ind in data_mooring.keys()])

    #recovered moorings
    rmooring_name = [rdata_mooring[a_ind]['MooringID'] for a_ind in rdata_mooring.keys()]
    try:
        rmooring_lat = np.array([float(rdata_mooring[a_ind]['Latitude'].split()[0]) + float(rdata_mooring[a_ind]['Latitude'].split()[1])/60.0 for a_ind in rdata_mooring.keys()])
        rmooring_lon = np.array([float(rdata_mooring[a_ind]['Longitude'].split()[0]) + float(rdata_mooring[a_ind]['Longitude'].split()[1])/60.0 for a_ind in rdata_mooring.keys()])
    except ValueError: #or empty
        rmooring_lat = np.array([float(rdata_mooring[a_ind]['Latitude'].split()[0]) for a_ind in rdata_mooring.keys()])
        rmooring_lon = np.array([float(rdata_mooring[a_ind]['Longitude'].split()[0]) for a_ind in rdata_mooring.keys()])

    #argo floats
    data_argo_name = [data_argo[a_ind]['ArgoID'] for a_ind in data_argo.keys()]
    try:
        data_argo_lat = np.array([float(data_argo[a_ind]['ReleaseLat'].split()[0]) + float(data_argo[a_ind]['ReleaseLat'].split()[1])/60.0 for a_ind in data_argo.keys()])
        data_argo_lon = np.array([float(data_argo[a_ind]['ReleaseLon'].split()[0]) + float(data_argo[a_ind]['ReleaseLon'].split()[1])/60.0 for a_ind in data_argo.keys()])
    except ValueError: #or empty
        data_argo_lat = np.array([float(data_argo[a_ind]['ReleaseLat'].split()[0]) for a_ind in data_argo.keys()])
        data_argo_lon = np.array([float(data_argo[a_ind]['ReleaseLon'].split()[0]) for a_ind in data_argo.keys()])

    #argos drifters
    data_drifters_name = [data_drifters[a_ind]['ArgosNumber'] for a_ind in data_drifters.keys()]
    try:
        data_drifters_lat = np.array([float(data_drifters[a_ind]['ReleaseLat'].split()[0]) + float(data_drifters[a_ind]['ReleaseLat'].split()[1])/60.0 for a_ind in data_drifters.keys()])
        data_drifters_lon = np.array([float(data_drifters[a_ind]['ReleaseLon'].split()[0]) + float(data_drifters[a_ind]['ReleaseLon'].split()[1])/60.0 for a_ind in data_drifters.keys()])
    except ValueError: #or empty
        data_drifters_lat = np.array([float(data_drifters[a_ind]['ReleaseLat'].split()[0]) for a_ind in data_drifters.keys()])
        data_drifters_lon = np.array([float(data_drifters[a_ind]['ReleaseLon'].split()[0]) for a_ind in data_drifters.keys()])
            
                
    ### Basemap Visualization
    if args.png or args.svg:
        print("Generating image")

        if args.svg:
            cartopy_plot(cast_lon,cast_lat,
                mooring_lon,mooring_lat,
                rmooring_lon,rmooring_lat,
                data_argo_lon,data_argo_lat,
                data_drifters_lon,data_drifters_lat, filetype='svg')
        if args.png:
            cartopy_plot(cast_lon,cast_lat,
                mooring_lon,mooring_lat,
                rmooring_lon,rmooring_lat,
                data_argo_lon,data_argo_lat,
                data_drifters_lon,data_drifters_lat, filetype='png')



        #cartopy_plot()

    ### KML for google Earth
    if args.kml:
        print("Generating .kml")
    
        kml_header = (
            '<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n'
            '<kml:kml xmlns:atom=\'http://www.w3.org/2005/Atom\' xmlns:gx=\'http://www.google.com/kml/ext/2.2\' xmlns:kml=\'http://www.opengis.net/kml/2.2\'>\n'
            '<kml:Document>\n'
            '<name>EcoFOCI</name>\n'
            )
    
        kml_style = (
        '        <Style id=\'drifter\'>\n'
        '            <LineStyle>\n'
        '                <color>ffffaa07</color>\n'
        '                <width>2</width>\n'
        '            </LineStyle>\n'
        '            <IconStyle>\n'
        '                <scale>0.75</scale>\n'
        '                <Icon>\n'
        '                    <href>http://maps.google.com/mapfiles/kml/shapes/donut.png</href>\n'
        '                </Icon>\n'
        '            </IconStyle>\n'
        '        </Style>\n'
        '        <Style id=\'ctd\'>\n'
        '            <LineStyle>\n'
        '                <color>b366ff00</color>\n'
        '                <width>2</width>\n'
        '            </LineStyle>\n'
        '            <IconStyle>\n'
        '                <scale>0.75</scale>\n'
        '                <Icon>\n'
        '                    <href>http://maps.google.com/mapfiles/kml/shapes/donut.png</href>\n'
        '                </Icon>\n'
        '            </IconStyle>\n'
        '           <LabelStyle>\n'
        '            <scale>0.5</scale>\n'
        '           </LabelStyle>\n'
        '        </Style>\n'
        '        <Style id=\'mooring\'>\n'
        '            <IconStyle>\n'
        '                <scale>1.0</scale>\n'
        '                <Icon>\n'
        '                    <href>http://maps.google.com/mapfiles/kml/shapes/donut.png</href>\n'
        '                </Icon>\n'
        '            </IconStyle>\n'
        '        </Style>\n'
                )
    
        kml_type = (
            '<Folder>\n'
            '<name>{0}</name>\n'
            '      <Style>\n'
            '    <ListStyle>\n'
            '      <listItemType>checkHideChildren</listItemType>\n'
            '    </ListStyle>\n'
            '  </Style>\n'
            ).format(cruiseID)    
    
        kml_footer = (
            '</Folder>\n'
            '</kml:Document>\n'
            '</kml:kml>\n'
            )
    
        kml = ''
        for ind, value in enumerate(list(data.keys())):
        
            kml = kml + (
               '        <Placemark>\n'
               '            <name>{0}</name>\n').format(cast_name[ind])
               
            kml = kml_description_box(kml,data[value])
            
            kml = kml + (
               '            <TimeStamp>\n'
               '                <when>{2}</when>\n'
               '            </TimeStamp>\n'
               '        <styleUrl>#ctd</styleUrl>\n'
               '        <Point>\n'
               '            <coordinates>{1:3.4f},{0:3.4f}</coordinates>\n'
               '        </Point>\n'
               '        </Placemark>\n'
               ).format(cast_lat[ind],-1*cast_lon[ind],sqldate2GEdate(cast_date[ind],cast_time[ind]))
    
        fid = open('images/' + cruiseID + '/' + cruiseID + '.kml', 'w')
        #fid.write( 'Content-Type: application/vnd.google-earth.kml+xml\n' )
        fid.write( kml_header + kml_style + kml_type + kml + kml_footer )
        fid.close()
        
    ### GeoJSON for openmaps
    if args.geojson:
        """
        GeoJSON format example:
        {
          "type": "FeatureCollection",
          "features": [
            {
              "type": "Feature",
              "geometry": {
                "type": "Point",
                "coordinates": [102.0, 0.6]
              },
              "properties": {
                "prop0": "value0"
              }
            },
            {
              "type": "Feature",
              "geometry": {
                "type": "LineString",
                "coordinates": [
                  [102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]
                ]
              },
              "properties": {
                "prop1": 0.0,
                "prop0": "value0"
              }
            },
            {
              "type": "Feature",
              "geometry": {
                "type": "Polygon",
                "coordinates": [
                  [
                    [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0],
                    [100.0, 0.0]
                  ]
                ]
              },
              "properties": {
                "prop1": {
                  "this": "that"
                },
                "prop0": "value0"
              }
            }
          ]
        }"""

        print("Generating .geojson as single points per cast")
        geojson_header = (
            '{\n'
            '"type": "FeatureCollection",\n'
            '"features": [\n'
            )
        geojson_Features = ''
        for ind, value in enumerate(list(data.keys())):
            geojson_Features = geojson_Features + (
            '{{\n'
            '"type": "Feature",\n'
            '"id": {2},\n'
            '"geometry": {{\n'
            '"type": "Point",\n'
            '"coordinates": '
            '[{1},{0}]'
            '}},\n'
            '"properties": {{\n'
            '"Project": "{3}",'
            '"ConsecutiveCastNo": "{4}",'
            '"StationNameID": "{5}",'
            '"GMTYear": "{6}",'
            '"GMTMonth": "{7}",'
            '"GMTDay": "{8}",'
            '"GMTTime": "{9}"'
            '}}\n').format(cast_lat[ind],-1*cast_lon[ind], ind, data[value]['Project'], 
            data[value]['ConsecutiveCastNo'],data[value]['StationNameID'],data[value]['GMTYear'],
            data[value]['GMTMonth'],data[value]['GMTDay'],data[value]['GMTTime'])
            
            if value is not list(data.keys())[-1]:
                geojson_Features = geojson_Features + '}\n, '

        geojson_tail = (
            '}\n'
            ']\n'
            '}\n'
            )
          
        fid = open('images/' + cruiseID + '/' + cruiseID + '.geo.json', 'w')
        fid.write( geojson_header + geojson_Features + geojson_tail )
        fid.close()        
            
    ### CSV file for any additional purpose
    if args.csv:
    
        with open('images/' + cruiseID + '/' + cruiseID + '.csv', 'w') as fid:
            for row, cast in enumerate(cast_name):
                fid.write( "{0}, {1}, {2}\n".format(cast, cast_lat[row], cast_lon[row]) )
