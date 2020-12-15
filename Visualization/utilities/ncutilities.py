#!/usr/bin/env 
"""
 ncutilities.py
 

   Using Anaconda packaged Python
"""
import datetime

from netCDF4 import Dataset, MFDataset

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2013, 12, 20)
__modified__ = datetime.datetime(2014, 3, 14) #<-- PI DAY :)
__version__  = "0.1.1"
__status__   = "Development"

"""---------------------------------------------------------------------------------"""

def ncopen(ncfile):
    """
    Parameters
    ----------
    TODO
    
    Returns
    -------
    TODO
              
    """
    nchandle = Dataset(ncfile,'r')
    return nchandle

def mf_ncopen(ncfiles):
    """
    Parameters
    ----------
    TODO
    
    Returns
    -------
    TODO
              
    """
    nchandle = MFDataset(ncfiles,'r')
    return nchandle
        
def ncclose(nchandle):
    """
    Parameters
    ----------
    TODO
    
    Returns
    -------
    TODO
              
    """
    nchandle.close()

def get_global_atts(nchandle):

    g_atts = {}
    att_names = nchandle.ncattrs()
    
    for name in att_names:
        g_atts[name] = nchandle.getncattr(name)
        
    return g_atts

def get_vars(nchandle):
    return nchandle.variables.keys()
    
    
def ncreadfile_dic(nchandle, params):
    data = {}
    for j, v in enumerate(params): 
        if v in nchandle.variables.keys(): #check for nc variable
                data[v] = nchandle.variables[v][:]

        else: #if parameter doesn't exist fill the array with zeros
            data[v] = None
    return (data)
    
"""---------------------------------------------------------------------------------"""

def main():
    """ Nothing to do here """
    
if __name__ == "__main__":
    main() 
