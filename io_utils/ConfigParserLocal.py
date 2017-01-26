#!/usr/bin/env

"""
 Background:
 --------
 ConfigParserLocal.py
 
 
 Purpose:
 --------
 Parse mooring specific and EcoFOCI specific configuration files for various routines

 The .pyini files are JSON formatted
 The .yaml files are YAML formatted

 Modifications:
 --------------

 2016-09-16: SW Bell - Add support for parsing yaml files and translating between yaml and json/pyini

  

"""

#System Stack
import json
import yaml

def get_config(infile):
    """ Input - full path to config file
    
        Output - dictionary of file config parameters
    """
    infile = str(infile)
    
    try:
        d = json.load(open(infile))
    except:
        raise RuntimeError('{0} not found'.format(infile))
        
    return d
    
def write_config(infile, d):
    """ Input - full path to config file
        Dictionary of parameters to write
        
        Output - None
    """
    infile = str(infile)
    
    try:
        d = json.dump(d, open(infile,'w'), sort_keys=True, indent=4)
    except:
        raise RuntimeError('{0} not found'.format(infile))
        

def get_config_yaml(infile):
    """ Input - full path to config file
    
        Output - dictionary of file config parameters
    """
    infile = str(infile)
    
    try:
        d = yaml.load(open(infile))
    except:
        raise RuntimeError('{0} not found'.format(infile))
        
    return d

def write_config_yaml(infile, data, default_flow_style=False):
    """ Input - full path to config file
        Dictionary of parameters to write
        
        Output - None
    """
    infile = str(infile)
    
    try:
        data = yaml.safe_dump(data, open(infile,'w'), default_flow_style)
    except:
        raise RuntimeError('{0} not found'.format(infile))

def pyini2yaml(infile, default_flow_style=False):
    """ Input - full path to config file
    
        Output - dictionary of file config parameters
    """
    infile = str(infile)
    
    try:
        d = yaml.safe_dump(json.load(open(infile)), default_flow_style)

    except:
        raise RuntimeError('{0} not found'.format(infile))
        
    return d