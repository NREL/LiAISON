import sys
import pandas as pd
from numpy import random
import numpy as np
#Monte Carlo of Foregound
def mc_foreground(yr,mc_runs,mc_foreground_flag,inventory_filename,output_dir):
    
    file = pd.read_csv(inventory_filename)
    print('Updating uncertainty',flush = True)    
    
    unc_dictionary = {}

    for index,row in file.iterrows(): 

            r = 0

            if row['input'] == True:


                    if yr == 2100.0:
                             #new_val = random.lognormal(mean = np.log(row['value']), sigma = 0.08, size  = mc_runs)
                             new_val = random.normal(loc = (row['value']), scale = (row['value']), size  = mc_runs)
                    elif yr == 2090.0:
                             #new_val = random.lognormal(mean = np.log(row['value']), sigma = 0.08, size  = mc_runs)
                             new_val = random.normal(loc = (row['value']), scale = (row['value'])/2, size  = mc_runs)
                    elif yr == 2080.0:
                             #new_val = random.lognormal(mean = np.log(row['value']), sigma = 0.07, size  = mc_runs)
                             new_val = random.normal(loc = (row['value']), scale = (row['value'])/3, size  = mc_runs)

                    elif yr == 2070.0:
                             #new_val = random.lognormal(mean = np.log(row['value']), sigma = 0.06, size  = mc_runs)
                             new_val = random.normal(loc = (row['value']), scale = (row['value'])/4, size  = mc_runs)

                    elif yr == 2060.0:
                             #new_val = random.lognormal(mean = np.log(row['value']), sigma = 0.05, size  = mc_runs)
                             new_val = random.normal(loc = (row['value']), scale = (row['value'])/5, size  = mc_runs)

                    elif yr == 2050.0:
                             #new_val = random.lognormal(mean = np.log(row['value']), sigma = 0.04, size  = mc_runs)
                             new_val = random.normal(loc = (row['value']), scale = (row['value'])/6, size  = mc_runs)

                    elif yr == 2040.0:
                             #new_val = random.lognormal(mean = np.log(row['value']), sigma = 0.03, size  = mc_runs)
                             new_val = random.normal(loc = (row['value']), scale = (row['value'])/7, size  = mc_runs)

                    elif yr == 2030.0:
                             #new_val = random.lognormal(mean = np.log(row['value']), sigma = 0.02, size  = mc_runs)
                             new_val = random.normal(loc = (row['value']), scale = (row['value'])/8, size  = mc_runs)
                           
                    else:
                             #new_val = random.lognormal(mean = np.log(row['value']), sigma = 0.01, size  = mc_runs)
                             new_val = random.normal(loc = (row['value']), scale = (row['value'])/9, size  = mc_runs)
            
  
                    unc_dictionary[row['process'] + row['flow']] = new_val

     

    file = pd.read_csv(inventory_filename)

    for r in range(0,mc_runs):
    

        if mc_foreground_flag:

             print(inventory_filename,flush = True)
             file = pd.read_csv(inventory_filename)
             print(yr,flush = True)

             for index,row in file.iterrows():

                     if row['input'] == True:

                         temp = row['value']
                         file.at[index,'value'] = unc_dictionary[row['process'] + row['flow']][r]
         
             name = output_dir+'/foreground_uncertainty_lci'+str(r)+'_'+str(yr)+'.csv'
             print('Recreated input file ' + name, flush = True)
             file.to_csv(name,index = False)
             r = r + 1        

            
         
    
    