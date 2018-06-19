#!/usr/bin/env python

"""
 EcoFOCI_netCDF_write.py
 
 class for building netcdf files from specified instruments
 
 
  History:
 --------
 2018-03-22: TODO: EVEN/UNEVEN is important for Ferret like tools. and should be accounted for
 2016-12-19: Add a class for ragged arrays (1D and 2D) - 1D is continuous file
 2016-12-16: Add a class for CF time conventions (1D and 2D) TODO: merge into other classes
 2016-09-16: Add a class for copying the existing structure of a file 
 2016-09-12: Add a class for duplicating netcdf files (all parameters and attributes) 
    but with a new number of data points due to trimming pre/post deployment times

 2016-08-02: Migrate to EcoFOCI_MooringAnalysis pkg and unify netcdf creation code so
    that it is no longer instrument dependant

"""

# Standard library.
import datetime, os

# Scientific stack.
import numpy as np
from netCDF4 import Dataset

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 13)
__modified__ = datetime.datetime(2014, 12, 02)
__version__  = "0.4.0"
__status__   = "Development"


"""-------------------------------NCFile Creation--------------------------------------"""

        
class NetCDF_Create_Timeseries(object):
    """ Class instance to generate a NetCDF file.  

    Standards
    ---------
    EPICNetCDF (PMEL) Standards  


    Usage
    -----
    
    Order of routines matters and no error checking currently exists
    ToDo: Error Checking
    
    Use this to create a nc file with all default values
        ncinstance = NetCDF_Create_Timeseries()
        ncinstance.file_create()
        ncinstance.sbeglobal_atts()
        ncinstance.dimension_init()
        ncinstance.variable_init()
        ncinstance.add_coord_data()
        ncinstance.add_data()
        ncinstance.close()
    """ 
    
    
    nc_format = 'NETCDF3_CLASSIC'
    nc_read   = 'w'

    def __init__(self, savefile='data/test.nc'):
        """initialize output file path"""
        
        self.savefile = savefile
    
    def file_create(self):
            rootgrpID = Dataset(self.savefile, NetCDF_Create_Timeseries.nc_read, 
                                format=NetCDF_Create_Timeseries.nc_format)
            self.rootgrpID = rootgrpID
            return ( rootgrpID )
        
    def sbeglobal_atts(self, raw_data_file='', Water_Mass='', Water_Depth=9999, 
                       Prog_Cmnt='', Experiment='', Edit_Cmnt='', Station_Name='', 
                       SerialNumber='',Instrument_Type='', History='', Project='', featureType=''):
        """
        Assumptions
        -----------
        
        Format of DataFrame.name = 'dy1309l1_ctd001'
        
        seabird related global attributes found in DataFrame.header list
        
        """
        
        self.rootgrpID.CREATION_DATE = datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")
        self.rootgrpID.COMPOSITE = 1
        self.rootgrpID.INST_TYPE = Instrument_Type
        self.rootgrpID.DATA_CMNT = raw_data_file
        self.rootgrpID.EPIC_FILE_GENERATOR = __file__.split('/')[-1] + ' ' + __version__ 
        self.rootgrpID.PROG_CMNT01 = Prog_Cmnt
        self.rootgrpID.EDIT_CMNT01 = Edit_Cmnt
        self.rootgrpID.WATER_DEPTH = Water_Depth
        self.rootgrpID.MOORING = Station_Name
        self.rootgrpID.WATER_MASS = Water_Mass
        self.rootgrpID.EXPERIMENT = Experiment
        self.rootgrpID.PROJECT = Experiment
        self.rootgrpID.SERIAL_NUMBER = SerialNumber
        self.rootgrpID.History = History
        
    def dimension_init(self, time_len=1):
        """
        Assumes
        -------
        Dimensions will be 'time', 'depth', 'lat', 'lon'
        
        Todo
        ----
        User defined dimensions
        """

        self.dim_vars = ['time', 'depth', 'lat', 'lon']
        
        self.rootgrpID.createDimension( self.dim_vars[0], time_len ) #time
        self.rootgrpID.createDimension( self.dim_vars[1], 1 ) #depth
        self.rootgrpID.createDimension( self.dim_vars[2], 1 ) #lat
        self.rootgrpID.createDimension( self.dim_vars[3], 1 ) #lon
        
        
    def variable_init(self, EPIC_VARS_dict):
        """
        EPIC keys:
            passed in as a dictionary (similar syntax as json data file)
            The dictionary keys are what defines the variable names.
        """
        #exit if the variable dictionary is not passed
        if not bool(EPIC_VARS_dict):
            raise RuntimeError('Empty EPIC Dictionary is passed to variable_init.')

        #build record variable attributes
        rec_vars, rec_var_name, rec_var_longname = [], [], []
        rec_var_generic_name, rec_var_FORTRAN, rec_var_units, rec_var_epic = [], [], [], []

        #cycle through epic dictionary and create nc parameters
        for evar in EPIC_VARS_dict.keys():
            rec_vars.append(evar)
            rec_var_name.append( EPIC_VARS_dict[evar]['name'] )
            rec_var_longname.append( EPIC_VARS_dict[evar]['longname'] )
            rec_var_generic_name.append( EPIC_VARS_dict[evar]['generic_name'] )
            rec_var_units.append( EPIC_VARS_dict[evar]['units'] )
            rec_var_FORTRAN.append( EPIC_VARS_dict[evar]['fortran'] )
            rec_var_epic.append( EPIC_VARS_dict[evar]['EPIC_KEY'] )
        
        rec_vars = ['time','time2','depth','lat','lon'] + rec_vars

        rec_var_name = ['', '', '', '', ''] + rec_var_name
        rec_var_longname = ['', '', '', '', ''] + rec_var_longname
        rec_var_generic_name = ['', '', '', '', ''] + rec_var_generic_name
        rec_var_FORTRAN = ['', '', '', '', ''] + rec_var_FORTRAN
        rec_var_units = ['True Julian Day', 'msec since 0:00 GMT','dbar','degree_north','degree_west'] + rec_var_units
        rec_var_type= ['i4', 'i4'] + ['f4' for spot in rec_vars[2:]]
        rec_var_strtype= ['EVEN', 'EVEN', 'EVEN', 'EVEN', 'EVEN'] + ['' for spot in rec_vars[5:]]
        rec_epic_code = [624, 624,1,500,501] + rec_var_epic
        
        var_class = []
        var_class.append(self.rootgrpID.createVariable(rec_vars[0], rec_var_type[0], self.dim_vars[0]))#time1
        var_class.append(self.rootgrpID.createVariable(rec_vars[1], rec_var_type[1], self.dim_vars[0]))#time2
        var_class.append(self.rootgrpID.createVariable(rec_vars[2], rec_var_type[2], self.dim_vars[1]))#depth
        var_class.append(self.rootgrpID.createVariable(rec_vars[3], rec_var_type[3], self.dim_vars[2]))#lat
        var_class.append(self.rootgrpID.createVariable(rec_vars[4], rec_var_type[4], self.dim_vars[3]))#lon
        
        for i, v in enumerate(rec_vars[5:]):  #1D coordinate variables
            var_class.append(self.rootgrpID.createVariable(rec_vars[i+5], rec_var_type[i+5], self.dim_vars))
            
        ### add variable attributes
        for i, v in enumerate(var_class): #4dimensional for all vars
            print ("Adding Variable {0}").format(v)#
            v.setncattr('name',rec_var_name[i])
            v.long_name = rec_var_longname[i]
            v.generic_name = rec_var_generic_name[i]
            v.FORTRAN_format = rec_var_FORTRAN[i]
            v.units = rec_var_units[i]
            v.type = rec_var_strtype[i]
            v.epic_code = rec_epic_code[i]
            
        self.var_class = var_class
        self.rec_vars = rec_vars

        
    def add_coord_data(self, depth=None, latitude=None, longitude=None, time1=None, time2=None, CastLog=False):
        """ """
        self.var_class[0][:] = time1
        self.var_class[1][:] = time2
        self.var_class[2][:] = depth
        self.var_class[3][:] = latitude
        self.var_class[4][:] = longitude #PMEL standard direction

    def add_data(self, EPIC_VARS_dict, data_dic=None, missing_values=1e35):
        """
            using the same dictionary to define the variables, and a new dictionary
                that associates each data array with an epic key, cycle through and populate
                the desired variables.  If a variable is defined in the epic keys but not passed
                to the add_data routine, it should be populated with missing data
        """
        #exit if the variable dictionary is not passed
        if not bool(EPIC_VARS_dict):
            raise RuntimeError('Empty EPIC Dictionary is passed to add_data.')
        
        #cycle through EPIC_Vars and populate with data - this is a comprehensive list of 
        # all variables expected
        # if no data is passed but an epic dictionary is, complete routine leaving variables
        #  with missing data if not found

        for EPICdic_key in EPIC_VARS_dict.keys():
            di = self.rec_vars.index(EPICdic_key)
            try:
                self.var_class[di][:] = data_dic[EPICdic_key]
            except KeyError:
                self.var_class[di][:] = missing_values
        
        
    def add_history(self, new_history):
        """Adds timestamp (UTC time) and history to existing information"""
        self.rootgrpID.History = self.rootgrpID.History + '\n' + datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")\
                    + ' ' + new_history
                    
    def close(self):
        self.rootgrpID.close()

class NetCDF_Create_Profile(object):
    """ Class instance to generate a NetCDF file.  

    Standards
    ---------
    EPICNetCDF (PMEL) Standards  


    Usage
    -----
    
    Order of routines matters and no error checking currently exists
    ToDo: Error Checking
    
    Use this to create a nc file with all default values
        ncinstance = NetCDF_Create_Profile()
        ncinstance.file_create()
        ncinstance.sbeglobal_atts()
        ncinstance.dimension_init()
        ncinstance.variable_init()
        ncinstance.add_coord_data()
        ncinstance.add_data()
        ncinstance.close()
    """ 
    
    
    nc_format = 'NETCDF3_CLASSIC'
    nc_read   = 'w'

    def __init__(self, savefile='data/test.nc'):
        """initialize output file path"""
        
        self.savefile = savefile
    
    def file_create(self):
            rootgrpID = Dataset(self.savefile, NetCDF_Create_Profile.nc_read, 
                                format=NetCDF_Create_Profile.nc_format)
            self.rootgrpID = rootgrpID
            return ( rootgrpID )
        
    def sbeglobal_atts(self, raw_data_file='', Water_Mass='', Water_Depth=9999, 
                       Prog_Cmnt='', Experiment='', Edit_Cmnt='', Station_Name='', 
                       SerialNumber='',Instrument_Type='', History='', Project='', featureType=''):
        """
        Assumptions
        -----------
        
        Format of DataFrame.name = 'dy1309l1_ctd001'
        
        seabird related global attributes found in DataFrame.header list
        
        """
        
        self.rootgrpID.CREATION_DATE = datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")
        self.rootgrpID.COMPOSITE = 1
        self.rootgrpID.INST_TYPE = Instrument_Type
        self.rootgrpID.DATA_CMNT = raw_data_file
        self.rootgrpID.EPIC_FILE_GENERATOR = __file__.split('/')[-1] + ' ' + __version__ 
        self.rootgrpID.PROG_CMNT01 = Prog_Cmnt
        self.rootgrpID.EDIT_CMNT01 = Edit_Cmnt
        self.rootgrpID.WATER_DEPTH = Water_Depth
        self.rootgrpID.MOORING = Station_Name
        self.rootgrpID.WATER_MASS = Water_Mass
        self.rootgrpID.EXPERIMENT = Experiment
        self.rootgrpID.PROJECT = Experiment
        self.rootgrpID.SERIAL_NUMBER = SerialNumber
        self.rootgrpID.History = History
        
    def dimension_init(self, time_len=1, depth_len=1):
        """
        Assumes
        -------
        Dimensions will be 'time', 'depth', 'lat', 'lon'
        
        Todo
        ----
        User defined dimensions
        """

        self.dim_vars = ['time', 'depth', 'lat', 'lon']
        
        self.rootgrpID.createDimension( self.dim_vars[0], time_len ) #time
        self.rootgrpID.createDimension( self.dim_vars[1], depth_len ) #depth
        self.rootgrpID.createDimension( self.dim_vars[2], 1 ) #lat
        self.rootgrpID.createDimension( self.dim_vars[3], 1 ) #lon
        
        
    def variable_init(self, EPIC_VARS_dict):
        """
        EPIC keys:
            passed in as a dictionary (similar syntax as json data file)
            The dictionary keys are what defines the variable names.
        """
        #exit if the variable dictionary is not passed
        if not bool(EPIC_VARS_dict):
            raise RuntimeError('Empty EPIC Dictionary is passed to variable_init.')

        #build record variable attributes
        rec_vars, rec_var_name, rec_var_longname = [], [], []
        rec_var_generic_name, rec_var_FORTRAN, rec_var_units, rec_var_epic = [], [], [], []

        #cycle through epic dictionary and create nc parameters
        for evar in EPIC_VARS_dict.keys():
            rec_vars.append(evar)
            rec_var_name.append( EPIC_VARS_dict[evar]['name'] )
            rec_var_longname.append( EPIC_VARS_dict[evar]['longname'] )
            rec_var_generic_name.append( EPIC_VARS_dict[evar]['generic_name'] )
            rec_var_units.append( EPIC_VARS_dict[evar]['units'] )
            rec_var_FORTRAN.append( EPIC_VARS_dict[evar]['fortran'] )
            rec_var_epic.append( EPIC_VARS_dict[evar]['EPIC_KEY'] )
        
        rec_vars = ['time','time2','depth','lat','lon'] + rec_vars

        rec_var_name = ['', '', '', '', ''] + rec_var_name
        rec_var_longname = ['', '', '', '', ''] + rec_var_longname
        rec_var_generic_name = ['', '', '', '', ''] + rec_var_generic_name
        rec_var_FORTRAN = ['', '', '', '', ''] + rec_var_FORTRAN
        rec_var_units = ['True Julian Day', 'msec since 0:00 GMT','dbar','degree_north','degree_west'] + rec_var_units
        rec_var_type= ['i4', 'i4'] + ['f4' for spot in rec_vars[2:]]
        rec_var_strtype= ['EVEN', 'EVEN', 'EVEN', 'EVEN', 'EVEN'] + ['' for spot in rec_vars[5:]]
        rec_epic_code = [624, 624,1,500,501] + rec_var_epic
        
        var_class = []
        var_class.append(self.rootgrpID.createVariable(rec_vars[0], rec_var_type[0], self.dim_vars[0]))#time1
        var_class.append(self.rootgrpID.createVariable(rec_vars[1], rec_var_type[1], self.dim_vars[0]))#time2
        var_class.append(self.rootgrpID.createVariable(rec_vars[2], rec_var_type[2], self.dim_vars[1]))#depth
        var_class.append(self.rootgrpID.createVariable(rec_vars[3], rec_var_type[3], self.dim_vars[2]))#lat
        var_class.append(self.rootgrpID.createVariable(rec_vars[4], rec_var_type[4], self.dim_vars[3]))#lon
        
        for i, v in enumerate(rec_vars[5:]):  #1D coordinate variables
            var_class.append(self.rootgrpID.createVariable(rec_vars[i+5], rec_var_type[i+5], self.dim_vars))
            
        ### add variable attributes
        for i, v in enumerate(var_class): #4dimensional for all vars
            print ("Adding Variable {0}").format(v)#
            v.setncattr('name',rec_var_name[i])
            v.long_name = rec_var_longname[i]
            v.generic_name = rec_var_generic_name[i]
            v.FORTRAN_format = rec_var_FORTRAN[i]
            v.units = rec_var_units[i]
            v.type = rec_var_strtype[i]
            v.epic_code = rec_epic_code[i]
            
        self.var_class = var_class
        self.rec_vars = rec_vars

        
    def add_coord_data(self, depth=None, latitude=None, longitude=None, time1=None, time2=None, CastLog=False):
        """ """
        self.var_class[0][:] = time1
        self.var_class[1][:] = time2
        self.var_class[2][:] = depth
        self.var_class[3][:] = latitude
        self.var_class[4][:] = longitude #PMEL standard direction

    def add_data(self, EPIC_VARS_dict, data_dic=None, missing_values=1e35):
        """
            using the same dictionary to define the variables, and a new dictionary
                that associates each data array with an epic key, cycle through and populate
                the desired variables.  If a variable is defined in the epic keys but not passed
                to the add_data routine, it should be populated with missing data
        """
        #exit if the variable dictionary is not passed
        if not bool(EPIC_VARS_dict):
            raise RuntimeError('Empty EPIC Dictionary is passed to add_data.')
        
        #cycle through EPIC_Vars and populate with data - this is a comprehensive list of 
        # all variables expected
        # if no data is passed but an epic dictionary is, complete routine leaving variables
        #  with missing data if not found

        for EPICdic_key in EPIC_VARS_dict.keys():
            di = self.rec_vars.index(EPICdic_key)
            try:
                self.var_class[di][:] = data_dic[EPICdic_key]
            except KeyError:
                self.var_class[di][:] = missing_values
        
        
    def add_history(self, new_history):
        """Adds timestamp (UTC time) and history to existing information"""
        self.rootgrpID.History = self.rootgrpID.History + '\n' + datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")\
                    + ' ' + new_history
                    
    def close(self):
        self.rootgrpID.close()

class NetCDF_Trimmed(object):
    """ Class instance to generate a NetCDF file.  
    Takes variable information from preexisting netcdf file via nchandle pass in variable_init.

    Standards
    ---------
    EPICNetCDF (PMEL) Standards  


    Usage
    -----
    
    Order of routines matters and no error checking currently exists
    ToDo: Error Checking
    
    Use this to create a nc file with all default values
        ncinstance = NetCDF_Trimmed()
        ncinstance.file_create()
        ncinstance.sbeglobal_atts()
        ncinstance.dimension_init()
        ncinstance.variable_init(nchandle)
        ncinstance.add_coord_data()
        ncinstance.add_data()
        ncinstance.close()
    """ 
    
    
    nc_format = 'NETCDF3_CLASSIC'
    nc_read   = 'w'
    def __init__(self, savefile='ncfiles/test.nc'):
        """data is a numpy array of temperature values"""
        
        self.savefile = savefile
    
    def file_create(self):
            rootgrpID = Dataset(self.savefile, NetCDF_Trimmed.nc_read, format=NetCDF_Trimmed.nc_format)
            self.rootgrpID = rootgrpID
            return ( rootgrpID )
        
    def sbeglobal_atts(self, raw_data_file='', Water_Mass='', Water_Depth=9999, 
                       Prog_Cmnt='', Experiment='', Edit_Cmnt='', Station_Name='', 
                       SerialNumber='',Inst_Type='', History='', Project='', featureType=''):
        """
        Assumptions
        -----------
        
        Format of DataFrame.name = 'dy1309l1_ctd001'
        
        seabird related global attributes found in DataFrame.header list
        
        """
        
        self.rootgrpID.CREATION_DATE = datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")
        self.rootgrpID.COMPOSITE = 1
        self.rootgrpID.INST_TYPE = Inst_Type
        self.rootgrpID.DATA_CMNT = raw_data_file
        self.rootgrpID.EPIC_FILE_GENERATOR = 'trim_netcdf.py V' + __version__ 
        self.rootgrpID.PROG_CMNT01 = Prog_Cmnt
        self.rootgrpID.EDIT_CMNT01 = Edit_Cmnt
        self.rootgrpID.WATER_DEPTH = Water_Depth
        self.rootgrpID.MOORING = Station_Name
        self.rootgrpID.WATER_MASS = Water_Mass
        self.rootgrpID.EXPERIMENT = Experiment
        self.rootgrpID.PROJECT = Experiment
        self.rootgrpID.History = History
     
    def dimension_init(self, time_len=1):
        """
        Assumes
        -------
        Dimensions will be 'time', 'depth', 'lat', 'lon'
        
        Todo
        ----
        User defined dimensions
        """

        self.dim_vars = ['time', 'depth', 'lat', 'lon']
        
        self.rootgrpID.createDimension( self.dim_vars[0], time_len ) #time
        self.rootgrpID.createDimension( self.dim_vars[1], 1 ) #depth
        self.rootgrpID.createDimension( self.dim_vars[2], 1 ) #lat
        self.rootgrpID.createDimension( self.dim_vars[3], 1 ) #lon
        
        
    def variable_init(self, nchandle):
        """
        built from knowledge about previous file
        """
        
        #build record variable attributes
        rec_vars, rec_var_name, rec_var_longname = [], [], []
        rec_var_generic_name, rec_var_FORTRAN, rec_var_units, rec_var_epic = [], [], [], []
        
        for v_name in nchandle.variables.keys():
            print v_name
            if not v_name in ['time','time2','depth','lat','lon','latitude','longitude']:
                print "Copying attributes for {0}".format(v_name)
                rec_vars.append( v_name )
                rec_var_name.append( nchandle.variables[v_name].name )
                rec_var_longname.append( nchandle.variables[v_name].long_name )
                rec_var_generic_name.append( nchandle.variables[v_name].generic_name )
                rec_var_units.append( nchandle.variables[v_name].units )
                rec_var_FORTRAN.append( nchandle.variables[v_name].FORTRAN_format )
                rec_var_epic.append( nchandle.variables[v_name].epic_code )

        
        rec_vars = ['time','time2','depth','lat','lon'] + rec_vars

        rec_var_name = ['', '', '', '', ''] + rec_var_name
        rec_var_longname = ['', '', '', '', ''] + rec_var_longname
        rec_var_generic_name = ['', '', '', '', ''] + rec_var_generic_name
        rec_var_FORTRAN = ['', '', '', '', ''] + rec_var_FORTRAN
        rec_var_units = ['True Julian Day', 'msec since 0:00 GMT','dbar','degree_north','degree_west'] + rec_var_units
        rec_var_type= ['i4', 'i4'] + ['f4' for spot in rec_vars[2:]]
        rec_var_strtype= ['EVEN', 'EVEN', 'EVEN', 'EVEN', 'EVEN'] + ['' for spot in rec_vars[5:]]
        rec_epic_code = [624, 624,1,500,501] + rec_var_epic
        
        var_class = []
        var_class.append(self.rootgrpID.createVariable(rec_vars[0], rec_var_type[0], self.dim_vars[0]))#time1
        var_class.append(self.rootgrpID.createVariable(rec_vars[1], rec_var_type[1], self.dim_vars[0]))#time2
        var_class.append(self.rootgrpID.createVariable(rec_vars[2], rec_var_type[2], self.dim_vars[1]))#depth
        var_class.append(self.rootgrpID.createVariable(rec_vars[3], rec_var_type[3], self.dim_vars[2]))#lat
        var_class.append(self.rootgrpID.createVariable(rec_vars[4], rec_var_type[4], self.dim_vars[3]))#lon
        
        for i, v in enumerate(rec_vars[5:]):  #1D coordinate variables
            var_class.append(self.rootgrpID.createVariable(rec_vars[i+5], rec_var_type[i+5], self.dim_vars))
            
        ### add variable attributes
        for i, v in enumerate(var_class): #4dimensional for all vars
            print ("Adding Variable {0}").format(v)#
            v.setncattr('name',rec_var_name[i])
            v.long_name = rec_var_longname[i]
            v.generic_name = rec_var_generic_name[i]
            v.FORTRAN_format = rec_var_FORTRAN[i]
            v.units = rec_var_units[i]
            v.type = rec_var_strtype[i]
            v.epic_code = rec_epic_code[i]
            
        self.var_class = var_class
        self.rec_vars = rec_vars

        
    def add_coord_data(self, depth=None, latitude=None, longitude=None, time1=None, time2=None, CastLog=False):
        """ """
        self.var_class[0][:] = time1
        self.var_class[1][:] = time2
        self.var_class[2][:] = depth
        self.var_class[3][:] = latitude
        self.var_class[4][:] = longitude #PMEL standard direction

    def add_data(self, data=None, trim_index=None):
        """ """
        
        for ind, varname in enumerate(data.keys()):
            if not varname in ['time','time2','lat','lon','depth','latitude','longitude']:
                di = self.rec_vars.index(varname)
                self.var_class[di][:] = data[varname][trim_index,0,0,0]
        

        
    def add_history(self, new_history):
        """Adds timestamp (UTC time) and history to existing information"""
        self.rootgrpID.History = self.rootgrpID.History + '\n' + datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")\
                    + ' ' + new_history + '\n'
                    
    def close(self):
        self.rootgrpID.close()

class NetCDF_Copy_Struct(object):
    """ Class instance to generate a NetCDF file.  
    Takes variable information from preexisting netcdf file via nchandle pass in variable_init.

    Standards
    ---------
    EPICNetCDF (PMEL) Standards  


    Usage
    -----
    
    Order of routines matters and no error checking currently exists
    ToDo: Error Checking
    
    Use this to create a nc file with all default values
        ncinstance = NetCDF_Copy_Struct()
        ncinstance.file_create()
        ncinstance.sbeglobal_atts()
        ncinstance.dimension_init()
        ncinstance.variable_init(nchandle)
        ncinstance.add_coord_data()
        ncinstance.add_data()
        ncinstance.close()
    """ 
    
    
    nc_format = 'NETCDF3_CLASSIC'
    nc_read   = 'w'
    def __init__(self, savefile='ncfiles/test.nc'):
        """data is a numpy array of temperature values"""
        
        self.savefile = savefile
    
    def file_create(self):
            rootgrpID = Dataset(self.savefile, NetCDF_Copy_Struct.nc_read, format=NetCDF_Copy_Struct.nc_format)
            self.rootgrpID = rootgrpID
            return ( rootgrpID )
        
    def sbeglobal_atts(self, raw_data_file='', Water_Mass='', Water_Depth=9999, 
                       Prog_Cmnt='', Experiment='', Edit_Cmnt='', Station_Name='', 
                       SerialNumber='',Inst_Type='', History='', Project='', featureType=''):
        """
        Assumptions
        -----------
        
        Format of DataFrame.name = 'dy1309l1_ctd001'
        
        seabird related global attributes found in DataFrame.header list
        
        """
        
        self.rootgrpID.CREATION_DATE = datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")
        self.rootgrpID.COMPOSITE = 1
        self.rootgrpID.INST_TYPE = Inst_Type
        self.rootgrpID.DATA_CMNT = raw_data_file
        self.rootgrpID.EPIC_FILE_GENERATOR = 'trim_netcdf.py V' + __version__ 
        self.rootgrpID.PROG_CMNT01 = Prog_Cmnt
        self.rootgrpID.EDIT_CMNT01 = Edit_Cmnt
        self.rootgrpID.WATER_DEPTH = Water_Depth
        self.rootgrpID.MOORING = Station_Name
        self.rootgrpID.WATER_MASS = Water_Mass
        self.rootgrpID.EXPERIMENT = Experiment
        self.rootgrpID.PROJECT = Experiment
        self.rootgrpID.History = History
        self.rootgrpID.featureType = featureType
     
    def dimension_init(self, time_len=1, depth_len=1):
        """
        Assumes
        -------
        Dimensions will be 'time', 'depth', 'lat', 'lon'
        
        Todo
        ----
        User defined dimensions
        """

        self.dim_vars = ['time', 'depth', 'lat', 'lon']
        
        self.rootgrpID.createDimension( self.dim_vars[0], time_len ) #time
        self.rootgrpID.createDimension( self.dim_vars[1], depth_len ) #depth
        self.rootgrpID.createDimension( self.dim_vars[2], 1 ) #lat
        self.rootgrpID.createDimension( self.dim_vars[3], 1 ) #lon
        
        
    def variable_init(self, variable_dic=None):
        """
        built from knowledge about previous file
        """
        
        #build record variable attributes
        rec_vars, rec_var_name, rec_var_longname = [], [], []
        rec_var_generic_name, rec_var_FORTRAN, rec_var_units, rec_var_epic = [], [], [], []
        
        for v_name in variable_dic.keys():
            print v_name
            if not v_name in ['time','time2','depth','lat','lon','latitude','longitude']:
                print "Copying attributes for {0}".format(v_name)
                rec_vars.append( v_name )
                rec_var_name.append( variable_dic[v_name].name )
                rec_var_longname.append( variable_dic[v_name].long_name )
                rec_var_generic_name.append( variable_dic[v_name].generic_name )
                rec_var_units.append( variable_dic[v_name].units )
                rec_var_FORTRAN.append( variable_dic[v_name].FORTRAN_format )
                rec_var_epic.append( variable_dic[v_name].epic_code )

        
        rec_vars = ['time','time2','depth','lat','lon'] + rec_vars

        rec_var_name = ['', '', '', '', ''] + rec_var_name
        rec_var_longname = ['', '', '', '', ''] + rec_var_longname
        rec_var_generic_name = ['', '', '', '', ''] + rec_var_generic_name
        rec_var_FORTRAN = ['', '', '', '', ''] + rec_var_FORTRAN
        rec_var_units = ['True Julian Day', 'msec since 0:00 GMT','dbar','degree_north','degree_west'] + rec_var_units
        rec_var_type= ['i4', 'i4'] + ['f4' for spot in rec_vars[2:]]
        rec_var_strtype= ['EVEN', 'EVEN', 'EVEN', 'EVEN', 'EVEN'] + ['' for spot in rec_vars[5:]]
        rec_epic_code = [624, 624,1,500,501] + rec_var_epic
        
        var_class = []
        var_class.append(self.rootgrpID.createVariable(rec_vars[0], rec_var_type[0], self.dim_vars[0]))#time1
        var_class.append(self.rootgrpID.createVariable(rec_vars[1], rec_var_type[1], self.dim_vars[0]))#time2
        var_class.append(self.rootgrpID.createVariable(rec_vars[2], rec_var_type[2], self.dim_vars[1]))#depth
        var_class.append(self.rootgrpID.createVariable(rec_vars[3], rec_var_type[3], self.dim_vars[2]))#lat
        var_class.append(self.rootgrpID.createVariable(rec_vars[4], rec_var_type[4], self.dim_vars[3]))#lon
        
        for i, v in enumerate(rec_vars[5:]):  #1D coordinate variables
            var_class.append(self.rootgrpID.createVariable(rec_vars[i+5], rec_var_type[i+5], self.dim_vars))
            
        ### add variable attributes
        for i, v in enumerate(var_class): #4dimensional for all vars
            print ("Adding Variable {0}").format(v)#
            v.setncattr('name',rec_var_name[i])
            v.long_name = rec_var_longname[i]
            v.generic_name = rec_var_generic_name[i]
            v.FORTRAN_format = rec_var_FORTRAN[i]
            v.units = rec_var_units[i]
            v.type = rec_var_strtype[i]
            v.epic_code = rec_epic_code[i]
            
        self.var_class = var_class
        self.rec_vars = rec_vars

        
    def add_coord_data(self, depth=None, latitude=None, longitude=None, time1=None, time2=None, CastLog=False):
        """ """
        self.var_class[0][:] = time1
        self.var_class[1][:] = time2
        self.var_class[2][:] = depth
        self.var_class[3][:] = latitude
        self.var_class[4][:] = longitude #PMEL standard direction

    def add_data(self, data=None, is2D=False, depthindex=False):
        """ """
        
        for ind, varname in enumerate(data.keys()):
            if not varname in ['time','time2','lat','lon','depth','latitude','longitude']:
                di = self.rec_vars.index(varname)
                if is2D:
                    self.var_class[di][:] = data[varname][:,:,0,0]
                else:
                    if (depthindex==False):
                        self.var_class[di][:] = data[varname][:,0,0,0]
                    else:    
                        self.var_class[di][:] = data[varname][:,depthindex,0,0]

        
    def add_history(self, new_history):
        """Adds timestamp (UTC time) and history to existing information"""
        self.rootgrpID.History = self.rootgrpID.History + '\n' + datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")\
                    + ' ' + new_history + '\n'
                    
    def close(self):
        self.rootgrpID.close()

class CF_NC(object):


    """ Class instance to generate a NetCDF file.  
    Assumes data format and information ingested is a dataframe object from ctd.py 

    Standards
    ---------
    EPICNetCDF (PMEL) Standards  


    Usage
    -----
    
    Order of routines matters and no error checking currently exists
    ToDo: Error Checking
    
    Use this to create a nc file with all default values
        ncinstance = CF_NC()
        ncinstance.file_create()
        ncinstance.sbeglobal_atts()
        ncinstance.dimension_init()
        ncinstance.variable_init()
        ncinstance.add_coord_data()
        ncinstance.add_data()
        ncinstance.close()
    """ 
    
    
    nc_format = 'NETCDF3_CLASSIC'
    nc_read   = 'w'
    def __init__(self, savefile='ncfiles/test.nc'):
        """data is a numpy array of temperature values"""
        
        self.savefile = savefile
    
    def file_create(self):
            rootgrpID = Dataset(self.savefile, CF_NC.nc_read, format=CF_NC.nc_format)
            self.rootgrpID = rootgrpID
            return ( rootgrpID )
        
    def sbeglobal_atts(self, raw_data_file='', Water_Mass='B', Water_Depth=9999, Prog_Cmnt='',\
                        Experiment='', Edit_Cmnt='', Station_Name='', Inst_Type='', Project='', History='',featureType=''):
        """
        Assumptions
        -----------
        
        Format of DataFrame.name = 'dy1309l1_ctd001'
        
        seabird related global attributes found in DataFrame.header list
        
        """
        
        self.rootgrpID.CREATION_DATE = datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")
        self.rootgrpID.COMPOSITE = 1
        self.rootgrpID.INST_TYPE = Inst_Type
        self.rootgrpID.DATA_CMNT = raw_data_file
        self.rootgrpID.EPIC_FILE_GENERATOR = 'nc_epic2udunits_time.py V' + __version__ 
        self.rootgrpID.PROG_CMNT01 = Prog_Cmnt
        self.rootgrpID.EDIT_CMNT01 = Edit_Cmnt
        self.rootgrpID.WATER_DEPTH = Water_Depth
        self.rootgrpID.MOORING = Station_Name
        self.rootgrpID.WATER_MASS = Water_Mass
        self.rootgrpID.EXPERIMENT = Experiment
        self.rootgrpID.PROJECT = Experiment
        self.rootgrpID.History = History
        self.rootgrpID.featureType = featureType
                        
        
    def dimension_init(self, time_len=1):
        """
        Assumes
        -------
        Dimensions will be 'time', 'depth', 'lat', 'lon'
        
        Todo
        ----
        User defined dimensions
        """

        self.dim_vars = ['time', 'depth', 'lat', 'lon']
        
        self.rootgrpID.createDimension( self.dim_vars[0], time_len ) #time
        self.rootgrpID.createDimension( self.dim_vars[1], 1 ) #depth
        self.rootgrpID.createDimension( self.dim_vars[2], 1 ) #lat
        self.rootgrpID.createDimension( self.dim_vars[3], 1 ) #lon
        
        
    def variable_init(self, nchandle, udunits_time_str='days since 1900-1-1' ):
        """
        built from knowledge about previous file
        """
        
        #build record variable attributes
        rec_vars, rec_var_name, rec_var_longname = [], [], []
        rec_var_generic_name, rec_var_FORTRAN, rec_var_units, rec_var_epic = [], [], [], []
        
        for v_name in nchandle.variables.keys():
            print v_name
            if not v_name in ['time','time2','depth','lat','lon','latitude','longitude']:
                print "Copying attributes for {0}".format(v_name)
                rec_vars.append( v_name )
                rec_var_name.append( nchandle.variables[v_name].name )
                rec_var_longname.append( nchandle.variables[v_name].long_name )
                rec_var_generic_name.append( nchandle.variables[v_name].generic_name )
                rec_var_units.append( nchandle.variables[v_name].units )
                rec_var_FORTRAN.append( nchandle.variables[v_name].FORTRAN_format )
                rec_var_epic.append( nchandle.variables[v_name].epic_code )

        
        rec_vars = ['time','depth','lat','lon'] + rec_vars

        rec_var_name = ['', '', '', ''] + rec_var_name
        rec_var_longname = ['', '', '', ''] + rec_var_longname
        rec_var_generic_name = ['', '', '', ''] + rec_var_generic_name
        rec_var_FORTRAN = ['', '', '', ''] + rec_var_FORTRAN
        rec_var_units = [udunits_time_str,'dbar','degree_north','degree_west'] + rec_var_units
        rec_var_type= ['f8'] + ['f4' for spot in rec_vars[1:]]
        rec_var_strtype= ['EVEN', 'EVEN', 'EVEN', 'EVEN'] + ['' for spot in rec_vars[4:]]
        rec_epic_code = [624,1,500,501] + rec_var_epic
        
        var_class = []
        var_class.append(self.rootgrpID.createVariable(rec_vars[0], rec_var_type[0], self.dim_vars[0]))#time1
        var_class.append(self.rootgrpID.createVariable(rec_vars[1], rec_var_type[1], self.dim_vars[1]))#depth
        var_class.append(self.rootgrpID.createVariable(rec_vars[2], rec_var_type[2], self.dim_vars[2]))#lat
        var_class.append(self.rootgrpID.createVariable(rec_vars[3], rec_var_type[3], self.dim_vars[3]))#lon
        
        for i, v in enumerate(rec_vars[4:]):  #1D coordinate variables
            var_class.append(self.rootgrpID.createVariable(rec_vars[i+4], rec_var_type[i+4], self.dim_vars))
            
        ### add variable attributes
        for i, v in enumerate(var_class): #4dimensional for all vars
            print ("Adding Variable {0}").format(v)#
            v.setncattr('name',rec_var_name[i])
            v.long_name = rec_var_longname[i]
            v.generic_name = rec_var_generic_name[i]
            v.FORTRAN_format = rec_var_FORTRAN[i]
            v.units = rec_var_units[i]
            v.type = rec_var_strtype[i]
            v.epic_code = rec_epic_code[i]
            
            
        self.var_class = var_class
        self.rec_vars = rec_vars

        
    def add_coord_data(self, depth=None, latitude=None, longitude=None, time=None, CastLog=False):
        """ """
        self.var_class[0][:] = time
        self.var_class[1][:] = depth
        self.var_class[2][:] = latitude
        self.var_class[3][:] = longitude #PMEL standard direction

    def add_data(self, data=None):
        """ """
        
        for ind, varname in enumerate(data.keys()):
            if not varname in ['time','time2','lat','lon','depth','latitude','longitude']:
                di = self.rec_vars.index(varname)
                self.var_class[di][:] = data[varname][:]
        

        
    def add_history(self, new_history):
        """Adds timestamp (UTC time) and history to existing information"""
        self.rootgrpID.History = self.rootgrpID.History + '\n' + datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")\
                    + ' ' + new_history + '\n'
                    
    def close(self):
        self.rootgrpID.close()

class CF_NC_Profile(object):


    """ Class instance to generate a NetCDF file.  
    Assumes data format and information ingested is a dataframe object from ctd.py 

    Standards
    ---------
    EPICNetCDF (PMEL) Standards  


    Usage
    -----
    
    Order of routines matters and no error checking currently exists
    ToDo: Error Checking
    
    Use this to create a nc file with all default values
        ncinstance = CF_NC()
        ncinstance.file_create()
        ncinstance.sbeglobal_atts()
        ncinstance.dimension_init()
        ncinstance.variable_init()
        ncinstance.add_coord_data()
        ncinstance.add_data()
        ncinstance.close()
    """ 
    
    
    nc_format = 'NETCDF3_CLASSIC'
    nc_read   = 'w'
    def __init__(self, savefile='ncfiles/test.nc'):
        """data is a numpy array of temperature values"""
        
        self.savefile = savefile
    
    def file_create(self):
            rootgrpID = Dataset(self.savefile, CF_NC.nc_read, format=CF_NC.nc_format)
            self.rootgrpID = rootgrpID
            return ( rootgrpID )
        
    def sbeglobal_atts(self, raw_data_file='', Water_Mass='B', Water_Depth=9999, Prog_Cmnt='',\
                        Experiment='', Edit_Cmnt='', Station_Name='', Inst_Type='', Project='', History='',featureType=''):
        """
        Assumptions
        -----------
        
        Format of DataFrame.name = 'dy1309l1_ctd001'
        
        seabird related global attributes found in DataFrame.header list
        
        """
        
        self.rootgrpID.CREATION_DATE = datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")
        self.rootgrpID.COMPOSITE = 1
        self.rootgrpID.INST_TYPE = Inst_Type
        self.rootgrpID.DATA_CMNT = raw_data_file
        self.rootgrpID.EPIC_FILE_GENERATOR = 'nc_epic2udunits_time.py V' + __version__ 
        self.rootgrpID.PROG_CMNT01 = Prog_Cmnt
        self.rootgrpID.EDIT_CMNT01 = Edit_Cmnt
        self.rootgrpID.WATER_DEPTH = Water_Depth
        self.rootgrpID.MOORING = Station_Name
        self.rootgrpID.WATER_MASS = Water_Mass
        self.rootgrpID.EXPERIMENT = Experiment
        self.rootgrpID.PROJECT = Experiment
        self.rootgrpID.History = History
        self.rootgrpID.featureType = featureType
                        
        
    def dimension_init(self, depth_len=1):
        """
        Assumes
        -------
        Dimensions will be 'time', 'depth', 'lat', 'lon'
        
        Todo
        ----
        User defined dimensions
        """

        self.dim_vars = ['time', 'depth', 'lat', 'lon']
        
        self.rootgrpID.createDimension( self.dim_vars[0], 1 ) #time
        self.rootgrpID.createDimension( self.dim_vars[1], depth_len ) #depth
        self.rootgrpID.createDimension( self.dim_vars[2], 1 ) #lat
        self.rootgrpID.createDimension( self.dim_vars[3], 1 ) #lon

        
        
    def variable_init(self, nchandle, udunits_time_str='days since 1900-1-1' ):
        """
        built from knowledge about previous file
        """
        
        #build record variable attributes
        rec_vars, rec_var_name, rec_var_longname = [], [], []
        rec_var_generic_name, rec_var_FORTRAN, rec_var_units, rec_var_epic = [], [], [], []
        
        for v_name in nchandle.variables.keys():
            print v_name
            if not v_name in ['time','time2','depth','lat','lon','latitude','longitude']:
                print "Copying attributes for {0}".format(v_name)
                rec_vars.append( v_name )
                rec_var_name.append( nchandle.variables[v_name].name )
                rec_var_longname.append( nchandle.variables[v_name].long_name )
                rec_var_generic_name.append( nchandle.variables[v_name].generic_name )
                rec_var_units.append( nchandle.variables[v_name].units )
                rec_var_FORTRAN.append( nchandle.variables[v_name].FORTRAN_format )
                rec_var_epic.append( nchandle.variables[v_name].epic_code )

        
        rec_vars = ['time','depth','lat','lon'] + rec_vars

        rec_var_name = ['', '', '', ''] + rec_var_name
        rec_var_longname = ['', '', '', ''] + rec_var_longname
        rec_var_generic_name = ['', '', '', ''] + rec_var_generic_name
        rec_var_FORTRAN = ['', '', '', ''] + rec_var_FORTRAN
        rec_var_units = [udunits_time_str,'dbar','degree_north','degree_west'] + rec_var_units
        rec_var_type= ['f8'] + ['f4' for spot in rec_vars[1:]]
        rec_var_strtype= ['EVEN', 'EVEN', 'EVEN', 'EVEN'] + ['' for spot in rec_vars[4:]]
        rec_epic_code = [624,1,500,501] + rec_var_epic
        
        var_class = []
        var_class.append(self.rootgrpID.createVariable(rec_vars[0], rec_var_type[0], self.dim_vars[0]))#time1
        var_class.append(self.rootgrpID.createVariable(rec_vars[1], rec_var_type[1], self.dim_vars[1]))#depth
        var_class.append(self.rootgrpID.createVariable(rec_vars[2], rec_var_type[2], self.dim_vars[2]))#lat
        var_class.append(self.rootgrpID.createVariable(rec_vars[3], rec_var_type[3], self.dim_vars[3]))#lon
        
        for i, v in enumerate(rec_vars[4:]):  #1D coordinate variables
            var_class.append(self.rootgrpID.createVariable(rec_vars[i+4], rec_var_type[i+4], self.dim_vars))
            
        ### add variable attributes
        for i, v in enumerate(var_class): #4dimensional for all vars
            print ("Adding Variable {0}").format(v)#
            v.setncattr('name',rec_var_name[i])
            v.long_name = rec_var_longname[i]
            v.generic_name = rec_var_generic_name[i]
            v.FORTRAN_format = rec_var_FORTRAN[i]
            v.units = rec_var_units[i]
            v.type = rec_var_strtype[i]
            v.epic_code = rec_epic_code[i]
            
            
        self.var_class = var_class
        self.rec_vars = rec_vars

        
    def add_coord_data(self, depth=None, latitude=None, longitude=None, time=None, CastLog=False):
        """ """
        self.var_class[0][:] = time
        self.var_class[1][:] = depth
        self.var_class[2][:] = latitude
        self.var_class[3][:] = longitude #PMEL standard direction

    def add_data(self, data=None):
        """ """
        
        for ind, varname in enumerate(data.keys()):
            if not varname in ['time','time2','lat','lon','depth','latitude','longitude']:
                di = self.rec_vars.index(varname)
                self.var_class[di][:] = data[varname][:]
        

        
    def add_history(self, new_history):
        """Adds timestamp (UTC time) and history to existing information"""
        self.rootgrpID.History = self.rootgrpID.History + '\n' + datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")\
                    + ' ' + new_history + '\n'
                    
    def close(self):
        self.rootgrpID.close()

class CF_NC_2D(object):

    """ Class instance to generate a NetCDF file.  
    Assumes data format and information ingested is a dataframe object from ctd.py 

    Standards
    ---------
    EPICNetCDF (PMEL) Standards  


    Usage
    -----
    
    Order of routines matters and no error checking currently exists
    ToDo: Error Checking
    
    Use this to create a nc file with all default values
        ncinstance = CF_NC()
        ncinstance.file_create()
        ncinstance.sbeglobal_atts()
        ncinstance.dimension_init()
        ncinstance.variable_init()
        ncinstance.add_coord_data()
        ncinstance.add_data()
        ncinstance.close()
    """ 
    
    
    nc_format = 'NETCDF3_CLASSIC'
    nc_read   = 'w'
    def __init__(self, savefile='ncfiles/test.nc'):
        """data is a numpy array of temperature values"""
        
        self.savefile = savefile
    
    def file_create(self):
            rootgrpID = Dataset(self.savefile, CF_NC.nc_read, format=CF_NC.nc_format)
            self.rootgrpID = rootgrpID
            return ( rootgrpID )
        
    def sbeglobal_atts(self, raw_data_file='', Water_Mass='B', Water_Depth=9999, Prog_Cmnt='',\
                        Experiment='', Edit_Cmnt='', Station_Name='', Inst_Type='', Project='', History='',featureType=''):
        """
        Assumptions
        -----------
        
        Format of DataFrame.name = 'dy1309l1_ctd001'
        
        seabird related global attributes found in DataFrame.header list
        
        """
        
        self.rootgrpID.CREATION_DATE = datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")
        self.rootgrpID.COMPOSITE = 1
        self.rootgrpID.INST_TYPE = Inst_Type
        self.rootgrpID.DATA_CMNT = raw_data_file
        self.rootgrpID.EPIC_FILE_GENERATOR = 'nc_epic2udunits_time.py V' + __version__ 
        self.rootgrpID.PROG_CMNT01 = Prog_Cmnt
        self.rootgrpID.EDIT_CMNT01 = Edit_Cmnt
        self.rootgrpID.WATER_DEPTH = Water_Depth
        self.rootgrpID.MOORING = Station_Name
        self.rootgrpID.WATER_MASS = Water_Mass
        self.rootgrpID.EXPERIMENT = Experiment
        self.rootgrpID.PROJECT = Experiment
        self.rootgrpID.History = History
                        
        
    def dimension_init(self, time_len=1, depth_len=1):
        """
        Assumes
        -------
        Dimensions will be 'time', 'depth', 'lat', 'lon'
        
        Todo
        ----
        User defined dimensions
        """

        self.dim_vars = ['time', 'depth', 'lat', 'lon']
        
        self.rootgrpID.createDimension( self.dim_vars[0], time_len ) #time
        self.rootgrpID.createDimension( self.dim_vars[1], depth_len ) #depth
        self.rootgrpID.createDimension( self.dim_vars[2], 1 ) #lat
        self.rootgrpID.createDimension( self.dim_vars[3], 1 ) #lon
        
        
    def variable_init(self, nchandle, udunits_time_str='days since 1900-1-1' ):
        """
        built from knowledge about previous file
        """
        
        #build record variable attributes
        rec_vars, rec_var_name, rec_var_longname = [], [], []
        rec_var_generic_name, rec_var_FORTRAN, rec_var_units, rec_var_epic = [], [], [], []
        
        for v_name in nchandle.variables.keys():
            print v_name
            if not v_name in ['time','time2','depth','lat','lon','latitude','longitude']:
                print "Copying attributes for {0}".format(v_name)
                rec_vars.append( v_name )
                rec_var_name.append( nchandle.variables[v_name].name )
                rec_var_longname.append( nchandle.variables[v_name].long_name )
                rec_var_generic_name.append( nchandle.variables[v_name].generic_name )
                rec_var_units.append( nchandle.variables[v_name].units )
                rec_var_FORTRAN.append( nchandle.variables[v_name].FORTRAN_format )
                rec_var_epic.append( nchandle.variables[v_name].epic_code )

        
        rec_vars = ['time','depth','lat','lon'] + rec_vars

        rec_var_name = ['', '', '', ''] + rec_var_name
        rec_var_longname = ['', '', '', ''] + rec_var_longname
        rec_var_generic_name = ['', '', '', ''] + rec_var_generic_name
        rec_var_FORTRAN = ['', '', '', ''] + rec_var_FORTRAN
        rec_var_units = [udunits_time_str,'dbar','degree_north','degree_west'] + rec_var_units
        rec_var_type= ['f8'] + ['f4' for spot in rec_vars[1:]]
        rec_var_strtype= ['EVEN', 'UNEVEN', 'EVEN', 'EVEN'] + ['' for spot in rec_vars[4:]]
        rec_epic_code = [624,1,500,501] + rec_var_epic
        
        var_class = []
        var_class.append(self.rootgrpID.createVariable(rec_vars[0], rec_var_type[0], self.dim_vars[0]))#time1
        var_class.append(self.rootgrpID.createVariable(rec_vars[1], rec_var_type[1], self.dim_vars[1]))#depth
        var_class.append(self.rootgrpID.createVariable(rec_vars[2], rec_var_type[2], self.dim_vars[2]))#lat
        var_class.append(self.rootgrpID.createVariable(rec_vars[3], rec_var_type[3], self.dim_vars[3]))#lon
        
        for i, v in enumerate(rec_vars[4:]):  #1D coordinate variables
            var_class.append(self.rootgrpID.createVariable(rec_vars[i+4], rec_var_type[i+4], self.dim_vars))
            
        ### add variable attributes
        for i, v in enumerate(var_class): #4dimensional for all vars
            print ("Adding Variable {0}").format(v)#
            v.setncattr('name',rec_var_name[i])
            v.long_name = rec_var_longname[i]
            v.generic_name = rec_var_generic_name[i]
            v.FORTRAN_format = rec_var_FORTRAN[i]
            v.units = rec_var_units[i]
            v.type = rec_var_strtype[i]
            v.epic_code = rec_epic_code[i]
            
            
        self.var_class = var_class
        self.rec_vars = rec_vars

        
    def add_coord_data(self, depth=None, latitude=None, longitude=None, time=None, CastLog=False):
        """ """
        self.var_class[0][:] = time
        self.var_class[1][:] = depth
        self.var_class[2][:] = latitude
        self.var_class[3][:] = longitude #PMEL standard direction

    def add_data(self, data=None):
        """ """
        
        for ind, varname in enumerate(data.keys()):
            if not varname in ['time','time2','lat','lon','depth','latitude','longitude']:
                di = self.rec_vars.index(varname)
                self.var_class[di][:] = data[varname][:]
        

        
    def add_history(self, new_history):
        """Adds timestamp (UTC time) and history to existing information"""
        self.rootgrpID.History = self.rootgrpID.History + ' \n' + datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")\
                    + ' ' + new_history + '\n'
                    
    def close(self):
        self.rootgrpID.close()

class NetCDF_Create_Profile_Ragged1D(object):
    """ Class instance to generate a NetCDF file.  

    Standards
    ---------
    EPICNetCDF (PMEL) Standards  


    Usage
    -----
    
    Order of routines matters and no error checking currently exists
    ToDo: Error Checking
    
    Use this to create a nc file with all default values
        ncinstance = NetCDF_Create_Profile_Ragged1D()
        ncinstance.file_create()
        ncinstance.sbeglobal_atts()
        ncinstance.dimension_init()
        ncinstance.variable_init()
        ncinstance.add_coord_data()
        ncinstance.add_data()
        ncinstance.close()
    """ 
    
    
    nc_format = 'NETCDF3_CLASSIC'
    nc_read   = 'w'

    def __init__(self, savefile='data/test.nc'):
        """initialize output file path"""
        
        self.savefile = savefile
    
    def file_create(self):
            rootgrpID = Dataset(self.savefile, NetCDF_Create_Profile_Ragged1D.nc_read, 
                                format=NetCDF_Create_Profile_Ragged1D.nc_format)
            self.rootgrpID = rootgrpID
            return ( rootgrpID )
        
    def sbeglobal_atts(self, raw_data_file='', Water_Mass='', Water_Depth=9999, 
                       Experiment='', Station_Name='', SerialNumber='', 
                       Instrument_Type='', History='', Project='', featureType=''):
        """
        Assumptions
        -----------
        
        Format of DataFrame.name = 'dy1309l1_ctd001'
        
        seabird related global attributes found in DataFrame.header list
        
        """
        
        self.rootgrpID.CREATION_DATE = datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")
        self.rootgrpID.INST_TYPE = Instrument_Type
        self.rootgrpID.DATA_CMNT = raw_data_file
        self.rootgrpID.NC_FILE_GENERATOR = __file__.split('/')[-1] + ' ' + __version__ 
        self.rootgrpID.WATER_DEPTH = Water_Depth
        self.rootgrpID.MOORING = Station_Name
        self.rootgrpID.WATER_MASS = Water_Mass
        self.rootgrpID.EXPERIMENT = Experiment
        self.rootgrpID.PROJECT = Project
        self.rootgrpID.SERIAL_NUMBER = SerialNumber
        self.rootgrpID.History = History
        self.rootgrpID.featureType = featureType

    def dimension_init(self, recnum_len=1):
        """
        Assumes
        -------
        Dimensions will be 'record_number'
        
        Todo
        ----
        User defined dimensions
        """

        self.dim_vars = ['obs','id_strlen']
        
        self.rootgrpID.createDimension( self.dim_vars[0], recnum_len ) #recnumber
        self.rootgrpID.createDimension( self.dim_vars[1], 20 ) #recnumber
        
        
    def variable_init(self, EPIC_VARS_dict):
        """
        EPIC keys:
            passed in as a dictionary (similar syntax as json data file)
            The dictionary keys are what defines the variable names.
        """
        #exit if the variable dictionary is not passed
        if not bool(EPIC_VARS_dict):
            raise RuntimeError('Empty EPIC Dictionary is passed to variable_init.')

        #build record variable attributes
        rec_vars, rec_var_name, rec_var_longname = [], [], []
        rec_var_generic_name, rec_var_FORTRAN, rec_var_units, rec_var_epic = [], [], [], []

        #cycle through epic dictionary and create nc parameters
        for evar in EPIC_VARS_dict.keys():
            rec_vars.append(evar)
            rec_var_name.append( EPIC_VARS_dict[evar]['name'] )
            rec_var_longname.append( EPIC_VARS_dict[evar]['longname'] )
            rec_var_generic_name.append( EPIC_VARS_dict[evar]['generic_name'] )
            rec_var_units.append( EPIC_VARS_dict[evar]['units'] )
        
        rec_vars = ['record_number'] + rec_vars

        rec_var_name = [''] + rec_var_name
        rec_var_longname = [''] + rec_var_longname
        rec_var_generic_name = [''] + rec_var_generic_name
        rec_var_units = ['sequential measurement id'] + rec_var_units
        rec_var_type= ['f4'] + ['f4' for spot in rec_vars[1:]]
        
        var_class = []
        var_class.append(self.rootgrpID.createVariable(rec_vars[0], rec_var_type[0], self.dim_vars[0]))#time1

        for i, v in enumerate(rec_vars[1:]):  #1D coordinate variables
            var_class.append(self.rootgrpID.createVariable(rec_vars[i+1], rec_var_type[i+1], self.dim_vars))
            
        ### add variable attributes
        for i, v in enumerate(var_class): #4dimensional for all vars
            print ("Adding Variable {0}").format(v)#
            v.setncattr('name',rec_var_name[i])
            v.long_name = rec_var_longname[i]
            v.generic_name = rec_var_generic_name[i]
            v.units = rec_var_units[i]
            
        self.var_class = var_class
        self.rec_vars = rec_vars

        
    def add_coord_data(self, recnum=None):
        """ """
        self.var_class[0][:] = recnum

    def add_data(self, EPIC_VARS_dict, data_dic=None, missing_values=99999):
        """
            using the same dictionary to define the variables, and a new dictionary
                that associates each data array with an epic key, cycle through and populate
                the desired variables.  If a variable is defined in the epic keys but not passed
                to the add_data routine, it should be populated with missing data
        """
        #exit if the variable dictionary is not passed
        if not bool(EPIC_VARS_dict):
            raise RuntimeError('Empty EPIC Dictionary is passed to add_data.')
        
        #cycle through EPIC_Vars and populate with data - this is a comprehensive list of 
        # all variables expected
        # if no data is passed but an epic dictionary is, complete routine leaving variables
        #  with missing data if not found

        for EPICdic_key in EPIC_VARS_dict.keys():
            di = self.rec_vars.index(EPICdic_key)
            try:
                self.var_class[di][:] = data_dic[EPICdic_key]
            except KeyError:
                self.var_class[di][:] = missing_values
        
        
    def add_history(self, new_history):
        """Adds timestamp (UTC time) and history to existing information"""
        self.rootgrpID.History = self.rootgrpID.History + '\n' + datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")\
                    + ' ' + new_history
                    
    def close(self):
        self.rootgrpID.close()  

class NetCDF_Create_Profile_Ragged2D(object):
    """ Class instance to generate a NetCDF file.  

    Standards
    ---------
    EPICNetCDF (PMEL) Standards  


    Usage
    -----
    
    Order of routines matters and no error checking currently exists
    ToDo: Error Checking
    
    Use this to create a nc file with all default values
        ncinstance = NetCDF_Create_Profile_Ragged2D()
        ncinstance.file_create()
        ncinstance.sbeglobal_atts()
        ncinstance.dimension_init()
        ncinstance.variable_init()
        ncinstance.add_coord_data()
        ncinstance.add_data()
        ncinstance.close()
    """ 
    
    
    nc_format = 'NETCDF3_CLASSIC'
    nc_read   = 'w'

    def __init__(self, savefile='data/test.nc'):
        """initialize output file path"""
        
        self.savefile = savefile
    
    def file_create(self):
            rootgrpID = Dataset(self.savefile, NetCDF_Create_Profile_Ragged2D.nc_read, 
                                format=NetCDF_Create_Profile_Ragged2D.nc_format)
            self.rootgrpID = rootgrpID
            return ( rootgrpID )
        
    def sbeglobal_atts(self, raw_data_file='', Water_Mass='', Water_Depth=9999, 
                       Experiment='', Station_Name='', SerialNumber='', 
                       Instrument_Type='', History='', Project='', featureType=''):
        """
        Assumptions
        -----------
        
        Format of DataFrame.name = 'dy1309l1_ctd001'
        
        seabird related global attributes found in DataFrame.header list
        
        """
        
        self.rootgrpID.CREATION_DATE = datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")
        self.rootgrpID.INST_TYPE = Instrument_Type
        self.rootgrpID.DATA_CMNT = raw_data_file
        self.rootgrpID.NC_FILE_GENERATOR = __file__.split('/')[-1] + ' ' + __version__ 
        self.rootgrpID.WATER_DEPTH = Water_Depth
        self.rootgrpID.MOORING = Station_Name
        self.rootgrpID.WATER_MASS = Water_Mass
        self.rootgrpID.EXPERIMENT = Experiment
        self.rootgrpID.PROJECT = Project
        self.rootgrpID.SERIAL_NUMBER = SerialNumber
        self.rootgrpID.History = History
        self.rootgrpID.featureType = featureType
        
    def dimension_init(self, profilenum_len=1, obsnum_len=1):
        """
        Assumes
        -------
        Dimensions will be 'profile_number', 'obs_num'
        
        Todo
        ----
        User defined dimensions
        """

        self.dim_vars = ['profile_number', 'obs_num']
        
        self.rootgrpID.createDimension( self.dim_vars[0], profilenum_len ) #recnumber
        self.rootgrpID.createDimension( self.dim_vars[1], obsnum_len ) #obs per profile
        
        
    def variable_init(self, EPIC_VARS_dict):
        """
        EPIC keys:
            passed in as a dictionary (similar syntax as json data file)
            The dictionary keys are what defines the variable names.
        """
        #exit if the variable dictionary is not passed
        if not bool(EPIC_VARS_dict):
            raise RuntimeError('Empty EPIC Dictionary is passed to variable_init.')

        #build record variable attributes
        rec_vars, rec_var_name, rec_var_longname = [], [], []
        rec_var_generic_name, rec_var_FORTRAN, rec_var_units, rec_var_epic = [], [], [], []

        #cycle through epic dictionary and create nc parameters
        for evar in EPIC_VARS_dict.keys():
            rec_vars.append(evar)
            rec_var_name.append( EPIC_VARS_dict[evar]['name'] )
            rec_var_longname.append( EPIC_VARS_dict[evar]['longname'] )
            rec_var_generic_name.append( EPIC_VARS_dict[evar]['generic_name'] )
            rec_var_units.append( EPIC_VARS_dict[evar]['units'] )
        
        rec_vars = ['profile_number','observation_number'] + rec_vars

        rec_var_name = ['',''] + rec_var_name
        rec_var_longname = ['',''] + rec_var_longname
        rec_var_generic_name = ['',''] + rec_var_generic_name
        rec_var_units = ['sequential profile id', 'sequential observation id'] + rec_var_units
        rec_var_type= ['f4', 'f4'] + ['f4' for spot in rec_vars[2:]]
        
        var_class = []
        var_class.append(self.rootgrpID.createVariable(rec_vars[0], rec_var_type[0], self.dim_vars[0]))
        var_class.append(self.rootgrpID.createVariable(rec_vars[1], rec_var_type[1], self.dim_vars[1]))

        for i, v in enumerate(rec_vars[2:]):  #1D coordinate variables
            var_class.append(self.rootgrpID.createVariable(rec_vars[i+2], rec_var_type[i+2], self.dim_vars))
            
        ### add variable attributes
        for i, v in enumerate(var_class): #4dimensional for all vars
            print ("Adding Variable {0}").format(v)#
            v.setncattr('name',rec_var_name[i])
            v.long_name = rec_var_longname[i]
            v.generic_name = rec_var_generic_name[i]
            v.units = rec_var_units[i]
            
        self.var_class = var_class
        self.rec_vars = rec_vars

        
    def add_coord_data(self, profile_num=None, obs_num=None):
        """ """
        self.var_class[0][:] = profile_num
        self.var_class[1][:] = obs_num

    def add_data(self, EPIC_VARS_dict, profile_num=None, data_dic=None, missing_values=99999):
        """
            using the same dictionary to define the variables, and a new dictionary
                that associates each data array with an epic key, cycle through and populate
                the desired variables.  If a variable is defined in the epic keys but not passed
                to the add_data routine, it should be populated with missing data
        """
        #exit if the variable dictionary is not passed
        if not bool(EPIC_VARS_dict):
            raise RuntimeError('Empty EPIC Dictionary is passed to add_data.')
        
        #cycle through EPIC_Vars and populate with data - this is a comprehensive list of 
        # all variables expected
        # if no data is passed but an epic dictionary is, complete routine leaving variables
        #  with missing data if not found

        for EPICdic_key in EPIC_VARS_dict.keys():
            di = self.rec_vars.index(EPICdic_key)
            print "adding data for {EPICdic_key}".format(EPICdic_key=EPICdic_key)
            ragged_ind = np.where(~np.isnan(data_dic[EPICdic_key]))[0]
            try:
                self.var_class[di][profile_num,ragged_ind] = np.array(data_dic[EPICdic_key])[ragged_ind]
            except KeyError:
                pass
            except IndexError:
                pass
            print "done"
        
    def add_history(self, new_history):
        """Adds timestamp (UTC time) and history to existing information"""
        self.rootgrpID.History = self.rootgrpID.History + '\n' + datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")\
                    + ' ' + new_history
                    
    def close(self):
        self.rootgrpID.close()  