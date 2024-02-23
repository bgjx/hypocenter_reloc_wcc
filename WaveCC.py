import os
import obspy
from obspy import read
from obspy.signal.cross_correlation import xcorr_pick_correction
import matplotlib.pyplot as plt
import glob
import numpy as np
import pandas as pd
import warnings
import time
from pathlib import PurePath, Path
from loguru import logger

print('''
Python code for waveform cross correlation 

Before you run this program, make sure you have changed all the path and set the necessary parameters correctly      
      ''')
      
# List of functions 
#============================================================================================
# function to read catalog picking data
def readcatalog(catalogfile):
    catalog = pd.read_excel(catalogfile, index_col = None)
    catalog = catalog.replace('NaN', np.nan)
    catalog = catalog.replace(np.nan, 9999)  # to ease filtering blank S information
    return catalog

# function to get event and station pairs
def pair(dtct):
    """
    make pair of event and station based on dt.ct
    :param dtct:
    :return:

    """
    f = open(dtct,'r').readlines()
    evpair, stpair, dt1, dt2, phase, dt = [], [], [], [], [], []
    for i in range(len(f)):
        if f[i][0] == '#':
            id1 = f[i].split()[1]
            id2 = f[i].split()[2]
            evpair.append([id1, id2])  # make event pair array
            j = 1
            st, ph = [], []
            while f[i + j][0] != '#' and i + j < len(f) - 1:  # make station pair array
                st.append(f[i + j].split()[0])
                dt1.append(f[i + j].split()[1])
                dt2.append(f[i + j].split()[2])
                ph.append(f[i + j].split()[4])
                j = j + 1
            # st = np.unique(st)
            stpair.append(st)
            dt.append([dt1, dt2])
            phase.append(ph)
    return(evpair,stpair,dt,phase)

# function to get the arrival time of master event in a pair
def arrival_master(catalog, evpair, stpair, i, j):
    """
    read event information and then assign arrival p and s in obspy UTM format 

    """
    year      = int(catalog['Year'][(catalog['Event ID'] == int(evpair[i][0])) & (catalog['Station'] == stpair[i][j])])
    month     = int(catalog['Month'][(catalog['Event ID'] == int(evpair[i][0])) & (catalog['Station'] == stpair[i][j])])
    day       = int(catalog['Day'][(catalog['Event ID'] == int(evpair[i][0])) & (catalog['Station'] == stpair[i][j])])
    hour      = int(catalog['Hour'][(catalog['Event ID'] == int(evpair[i][0])) & (catalog['Station'] == stpair[i][j])])
    minutes_p = int(catalog['Minutes_P'][(catalog['Event ID'] == int(evpair[i][0])) & (catalog['Station'] == stpair[i][j])])
    minutes_s   = int(catalog['Minutes_S'][(catalog['Event ID'] == int(evpair[i][0])) & (catalog['Station'] == stpair[i][j])])
    seconds_p   = float(catalog['P_Arr_Sec'][(catalog['Event ID'] == int(evpair[i][0])) & (catalog['Station'] == stpair[i][j])])
    seconds_s   = float(catalog['S_Arr_Sec'][(catalog['Event ID'] == int(evpair[i][0])) & (catalog['Station'] == stpair[i][j])])
    
    tp = obspy.UTCDateTime("{0}-{1}-{2}T{3}:{4}:{5}Z".format(year, month, day, hour, minutes_p, seconds_p))
    if seconds_s != 9999:
        ts = obspy.UTCDateTime("{0}-{1}-{2}T{3}:{4}:{5}Z".format(year, month, day, hour, minutes_s, seconds_s))
    else:
        ts = 9999
    return tp, ts

# function to get the arrival time of slave event in a pair
def arrival_pair(catalog, evpair, stpair, i, j):
    """
    read event information and then assign arrival p and s in obspy UTM format

    """
    year    = int(catalog['Year'][(catalog['Event ID'] == int(evpair[i][1])) & (catalog['Station'] == stpair[i][j])])
    month   = int(catalog['Month'][(catalog['Event ID'] == int(evpair[i][1])) & (catalog['Station'] == stpair[i][j])])
    day     = int(catalog['Day'][(catalog['Event ID'] == int(evpair[i][1])) & (catalog['Station'] == stpair[i][j])])
    hour    = int(catalog['Hour'][(catalog['Event ID'] == int(evpair[i][1])) & (catalog['Station'] == stpair[i][j])])
    minutes_p = int(catalog['Minutes_P'][(catalog['Event ID'] == int(evpair[i][1])) & (catalog['Station'] == stpair[i][j])])
    minutes_s = int(catalog['Minutes_S'][(catalog['Event ID'] == int(evpair[i][1])) & (catalog['Station'] == stpair[i][j])])
    seconds_p = float(catalog['P_Arr_Sec'][(catalog['Event ID'] == int(evpair[i][1])) & (catalog['Station'] == stpair[i][j])])
    seconds_s = float(catalog['S_Arr_Sec'][(catalog['Event ID'] == int(evpair[i][1])) & (catalog['Station'] == stpair[i][j])])

    tp = obspy.UTCDateTime("{0}-{1}-{2}T{3}:{4}:{5}Z".format(year, month, day, hour, minutes_p, seconds_p))
    if seconds_s != 9999:
        ts = obspy.UTCDateTime("{0}-{1}-{2}T{3}:{4}:{5}Z".format(year, month, day, hour, minutes_s, seconds_s))
    else:
        ts = 9999
    return tp, ts

# function to read waveform data (vertical/z component)
def waveform_z(wavepath, evpair, stpair, i, j):
    """
    extract vertical-component waveform of master and pair event

    """
    stream1 = read(wavepath.joinpath("{0}\\*{1}*".format(evpair[i][0], stpair[i][j])))  # read event master waveform
    stream2 = read(wavepath.joinpath("{0}\\*{1}*".format(evpair[i][1], stpair[i][j])))  # read event pair waveform

    # print(stream1.select(station=stpair[i][j])[0].stats.sampling_rate)
    # print(stream1.select(station=stpair[i][j])[0].stats.channel)

    # resample the waveform
    if stream1.select(station=stpair[i][j])[0].stats.sampling_rate !=200:
        stream1.interpolate(sampling_rate = 250)
    if stream2.select(station=stpair[i][j])[0].stats.sampling_rate !=200:
        stream2.interpolate(sampling_rate = 250)

    # pick the component
    if stream1.select(station=stpair[i][j])[0].stats.channel == '1':
        master = stream1.select()[0]
    else:
        master = stream1.select(component='Z')[0]
    if stream2.select(station=stpair[i][j])[0].stats.channel == '1':
        pair = stream2.select()[0]
    else:
        pair = stream2.select(component='Z')[0]
    return master, pair

# function to read waveform data (horizontal/n component)
def waveform_n(wavepath, evpair, stpair, i, j):
    """
    extract horizontal-component waveform of master and pair event

    """
    stream1 = read(wavepath.joinpath("{0}\\*{1}*".format(evpair[i][0], stpair[i][j])))  # read event master waveform
    stream2 = read(wavepath.joinpath("{0}\\*{1}*".format(evpair[i][1], stpair[i][j])))  # read event pair waveform
    
   

    # print(stream1.select(station=stpair[i][j])[0].stats.sampling_rate)
    # print(stream1.select(station=stpair[i][j])[0].stats.channel)

    # resample the waveform
    if stream1.select(station=stpair[i][j])[0].stats.sampling_rate != 200:
        stream1.interpolate(sampling_rate=250)
    if stream2.select(station=stpair[i][j])[0].stats.sampling_rate != 200:
        stream2.interpolate(sampling_rate=250)

    # pick the component
    if stream1.select(station=stpair[i][j])[0].stats.channel == '1':
        master = stream1.select()[1]
    else:
        master = stream1.select(component='N')[0]
    if stream2.select(station=stpair[i][j])[0].stats.channel == '1':
        pair = stream2.select()[1]
    else:
        pair = stream2.select(component='N')[0]

    return master, pair
 
# End of functions 
#============================================================================================

if __name__ == "__main__":
    starttime = time.time()
    warnings.filterwarnings("ignore") #ignore warnings such as low coefficient value or lack of number of sample
    
    # setting logger for debugging 
    logger.add("runtime.log", level="ERROR", backtrace=True, diagnose=True)
    
    # initialize input and output path
    catalogfile = Path(r"F:\SEML\DATA WCC\2023\2023_09_full_test.xlsx")
    dtct        = Path(r"F:\SEML\DATA WCC\2023\dt_09.ct")
    wavepath    = Path(r"F:\SEML\DATA TRIMMING\EVENT DATA TRIM\2023\COMBINED")
    outputfile  = Path(r"F:\SEML\DATA WCC\2023\result_test.csv")
   
    # reading file input
    catalog = readcatalog(catalogfile)       # read catalog
    evpair, stpair, dt, phase = pair(dtct)   # read dt.ct to make an array of event pair and station pair
    
    # predefined parameters
    low_bp = 1.0   #define bandpass filter boundary
    high_bp = 15.0   #define bandpass filter boundary

    # preparing the variable
    tp_master, ts_master, tp_pair, ts_pair, lagtime, coeff = [], [], [], [], [], []
    station, event, fase, dtpair = [], [], [], []

    # correlate waveform in each paired station of paired event
    for i in range(len(evpair)):  # range(len(evpair)):
        for j in range(len(stpair[i])):
            tp1, ts1 = arrival_master(catalog, evpair, stpair, i, j)
            tp2, ts2 = arrival_pair(catalog, evpair, stpair, i, j)
            tp_master.append(tp1), ts_master.append(ts1), tp_pair.append(tp2), ts_pair.append(ts2)
            try:
                if phase[i][j] == 'P':
                    print('Correlating p-wave for event {0} and {1} ...'.format(evpair[i][0], evpair[i][1]))
                    master, pair = waveform_z(wavepath, evpair, stpair, i, j)
                    lag, c = xcorr_pick_correction(tp1, master, tp2, pair, 0.05, 0.2, 0.2, plot=False,
                                                   filter="bandpass", filter_options={'freqmin': low_bp, 'freqmax': high_bp})
                else:
                    if ts1 != 9999 and ts2 != 9999:
                        print('Correlating s-wave for event {0} and {1} ...'.format(evpair[i][0], evpair[i][1]))
                        master, pair = waveform_n(wavepath, evpair, stpair, i, j)
                        lag, c = xcorr_pick_correction(ts1, master, ts2, pair, 0.05, 0.2, 0.2,plot=False,
                                                       filter="bandpass", filter_options={'freqmin': low_bp, 'freqmax': high_bp})
                    else:
                        lag, c = np.nan, np.nan
            except Exception as e:
                logger.exception("An error occured during runtime:", str(e))
                continue

            # assign the informations to an array
            station.append(stpair[i][j]), lagtime.append(lag)
            coeff.append(c), fase.append(phase[i][j])
            event.append([evpair[i][0], evpair[i][1]])
            dtpair.append([dt[i][0][j], dt[i][1][j]])
    print('Done\n')

    # make dataframe to tabulate data
    print('Making data table ...')
    df = pd.DataFrame({'master':[i[0] for i in event], 'pair':[i[1] for i in event],
                       'station':station,'lagtime':lagtime, 'coefficient':coeff,
                       'phase':fase, 'ttmaster':[i[0] for i in dtpair],
                       'ttpair':[i[1] for i in dtpair],
                       'dt':[float(i[1])-float(i[0]) for i in dtpair]})
    print('Done\n')
    df.to_csv(outputfile, index=False)

    e = int(time.time() - starttime)
    print('Time elapsed = {:02d}:{:02d}:{:02d}'.format(e // 3600, (e % 3600 // 60), e % 60))
    print('-----------  The code has run succesfully! --------------')

