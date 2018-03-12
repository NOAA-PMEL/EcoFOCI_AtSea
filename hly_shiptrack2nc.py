#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 13:31:12 2018

#Healy underway data has a specific format. 
#Dyson/NOAA underway data is SCS format.

@author: bell
"""

#System Stack
import datetime
import argparse
import os

#science stack
import pandas as pd
import numpy as np
from netCDF4 import date2num, num2date

#User Stack
import io_utils.EcoFOCI_netCDF_write as EcF_write
import io_utils.ConfigParserLocal as ConfigParserLocal

path = '/Users/bell/ecoraid/2017/AlongTrack/hly1702/met/'
flist = [path + f for f in os.listdir(path) if '.COR' in f]

lat = lon = timestamp = []

for fin in flist:
	print('{currentfile}'.format(currentfile=fin))
	try:
		rawdata = pd.read_csv(fin, header=None, error_bad_lines=False)
		lat = lat + (rawdata[157].values).tolist()
		lon = lon + (rawdata[159].values).tolist()
		timestamp = timestamp + [(pd.to_datetime(str(v1).zfill(8)[-6:]+' '+str(v2).zfill(8)[-6:], format='%d%m%y %H%M%S')).to_pydatetime().isoformat() for v1,v2 in zip(rawdata[1].values,rawdata[2].values)]
		print( len(lat),len(lon),len(timestamp))
	except:
		print("something failed in file {0}".format(fin))

data = pd.DataFrame({'DateTime':timestamp,'latitude':lat,'longitude':lon})
data.set_index(pd.DatetimeIndex(data['DateTime']),inplace=True)
data['time'] = [date2num(x[1],'hours since 1900-01-01T00:00:00Z') for x in enumerate(data.index)]

#data.resample('1H').mean().to_csv('HLY1702_shiptrack.csv')

EPIC_VARS_dict = ConfigParserLocal.get_config('config_files/GPS2NetCDF.yaml','yaml')

#create new netcdf file
ncinstance = EcF_write.NetCDF_Create_Profile_Ragged1D(savefile=path + 'shiptrack.nc')
ncinstance.file_create()
ncinstance.sbeglobal_atts(raw_data_file='', 
    History='File Created from SCS GPPGA GPS data.')
ncinstance.dimension_init(recnum_len=len(data))
ncinstance.variable_init(EPIC_VARS_dict)
ncinstance.add_coord_data(recnum=range(1,len(data)+1))
ncinstance.add_data(EPIC_VARS_dict,data_dic=data,missing_values=np.nan,pandas=True)
ncinstance.close()