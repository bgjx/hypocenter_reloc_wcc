#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  3 19:21:24 2021

@author : ARHAM ZAKKI EDELO
@contact: edelo.arham@gmail.com
"""
from collections import defaultdict as dfdict
from obspy import UTCDateTime
from pathlib import PurePath, Path
import pandas as pd

print('''
This code is used for formating NonLinLoc output to ph2dt input format.

Please read the hypoDD documentation for complete data format information.
''')

def weighting_generator (pick_data, id_start, id_end, weight_statement ):
    # data handler
    pick_handler = pick_data[(pick_data["Event ID"] >= id_start) & (pick_data["Event ID"] <= id_end)]
    
    # list of station 
    list_station = ['ML01','ML02','ML03','ML04','ML05','ML06','ML07','ML08','ML09','ML10','ML11','ML12','ML13','ML14','ML15']
    
    # initialize an empty list dict
    station_dict = dfdict(list)
    
    # create dict holder for all complete stations ==> dict structture {"ML01 P:"[total,weighting]}
    for x in range(0, len(list_station)):
            station_dict[f"{list_station[x]} P"] = [0,0]
            station_dict[f"{list_station[x]} S"] = [0,0]
    dio = station_dict # aliasing
    
    # calculate number of pick recorded by each station
    for sta in list(pick_handler.get("Station")):
        if sta in list_station:
            dio[f"{sta} P"][0] += 1
            dio[f"{sta} S"][0] += 1
    
    # start weighting 
    print ('--------------------------------------------------\n\n',
        " Total phase for each station: \n")
    for xx in sorted(list(dio.keys())):
        print(f"{xx} : {dio[xx][0]} ")
    if not weight_statement == "yes":
        print("\n\n",
                "Input the weighting value for each station",
                "\n\n")
    for yy in sorted(list(dio.keys())):
        if dio[yy][0] > 0:
            if weight_statement == "yes":
                weight_value = 1.000
            else:
                print('For station', yy)
                weight_value = float(input('Please input number for weighting value (between 0(worst) - 1(best)): \n'))
            dio[yy][1] = weight_value
    return dio

if __name__== "__main__":
    # initialize input and output path
    hypo_input  = Path(r"F:\SEML\CATALOG HYPOCENTER\catalog\hypo_init.xlsx") # relocated catalog
    pick_input  = Path(r"F:\SEML\DATA PICKING MEQ\DATA PICK 2023\PICK 2023 09\2023_09_full_test.xlsx") # catalog picking
    phase_out   = Path(r"F:\SEML\DD RELOCATION\ph2dt") # output path
    
    # dynamic input
    ID_start       = int(input("Event's ID to start the conversion process : "))
    ID_end         = int(input("Event's ID to end the conversion process : "))
    out_name       = input("Output phase file name (ex. ML_november) :" )
    weight_input   = str(input("type yes if you want to set default pick weight to 1.000, or no for manual input:"))

    # loading file input
    hypo_data    = pd.read_excel(hypo_input, index_col = None) 
    pick_data    = pd.read_excel(pick_input, index_col = None)
    
    # Generate weighting shceme
    dio = weighting_generator(pick_data, ID_start, ID_end, weight_input)
    
    with open (phase_out.joinpath(f"{out_name}.pha"), "w") as file_DD:
        for _id in range (ID_start, ID_end + 1):
        
            # get the dataframe 
            hypo = hypo_data[hypo_data["ID"] == _id]
            pick = pick_data[pick_data["Event ID"] == _id]
            
            # get origin time 
            year, month, day  = hypo.Year.iloc[0], hypo.Month.iloc[0], hypo.Day.iloc[0]
            hour, minute, sec = hypo.Hour.iloc[0], hypo.Minute.iloc[0], hypo.T0.iloc[0]
            
            # get hypo attribut
            lat, lon, depth = hypo.Lat.iloc[0], hypo.Lon.iloc[0], hypo.Depth.iloc[0]
            
            # corrected depth to fix the airquake normalize effect by the hypoDD program
            depth_cor = (depth * 0.001) + 2.000 # in km unit
            
            # rms error
            rms = hypo.RMS_error.iloc[0]
            
            # origin time
            OT = UTCDateTime(f"{year}-{int(month):02d}-{int(day):02d}T{int(hour):02d}:{int(minute):02d}:{float(sec):012.9f}")
            
            # start writing the phase file
            file_DD.write(f"#  {int(year):4d}  {int(month):2d} {int(day):2d} {int(hour):2d} {int(minute):2d}  {float(sec):9.6f} {float(lat):13.9f} {float(lon):14.9f}  {float(depth_cor):8.5f}  0  0  0 {float(rms):11.8f}  {int(_id):4d}\n")
            
            for sta in list(pick.get("Station")):
                
                # get the P and S pick time
                year, month, day, hour  = pick.Year[pick.Station == sta].iloc[0], pick.Month[pick.Station == sta].iloc[0], pick.Day[pick.Station == sta].iloc[0], pick.Hour[pick.Station == sta].iloc[0]
                minute_P, sec_P         = pick.Minutes_P[pick.Station == sta].iloc[0], pick.P_Arr_Sec[pick.Station == sta].iloc[0]
                minute_S, sec_S         = pick.Minutes_S[pick.Station == sta].iloc[0], pick.S_Arr_Sec[pick.Station == sta].iloc[0]
                P_pick_time             = UTCDateTime(f"{year}-{int(month):02d}-{int(day):02d}T{int(hour):02d}:{int(minute_P):02d}:{float(sec_P):012.9f}")
                S_pick_time             = UTCDateTime(f"{year}-{int(month):02d}-{int(day):02d}T{int(hour):02d}:{int(minute_S):02d}:{float(sec_S):012.9f}")
                
                # start writing the phase file
                weight_P = dio[f"{sta} P"][1]
                weight_S = dio[f"{sta} S"][1]
                file_DD.write(f"{sta} {abs(float(P_pick_time - OT)):11.8f}  {float(weight_P):5.3f}  P\n")
                file_DD.write(f"{sta} {abs(float(S_pick_time - OT)):11.8f}  {float(weight_S):5.3f}  S\n")

    file_DD.close()
    print('-----------  The code has run succesfully! --------------')