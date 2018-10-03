#!/usr/bin/env python

"""
 Background:
 ===========
 nc2nc_2files.py
 
 
 Purpose:
 ========
 Replaces entries from one specified netcdf file to another


 History:
 ========

 Compatibility:
 ==============
 python 2.7 
"""

#System Stack
import datetime
import argparse

#Science Stack
from netCDF4 import Dataset

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 29)
__modified__ = datetime.datetime(2014, 01, 29)
__version__  = "0.2.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header', 'QC'

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

def repl_var(nchandle, var_name, user_val ):
    nchandle.variables[var_name][0,:,0,0] = user_val[0,:,0,0]
    return

def repl_var_dim(nchandle, var_name, user_val ):
    nchandle.variables[var_name][:] = user_val[:]
    return

"""------------------------------- MAIN--------------------------------------------"""

parser = argparse.ArgumentParser(description='Copy Data from one netcdf file to another existing file')
parser.add_argument('sourcefile', metavar='sourcefile', type=str, help='complete path to epic file')
parser.add_argument('destinationfile', metavar='destinationfile', type=str,help='complete path to epic file')
parser.add_argument('epic_var', metavar='epic_var', type=str, help='epic variable to add from source to destination')

args = parser.parse_args()


#add ability to ingest entire directory
#EPIC files only

print "Grabing information from file %s \n" % args.sourcefile
print "Placing it in file %s \n" % args.destinationfile

###nc readin
nchandle = Dataset(args.sourcefile,'a')
vars_dic = get_vars(nchandle)
data = ncreadfile_dic(nchandle,vars_dic)
nchandle.close()

if args.epic_var in ['time','time2','lat','lon','dep','depth']:
    nchandle = Dataset(args.destinationfile,'a')
    vars_dic2 = get_vars(nchandle)
    for v,k in enumerate(vars_dic):
        if k in [args.epic_var]:
            print "Replacing {0}".format(k)
            repl_var_dim(nchandle, args.epic_var, data[k])
        else:
            continue
else:
    nchandle = Dataset(args.destinationfile,'a')
    vars_dic2 = get_vars(nchandle)
    for v,k in enumerate(vars_dic):
        if k in [args.epic_var]:
            print "Replacing {0}".format(k)
            repl_var(nchandle, args.epic_var, data[k])
        else:
            continue
        
nchandle.close()


