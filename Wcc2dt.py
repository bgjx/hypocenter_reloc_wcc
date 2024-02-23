import pandas as pd
import numpy as np
from pathlib import PurePath, Path

print('''
Python code for converting WCC result format to dt.cc hypoDD input format 

Before you run this program, make sure you have changed all the path and set the necessary parameters correctly      
      ''')
      
# List of functions 
#============================================================================================
def write_head(file,index,wcc):
    """
    write line consisting #, master ID, pair ID, and code

    """
    file.write('#' + ' ' + str(wcc['master'][index]) + ' ' + str(wcc['pair'][index]) +
              ' ' + '0.0' + '\n')

def write_content(file,index,wcc):
    """
    write line consisting station, lagtime, coefficient, and phase

    """
    file.write(wcc['station'][index] + ' ' + str(wcc['lagtime'][index]) + ' ' +
                   str(wcc['coefficient'][index]) + ' ' + wcc['phase'][index] + '\n')
# End of functions 
#============================================================================================

if __name__ =="__main__":
    # initialize input and output path
    wccfile     = Path(r"E:\SEML\DATA WCC\2023\result_2.csv")
    outputcc    = Path(r"E:\SEML\DATA WCC\2023\dt.cc")
    
    # set coefficient cut-off
    koefisien = 0.7

    # dataframe preparation : nan removal, apply coefficient low bound = 0.7
    df = pd.read_csv(wccfile)
    df = df.replace(np.nan,9999)
    wcc = df[df['coefficient']>koefisien]
    wcc = wcc[wcc['coefficient']<9999]
    wcc = wcc.set_index(pd.Series([i for i in range(len(wcc))]))

    # write output file
    print('writing dt.cc ...')
    file = open(outputcc, 'w')
    write_head(file, 0, wcc)
    write_content(file, 0, wcc)

    for i in range(1, len(wcc)):
        if (wcc['master'][i] != wcc['master'][i - 1]) or (wcc['pair'][i] != wcc['pair'][i - 1]):
            write_head(file, i, wcc)
        write_content(file, i, wcc)

    file.close()
    print('-----------  The code has run succesfully! --------------')