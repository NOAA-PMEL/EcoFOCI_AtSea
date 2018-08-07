#!/usr/bin/env python

"""
 Background:
 ===========
 NetCDF_ADDvar.py
 
 
 Purpose:
 ========
 Add a variable to a netcdf file
 
 History:
 ========

 2016-06-10: Update program so that it pulls possible new variables from epic.json file
 2016-12-29: Update to add History attribute

Compatibility:
 ==============
 python >=3.6 - Not Tested
 python 2.7 
"""

#System Stack
import datetime
import argparse
import os

#Science Stack
from netCDF4 import Dataset

#User Stack
# Relative User Stack
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(1, parent_dir)
import io_utils.ConfigParserLocal as ConfigParserLocal


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 29)
__modified__ = datetime.datetime(2014, 01, 29)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header'

    
"""--------------------------------netcdf Routines---------------------------------------"""


def get_global_atts(nchandle):

    g_atts = {}
    att_names = nchandle.ncattrs()
    
    for name in att_names:
        g_atts[name] = nchandle.getncattr(name)
        
    return g_atts

def get_vars(nchandle):
    return nchandle.variables

def ncreadfile_dic(nchandle, params):
    data = {}
    for j, v in enumerate(params): 
        if v in nchandle.variables.keys(): #check for nc variable
                data[v] = nchandle.variables[v][:]

        else: #if parameter doesn't exist fill the array with zeros
            data[v] = None
    return (data)

def repl_var(nchandle, var_name, val):
    nchandle.variables[var_name][0,:,0,0] = val
    return
        
"""------------------------------- MAIN------------------------------------------------"""

parser = argparse.ArgumentParser(description='add a variable to a .nc file')
parser.add_argument('sourcedir', metavar='sourcedir', type=str, help='path to .nc files')
parser.add_argument('add_epic_var', metavar='add_epic_var', type=str, help='name of new epic variable')

args = parser.parse_args()

# If these variables are not defined, no data will be archived into the nc file for that parameter.
EPIC_VARS_dict = ConfigParserLocal.get_config(parent_dir + '/config_files/epickey.json', ftype='json')


ctd_data_files = [x for x in os.listdir(args.sourcedir) if x.endswith('.nc')]

for count, ncfile in enumerate(ctd_data_files): #cycle through all available files for an id

    ###nc readin
    nchandle = Dataset(args.sourcedir + ncfile,'a')
    global_atts = get_global_atts(nchandle)
    vars_dic = get_vars(nchandle)
    data = ncreadfile_dic(nchandle, vars_dic.keys())


    try :
        epic_var_ind = (args.add_epic_var).split('_')[1]
        print("Adding {0} by searching for {1}".format(args.add_epic_var, epic_var_ind))
        newvar = nchandle.createVariable(EPIC_VARS_dict[epic_var_ind]['EPIC_KEY'],'f4',('time','dep','lat','lon',), fill_value=1e35)
        newvar.setncattr('name',EPIC_VARS_dict[epic_var_ind]['NAME']) 
        newvar.long_name = EPIC_VARS_dict[epic_var_ind]['LONGNAME'] 
        newvar.generic_name = EPIC_VARS_dict[epic_var_ind]['GENERIC_NAME']
        newvar.units = EPIC_VARS_dict[epic_var_ind]['UNITS']
        newvar.FORTRAN_format = EPIC_VARS_dict[epic_var_ind]['FORMAT']
        newvar.epic_code = int(epic_var_ind) 


        print("adding history attribute")
        if not 'History' in global_atts.keys():
            histtime=datetime.datetime.utcnow()
            nchandle.setncattr('History','{histtime:%B %d, %Y %H:%M} UTC {variable} added'.format(histtime=histtime,variable=args.add_epic_var))
        else:
            histtime=datetime.datetime.utcnow()
            nchandle.setncattr('History', global_atts['History'] +'\n'+ '{histtime:%B %d, %Y %H:%M} UTC {variable} added'.format(histtime=histtime,variable=args.add_epic_var))


    except:
        print("{0} - not added".format(args.add_epic_var))

      
    nchandle.close()
    
