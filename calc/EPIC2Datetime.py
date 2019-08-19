# filename: EPIC2Datetime.py
r"""Module to convert PMEL-EPIC timeword to a python datetime 

    Modifications
    -------------
    2018-07-17: SBELL - force numpy ints to be datetime compliant
    2018-06-19: SBELL - make python3 compliant
    2016-11-14: SBELL - create routine to add datetime offset

"""
import datetime
from netCDF4 import date2num

__author__ = "Shaun Bell"
__email__ = "shaun.bell@noaa.gov"
__created__ = datetime.datetime(2016, 7, 21)
__modified__ = datetime.datetime(2016, 7, 21)
__version__ = "0.2.1"
__status__ = "Development"


def EPIC2Datetime(timeword_1, timeword_2):
    r""" 

    PMEL-EPIC time stored in NetCDF files is defined as two timewords: time, time2.  
        The first (time) represents "True Julian Day", 
        the second (time2) is "msec since 0:00 GMT"

        This allowed for integer representation of millisecond resolution 
        (without fear of floating point rounding issues) but is rarely encountered
        in data that his one minute or sparser resolution.

        The usage of two timewords for dimensions is not advised 
        (example above, time2 is a periodic value not well-suited for a dimension)

        It is not supported by current CF convention which specifies using numeric values to represent:
        "seconds since 2001-1-1 0:0:0" or "days since 2001-1-1 0:0:0" or "{units} since {initial date}"
        as there is not reference date explicitly stated nor is there a calendar mentioned.

    This routine will convert an EPIC two-time word value to a python datetime in order to ease
    the usage with NetCDF date2num utility (for CF and COARDS conventions)


    Parameters
    ----------
    timeword_1 : array_like
         first EPIC timeword (time)
    timeword_2 : array-like
         second EPIC timeword (time2)
    
    Returns
    -------
    Outputs : array_like
              Python datetime structure representing the EPIC datetime
        
    Notes
    -----
    TODO
    
    Examples
    --------
    TODO
    
    References
    ----------
    ftp://ftp.unidata.ucar.edu/pub/netcdf/Conventions/PMEL-EPIC/Conventions

    As long as this document survives.  It defines the conventions of the PMEL-EPIC standard.
    A misprint exists that specifies a reference date of 1968-05-23 as 2400000 when it should be 2440000
    
    http://aa.usno.navy.mil/data/docs/JulianDate.php

    Converts the "true julian date" and confirms the misprint in the documentation.

    (Note: the US Naval site above uses seconds since 12:00 UTC whereas EPIC uses seconds since 00:00 UTC)
    

    """

    # We can used the defined date from the conventions
    # 1968-05-23 => 2440000
    # 4713-01-01 BCE => 0 (be aware that this uses the julian calendar not the gregorian or mixed
    #   and may result in a 10 day error if the calendar is not appropriately identified)
    #
    # Using a more modern reference date skips this problem and is sufficient if the dates of all data
    #   are after 1582.

    ref_time_dt = datetime.datetime(1968, 5, 23)
    ref_time_epic = 2440000

    delta_days = [x - ref_time_epic for x in timeword_1]
    delta_seconds = [x / 1000 for x in timeword_2]

    epic_dt = [
        ref_time_dt + datetime.timedelta(int(a), int(c))
        for a, c in zip(delta_days, delta_seconds)
    ]

    return epic_dt


def get_UDUNITS(epic_dt, time_since_str="days since 1900-1-1"):
    """Using netCDF4.date2num (also available in matplotlib) to convert a datetime to a time since reference date.
    {units} since {yyyy-mm-dd}

    Parameters
    ----------
    epic_dt : array_like
         list of EPIC times in datetime structure
    time_since_str : str
         string to represent {units} since {reference date}: eg days since 1981-08-31

    Returns
    -------
    Outputs : array_like
              numerical value of date since reference time in units specified

    Notes
    -----

    See netCDF4.date2num for full examples.  This program is just a wrapper to provide a fixed
    string date in case not provided.
    """
    udnum = date2num(epic_dt, time_since_str)
    return udnum


def Datetime2EPIC(epic_dt):
    r"""
    Convert a datetime object into a PMEL-EPIC two word time value.  

    PMEL-EPIC time stored in NetCDF files is defined as two timewords: time, time2.  
        The first (time) represents "True Julian Day", 
        the second (time2) is "msec since 0:00 GMT"

    Parameters
    ----------
    epic_dt : array of datetime objects
              Python datetime structure representing the EPIC datetime

    
    Returns
    -------
    Outputs : array_like    (time, time1)
              time: array of integer values representing true julian day
              time1: array of integer values representing milliseconds since 00:00 UTC

    """

    ref_time_py = datetime.datetime.toordinal(datetime.datetime(1968, 5, 23))
    ref_time_epic = 2440000
    offset = ref_time_epic - ref_time_py

    if not isinstance(epic_dt, list):
        time = offset + epic_dt.toordinal()
        time1 = int(
            (epic_dt.hour * (60.0 * 60.0 * 1000.0))
            + (epic_dt.minute * (60.0 * 1000.0))
            + (epic_dt.second * (1000.0))
        )
    else:
        time = [offset + x.toordinal() for x in epic_dt]
        time1 = [
            int(
                (x.hour * (60.0 * 60.0 * 1000.0))
                + (x.minute * (60.0 * 1000.0))
                + (x.second * (1000.0))
            )
            for x in epic_dt
        ]

    return (time, time1)


"""------------------------------------------------------------------------------------------------"""


def main():
    pass


def test_1d():
    testdate = EPIC2Datetime([2440000], [43200000 + 3600 * 1000])
    print("\n{0}\n".format(testdate))
    for time_format in ["days", "hours", "seconds"]:
        time_since_str = time_format + " since 1900-1-1"
        print(
            "{0}:value \n{1}:units\n".format(
                get_UDUNITS(testdate, time_since_str), time_since_str
            )
        )


def test_2d():
    testdate = EPIC2Datetime([2440000, 2450000], [43200000, 0])
    print("\n{0}\n".format(testdate))
    for time_format in ["days", "hours", "seconds"]:
        time_since_str = time_format + " since 1900-1-1"
        print(
            "{0}:value \n{1}:units\n".format(
                get_UDUNITS(testdate, time_since_str), time_since_str
            )
        )


def test_1d_EPIC():
    testdate = EPIC2Datetime([2440000], [43200000 + 3600 * 1000])
    print(testdate)
    testdate1 = Datetime2EPIC(testdate)
    print(testdate1)


def test_2d_EPIC():
    testdate = EPIC2Datetime([2440000, 2450000], [43200000, 0])
    prin(testdate)
    testdate1 = Datetime2EPIC(testdate)
    prin(testdate1)


if __name__ == "__main__":
    main()
