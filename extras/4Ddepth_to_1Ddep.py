#!/usr/bin/env python

"""
 Background:
 ===========
 4Ddepth_to_1Ddep.py
 
 
 Purpose:
 ========
 Takes a 4D netcdf file (like ADCP data) and breaks it into 1D files.
 More specifically, it takes an EPIC flavored file with multiple depths and 
  makes indvidual files for each depth.


 History:
 ========

 Compatibility:
 ==============
 python 2.7 
"""

#System Stack
import datetime
import argparse
import pymysql

#Science Stack
from netCDF4 import Dataset
import numpy as np

#User Stack
import io_utils.ConfigParserLocal as ConfigParserLocal
from calc.EPIC2Datetime import EPIC2Datetime
from io_utils.EcoFOCI_netCDF_read import EcoFOCI_netCDF
from io_utils.EcoFOCI_netCDF_write import NetCDF_Create

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 29)
__modified__ = datetime.datetime(2016, 9, 12)
__version__  = "0.2.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header', 'deployment', 'recovery'



"""------------------------------- MAIN------------------------------------------------"""

parser = argparse.ArgumentParser(description='Trim NC files')
parser.add_argument('inputpath', metavar='inputpath', type=str, help='path to .nc file')

args = parser.parse_args()

###nc readin/out
ncfile = args.inputpath
df = EcoFOCI_netCDF(ncfile)
global_atts = df.get_global_atts()
nchandle = df._getnchandle_()
vars_dic = df.get_vars()
data = df.ncreadfile_dic()

#check for History and make blank if none
if not 'History' in global_atts.keys():
    global_atts['History'] = ''
    
#converttime to datetime
data_dati = EPIC2Datetime(data['time'], data['time2'])
data_dati = np.array(data_dati)


#create new netcdf file
ncinstance = NetCDF_Create(savefile=ncfile.split('.nc')[0] + '.ed.nc')
ncinstance.file_create()      
ncinstance.sbeglobal_atts(raw_data_file=global_atts['DATA_CMNT'], Station_Name=global_atts['STATION_NAME'], 
                            Water_Depth=global_atts['WATER_DEPTH'], 
                            Water_Mass=global_atts['WATER_MASS'], Cast=global_atts['CAST'], 
                            Cruise=global_atts['CRUISE'], History=global_atts['History'],
                            Prog_Cmnt='', Experiment='', Instrument_Type=global_atts['INST_TYPE'], 
                            Barometer=global_atts['BAROMETER'], Wind_Dir=global_atts['WIND_DIR'], 
                            Wind_Speed=global_atts['WIND_SPEED'], 
                            coord_system=global_atts['COORD_SYSTEM'], Air_Temp=global_atts['AIR_TEMP'], sfc_extend=global_atts['SFC_EXTEND'])
ncinstance.dimension_init(depth_len=len(data['depth']))
ncinstance.variable_init(nchandle)

ncinstance.add_coord_data(depth=data['dep'][0,:,0,0], latitude=data['lat'], longitude=data['lon'],
                                 time1=data['time'], time2=data['time2'])
ncinstance.add_data(data=data)    

ncinstance.close()

#close file
df.close()
