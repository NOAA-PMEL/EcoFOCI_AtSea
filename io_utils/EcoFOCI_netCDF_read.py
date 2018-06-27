#!/usr/bin/env

"""

class definitions for netcdf4 wrappers

"""


# science stack
from netCDF4 import Dataset, MFDataset
import numpy as np


class EcoFOCI_netCDF(object):

    def __init__(self, file_name=None):
        """Initialize opening of netcdf file.

        Parameters
        ----------
        file_name : str
            full path to file on disk

        """

        self.nchandle = Dataset(file_name,'a')
        self.file_name = file_name


    def _getnchandle_(self):
        return (self.nchandle)        

    def get_global_atts(self):
        """get global attribute for specified name"""
        g_atts = {}
        att_names = self.nchandle.ncattrs()
        
        for name in att_names:
            g_atts[name] = self.nchandle.getncattr(name)
            
        return g_atts

    def set_global_atts(self, name=None, attribute=None):
        """set global attribute for specified name"""
        self.nchandle.setncattr(name,attribute)

    def get_vars(self):
        self.variables = self.nchandle.variables
        return self.nchandle.variables

    def get_vars_attributes(self, var_name=None):
        """get variable attributes for specified variable"""
        return self.nchandle.variables[var_name]


    def repl_var(self, var_name, val=1e35):
        if len(val) == 1:
            self.nchandle.variables[var_name][:] = np.ones_like(self.nchandle.variables[var_name][:]) * val
        else:
            self.nchandle.variables[var_name][:] = val
        return

    def ncreadfile_dic(self,output='array'):

        data = {}
        if output in ['array']:
            for j, v in enumerate(self.nchandle.variables): 
                if v in self.nchandle.variables.keys(): #check for nc variable
                        data[v] = self.nchandle.variables[v][:]

                else: #if parameter doesn't exist fill the array with zeros
                    data[v] = None
        elif output in ['vector']:
            for j, v in enumerate(self.nchandle.variables): 
                if v in self.nchandle.variables.keys(): #check for nc variable
                    try:
                        data[v] = self.nchandle.variables[v][0,:,0,0]
                    except:
                        data[v] = self.nchandle.variables[v][:]
                else: #if parameter doesn't exist fill the array with zeros
                    data[v] = None
        return (data)

    def add_history(self, prev_history, new_history):
        """Adds timestamp (UTC time) and history to existing information"""
        self.nchandle.setncattr('History', prev_history + '\n' 
                + datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")\
                + ' ' + new_history)

    def close(self):
        self.nchandle.close()
 
class EcoFOCI_mfnetCDF(object):

    def __init__(self, file_name=None, aggdim=None):
        """Initialize opening of multiple netcdf files along
        same dimension (aggdim) in same path.

        Parameters
        ----------
        file_name : str
            full path to file on disk (with wildcards)
        aggdim : str
            dimesion name to aggregate along.  Slowest varying
            dimension or unlimited dimension will be choosen if 
            no option is passed.

        """

        self.nchandle = MFDataset(file_name,'a',aggdim=aggdim)
        self.file_name = file_name
        

    def get_global_atts(self):

        g_atts = {}
        att_names = self.nchandle.ncattrs()
        
        for name in att_names:
            g_atts[name] = self.nchandle.getncattr(name)
            
        return g_atts

    def get_vars(self):
        self.variables = self.nchandle.variables
        return self.nchandle.variables

    def ncreadfile_dic(self):

        data = {}
        for j, v in enumerate(self.nchandle.variables): 
            if v in self.nchandle.variables.keys(): #check for nc variable
                    data[v] = self.nchandle.variables[v][:]

            else: #if parameter doesn't exist fill the array with zeros
                data[v] = None
        return (data)

    def close(self):
        self.nchandle.close()