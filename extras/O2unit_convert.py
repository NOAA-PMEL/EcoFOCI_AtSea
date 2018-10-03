#!/usr/bin/env python

"""
Background:
===========
O2unit_convert.py

Convert ml/l to Mm/kg or vice versa

Used for discreet oxygen samples from Mordy

History:
=======

2018-04-25 S.Bell: CORRECTED.  Use dens insted of pden and dens0 for general corrections.
    (should be pretty small correction). (maybe potential density is more appropiate but I
    can't find the reference)
  Make sure proper variables are being passed into TEOS routines

2017-03-23 S.Bell: update to use Pandas for excel read

Compatibility:
==============
python >=3.6 - Not Tested
python 2.7 

"""
import warnings
#remove the numpy/pandas/cython warnings
warnings.filterwarnings(action='ignore', message="numpy.dtype size changed,")

#System Stack
import datetime
import argparse

#Science Stack
import pandas as pd
import seawater as sw

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 10, 30)
__modified__ = datetime.datetime(2017, 03, 23)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'CTD', 'SeaWater', 'Cruise', 'derivations'

"""----------------------------- Density Correction ------------------------"""
def O2_conv(S,T,P,O2conc):
    """sal, temp, press, oxy conc"""
    sigmatheta_pri = sw.eos80.dens(s=S, t=T, p=P)
    density = (sigmatheta_pri / 1000)
    O2conc = O2conc / density
    return O2conc

"""----------------------------- Main -------------------------------------"""
parser = argparse.ArgumentParser(description='Discreet Oxygen Unit Conversion')
parser.add_argument('DataPath', metavar='DataPath', type=str,
               help='full path to file')
parser.add_argument('sheetname', metavar='sheetname', type=str,
               help='sheetname in excel file')
parser.add_argument('-p','--primary', action="store_true",
               help='primary instruments')
parser.add_argument('-s','--secondary', action="store_true",
               help='secondary instruments')                  
args = parser.parse_args()

df = pd.read_excel(args.DataPath, sheetname=args.sheetname)

print "umol/l to umol/kg \n"
for i in df.index:
    if args.primary:
        print(O2_conv(S=df.Sal00[i],T=df.T090C[i],P=df.PrDM[i],O2conc=df['O2 (uM/l)'][i]))
    if args.secondary:
        print(O2_conv(S=df.Sal11[i],T=df.T190C[i],P=df.PrDM[i],O2conc=df['O2 (uM/l)'][i]))
        
print "sigma-t"
for i in df.index:
    if args.primary:
        print(sw.eos80.dens(s=df.Sal00[i],t=df.T090C[i])-1000.)
    if args.secondary:
        print(sw.eos80.dens(s=df.Sal11[i],t=df.T190C[i])-1000. )  