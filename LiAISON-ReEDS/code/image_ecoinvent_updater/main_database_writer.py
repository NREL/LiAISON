import numpy as np
import pyprind
import pandas as pd
import os
import pprint
import copy
from pandas import DataFrame
import time
import sys
import pickle
from wurst import *

def reset_project(db,bw):
    #Creating a new fresh project for calculations for storing the modified databases. 
    
    project_name = db
    try:
      bw.projects.delete_project(project_name,delete_dir = True)
      print('Project deleted',flush=True)
    except:
      print('Project does not exist',flush=True)
      pass
    
    bw.projects.set_current(project_name)
    bw.bw2setup()



def writer(data_dict_edited_file,uncertainty_corrections,project,bw):
    #Writing the modified databses to memory
    #The databases are written to a pre defined project name. 


  try:
    print('Reading Database modified Dict')
    file = open(data_dict_edited_file,'rb')
    database_dict = pickle.load(file)
    print('Success Read modified Database Dict')

  except IOError as err:
        print('Could not find edited database dictionary')
        print(data_dict_edited_file)
        exit(1)
  reset_project(project, bw) 
  for key in pyprind.prog_bar(database_dict.keys()):
      
        print(key)
        
        time0 = time.time()
        try:
           del bw.databases[key]
        #  print('Old database deleted '+str(key))
        except:
           pass
        db = database_dict[key]['db']
        year = database_dict[key]['year']
        scenario = database_dict[key]['scenario']
        write_brightway2_database(db,key)
        print('written database')
        
        
        #Correction for uncertainty
        ei_cf_36_db = bw.Database(key)      
        if uncertainty_corrections:
            print('correcting uncertainty')
            for i in ei_cf_36_db:
         
             c= 0
             for j in i.exchanges():
                 if j.get('scale') == None:
                          continue
                 elif j.get('scale') == 0 or j.get('scale')<0:
                          c = 1
                          print(j.get('name') + ' ' + i.get('name') + ' '+ str(j.get('scale'))+ ' '+ str(j.get('loc')))
                          j['scale'] = 0.1
                          print(' Updated scale '+ str(j.get('scale'))+ ' '+ str(j.get('loc')))
                          j.save()
             if c == 1:
                print(i['name'] + ' saved')   
                i.save()
        
        print('\n')
        print(key+' took '+str(time.time()-time0))

    
    
