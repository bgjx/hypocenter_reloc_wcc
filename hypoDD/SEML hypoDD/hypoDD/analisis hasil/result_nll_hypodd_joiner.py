from pathlib import PurePath, Path
import re

## path address for dinamic path
ID_file=Path(r"E:\SEML\DATA PROCESSING\MEQ MISCELANEOUS PROCESSING\HypoDD Processing SEML\HYPODD 14 08 2023\HYPODD 2020 12_ 2022_4\hasil hypoDD")
output_path=Path(r"E:\SEML\DATA PROCESSING\MEQ MISCELANEOUS PROCESSING\HypoDD Processing SEML\HYPODD 14 08 2023\HYPODD 2020 12_ 2022_4\hasil hypoDD")


## input name
input_NLL=input("Input the initital NLL from previouse  catalog: !! PRESS ENTER FOR result_NLL.csv: ")
if input_NLL == '':
    input_NLL=r"result_NLL.csv"
 
input_DD_result=input("Input the hypoDD result file: PRESS ENTER FOR all_recap.csv: " )
if input_DD_result == '':
    input_DD_result=r"all_recap.csv"
    
output_ID =input("Ooutput file: PRESS ENTER FOR output_copier.csv: ")
if output_ID == '':
    output_ID=r"output_copier.csv"

# crate file read and file ouput
with open(input_NLL, 'r') as file_NLL , open(input_DD_result, 'r') as DD_result, open(output_ID, 'w') as output_file:
    output_file.write("ID;Lat;Lon;UTM_X;UTM_Y;Depth;Elev;Year;Month;Day;Hour;Minute;T0;RMS_error;Remarks\n")
    ## create ID list
    NLL_list=[i[:-1].split(';') for i in file_NLL.readlines()]
   
    ## create DD result list
    DD_result=[i[:-1].split(';') for i in DD_result.readlines()]
    ## looping trough DD result
    counter=0
    for x in range(0, len(NLL_list)):
        if NLL_list[x][0] == DD_result[counter][0]:
            output_file.write( "{}\n".format(";".join(DD_result[counter])))
            counter+=1
        else: 
            output_file.write("{};Initial\n".format(";".join(NLL_list[x])))
