#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 12:31:35 2022

@author: arhamze
"""
from pyproj import Proj

#### initialize path file
hypoddReloc = input('Input the hypoDD reloc result to be formatted (PRESS ENTER IF hypoDD_all.reloc) : ')
FirstId, SecondId= input ('Input the first and last ID Number (ex. 1000 2000): ').split()
ExcelOutput=input('Input your desire file csv file output name:')
zone_input=input("Insert UTM zone for convertion from Geographic system : ")
if len(hypoddReloc) < 1: hypoddReloc='hypoDD_all.reloc'

#projection from geographic to utm
myProj = Proj(proj='utm', zone=int(zone_input), ellps='WGS84', datum='WGS84', units='m', south=True )


IdList=[ i for i in range(int(FirstId), int(SecondId)+1)]
DataFormatted=[i.split() for i in open(hypoddReloc,'r').readlines()]

DataReorde=[]
for i in DataFormatted:
    try:
        Lat, Long=myProj(float(i[2]),float(i[1]))
        Depth=(float(i[3])- 2.00)*1000
        Elev=-1*Depth
        i=[int(i[0]),float(i[1]),float(i[2]),Lat,Long,Depth,Elev,int(i[10]),int(i[11]),int(i[12]),int(i[13]),int(i[14]),float(i[15]),float(i[21]),float(i[22])]
        DataReorde.append(i)
    except Exception:
        pass

DataReorde.sort()

with open (ExcelOutput + '.csv','w') as file2:
    v=0
    for i in range(len(IdList)):
        try:
            if IdList[i] == int(DataReorde[v][0]):
                if DataReorde[v][-2] < 0:
                    del DataReorde[v][-2]
                    file2.write("%4i\t%.12f\t%.12f\t%.6f\t%.6f\t%.6f\t%.6f\t%2i\t%2i\t%2i\t%2s\t%2s\t%.7f\t%.7f\tReloc\n" % (DataReorde[v][0],DataReorde[v][1],DataReorde[v][2],DataReorde[v][3],DataReorde[v][4],DataReorde[v][5],DataReorde[v][6],DataReorde[v][7],
                                                                                                                  DataReorde[v][8],DataReorde[v][9],DataReorde[v][10],DataReorde[v][11],DataReorde[v][12],DataReorde[v][13]))
                else :
                    del DataReorde[v][-1]
                    file2.write("%4i\t%.12f\t%.12f\t%.6f\t%.6f\t%.6f\t%.6f\t%2i\t%2i\t%2i\t%2s\t%2s\t%.7f\t%.7f\tWCC\n" % (DataReorde[v][0],DataReorde[v][1],DataReorde[v][2],DataReorde[v][3],DataReorde[v][4],DataReorde[v][5],DataReorde[v][6],DataReorde[v][7],
                                                                                                                  DataReorde[v][8],DataReorde[v][9],DataReorde[v][10],DataReorde[v][11],DataReorde[v][12],DataReorde[v][13]))
                v+=1
            else:
                file2.write("null\n")
        except Exception as e:
            print(e)
            pass
    file2.close()
print("""
      

 _____  ____  ____   ____ _____ __ __    ___  ___    __  __  __ 
|     ||    ||    \ |    / ___/|  |  |  /  _]|   \  |  ||  ||  |
|   __| |  | |  _  | |  (   \_ |  |  | /  [_ |    \ |  ||  ||  |
|  |_   |  | |  |  | |  |\__  ||  _  ||    _]|  D  ||__||__||__|
|   _]  |  | |  |  | |  |/  \ ||  |  ||   [_ |     | __  __  __ 
|  |    |  | |  |  | |  |\    ||  |  ||     ||     ||  ||  ||  |
|__|   |____||__|__||____|\___||__|__||_____||_____||__||__||__|
                                                                






""")