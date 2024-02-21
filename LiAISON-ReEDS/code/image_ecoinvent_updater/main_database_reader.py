import numpy as np
import pyprind
import pandas as pd
import os
import pprint
import copy
from pandas import DataFrame
import time
import pickle


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

def read_ecoinvent_database(base_database, ecoinvent_file, bw):
    
        print('Reading' + base_database, flush = True)
        #Reading the ecoinvent database from the folder
        ei38_path = ecoinvent_file
        print(ei38_path)

        ei_38 = bw.SingleOutputEcospold2Importer(ei38_path, base_database, use_mp=False)
        ei_38.apply_strategies()
        ei_38.statistics()
        ei_38.write_database()        
        print('Successfully written '+base_database, flush = True)

def reader(eco_databases,ecoinvent_file,base_database,bw):
    #Main editor functions that actually calls the functions for reading IMAGE files,
    #IMAGE DATA from posterity and updating the ecoinvent databases. 
    #it stores the updated databases in dictionary files
    
       
        time0 = time.time()
        for eco in eco_databases:
            key = eco
            year = eco[10:14]
            scenario = eco[15:]
            version = base_database[9:]
            print(key, flush = True)
            reset_project(key, bw)
            read_ecoinvent_database(base_database, ecoinvent_file, bw)
            
            
        print(time.time() - time0, flush = True)
        print("seconds")