#!/usr/bin/env

"""
CTD_isosfc_map.py

Generates png map of isosurface for all casts in a designated cruise

 History
 =======

 2018-07-13: Make python3 compliant

 Compatibility:
 ==============
 python >=3.6 
 python 2.7 

"""

from __future__ import (absolute_import, division, print_function)

#System Stack
import datetime
import argparse
import os
import sys

#Science Stack
import numpy as np
from netCDF4 import Dataset

# Plotting Stack
import matplotlib as mpl
mpl.use('Agg')
from mpl_toolkits.basemap import Basemap, shiftgrid
import matplotlib.pyplot as plt
import matplotlib as mpl



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

"""--------------------------------time Routines---------------------------------------"""

def date2pydate(file_time, file_time2=None, file_flag='EPIC'):

    if file_flag == 'EPIC':
        ref_time_py = datetime.datetime.toordinal(datetime.datetime(1968, 5, 23))
        ref_time_epic = 2440000
    
        offset = ref_time_epic - ref_time_py
    
       
        try: #if input is an array
            python_time = [None] * len(file_time)

            for i, val in enumerate(file_time):
                pyday = file_time[i] - offset 
                pyfrac = file_time2[i] / (1000. * 60. * 60.* 24.) #milliseconds in a day
        
                python_time[i] = (pyday + pyfrac)

        except:
    
            pyday = file_time - offset 
            pyfrac = file_time2 / (1000. * 60. * 60.* 24.) #milliseconds in a day
        
            python_time = (pyday + pyfrac)
        
    else:
        print("time flag not recognized")
        sys.exit()
        
    return np.array(python_time)    
    
"""------------------------------------- MAPS -----------------------------------------"""

def etopo5_data():
    """ read in etopo5 topography/bathymetry. """
    file = '../data/etopo5.nc'
    etopodata = Dataset(file)
    
    topoin = etopodata.variables['bath'][:]
    lons = etopodata.variables['X'][:]
    lats = etopodata.variables['Y'][:]
    etopodata.close()
    
    topoin,lons = shiftgrid(0.,topoin,lons,start=False) # -360 -> 0
    
    #lons, lats = np.meshgrid(lons, lats)
    
    return(topoin, lats, lons)


def find_nearest(a, a0):
    "Element in nd array `a` closest to the scalar value `a0`"
    idx = np.abs(a - a0).argmin()
    return idx
        
"""------------------------------------- Main -----------------------------------------"""

# parse incoming command line options
parser = argparse.ArgumentParser(description='Create map of isosurface contours for a designated cruise')
parser.add_argument('sourcedir', metavar='sourcedir', type=str, help='path to cruise ctd cast files (.nc)')
parser.add_argument('-ek','--EPIC_KEY', type=str, help='selected variable to contour')
parser.add_argument('--Depth', type=int, help='integer depth to contour at')

args = parser.parse_args()

## get list of all files in directory
ctd_data_files = [x for x in os.listdir(args.sourcedir) if x.endswith('.nc')]
ctd_data_files = sorted(ctd_data_files)
           
### Basemap Visualization

#cycle though list of provided ctd's
isemptydata = True
ctd_data = {}
for count, ncfile in enumerate(ctd_data_files): #cycle through all available files for an id
    print("Working on file {0}".format(args.sourcedir + ncfile))
    print("Retreiving {0} at {1} dBar".format(args.EPIC_Key, args.Depth))
    ###nc readin
    nchandle = Dataset(args.sourcedir + ncfile,'a')
    vars_dic = get_vars(nchandle)
    data = ncreadfile_dic(nchandle,vars_dic)
    nchandle.close()

    ctd_data[count] = {'value':data[args.EPIC_Key][0,args.Depth,0,0],
                        'lat':data['lat'],'lon':data['lon'],'depth':data['dep'][args.Depth],
                        'pydate':date2pydate(data['time'],data['time2'])}

#parse data out for plotting
lat = [ctd_data[x]['lat'] for x in ctd_data.keys()]
lat = np.array(lat)
lon = [ctd_data[x]['lon'] for x in ctd_data.keys()]
lon = np.array(lon)
value = [ctd_data[x]['value'] for x in ctd_data.keys()]
value = np.array(value)
pydate = [ctd_data[x]['pydate'] for x in ctd_data.keys()]
pydate = np.array(pydate)

                                
## plot boundaries for topography
(topoin, elats, elons) = etopo5_data()

#build regional subset of data
topoin = topoin[find_nearest(elats,lat.min()-5):find_nearest(elats,lat.max()+5),find_nearest(elons,-1*(lon.max()+5)):find_nearest(elons,-1*(lon.min()-5))]
elons = elons[find_nearest(elons,-1*(lon.max()+5)):find_nearest(elons,-1*(lon.min()-5))]
elats = elats[find_nearest(elats,lat.min()-5):find_nearest(elats,lat.max()+5)]

print("Generating image")

#determine regional bounding
y1 = np.floor(lat.min()-1)
y2 = np.ceil(lat.max()+1)
x1 = np.ceil(-1*(lon.max()+4))
x2 = np.floor(-1*(lon.min()-5))

fig1 = plt.figure(1)
#Custom adjust of the subplots
ax = plt.subplot(1,1,1)

        
m = Basemap(resolution='i',projection='merc', llcrnrlat=y1, \
            urcrnrlat=y2,llcrnrlon=x1,urcrnrlon=x2,\
            lat_ts=45)

elons, elats = np.meshgrid(elons, elats)
x, y = m(-1. * lon,lat)
ex, ey = m(elons, elats)

m.drawcountries(linewidth=0.5)
m.drawcoastlines(linewidth=0.5)
#m.drawparallels(np.arange(y1,y2,2.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
#m.drawmeridians(np.arange(x1-20,x2,2.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
m.drawparallels(np.arange(y1,y2,2.),labels=[0,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
m.drawmeridians(np.arange(x1-20,x2,2.),labels=[0,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
m.fillcontinents(color='white')


m.contourf(ex,ey,topoin, levels=[-80 , -60, -40, -20, ], colors=('#737373','#969696','#bdbdbd','#d9d9d9','#f0f0f0'), extend='both', alpha=.75)
m.scatter(x,y,40,marker='.', edgecolors='none', c=value, vmin=-2, vmax=10, cmap='jet')
#c = plt.colorbar()
#c.set_label("")


f = plt.gcf()
DefaultSize = f.get_size_inches()
f.set_size_inches( (DefaultSize[0], DefaultSize[1]) )
plt.savefig('images/CTD_isosurface' + args.EPIC_Key + '_' + str(args.Depth) + 'db.png', bbox_inches='tight', dpi=300)
plt.close()

