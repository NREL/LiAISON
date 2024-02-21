import numpy as np
import pyprind
import pandas as pd
import os
import pprint
import copy
from pandas import DataFrame
import time
import pickle


def reset_project(base_project,bw):
    #Creating a new fresh project for calculations for storing the modified databases. 
    
    project_name = base_project
    print('Creating base project '+base_project)
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

def read_other_databases(base_database,wave_file,biomethane_file,ccs_file,geothermal_file):
                
        print('Reading Wave, Geothermal, Carma CCS, Biomethane')
        lci_wave_path = wave_file
        sp = bw.ExcelImporter(lci_wave_path)
        sp.apply_strategies()  
        sp.match_database(fields=["name", "unit", "location"])
        sp.match_database(base_database, fields=["reference product", "name", "unit", "location"])
        sp.match_database(base_database, fields=["name", "unit", "location"])
        sp.write_database()
        
        
        lci_biomethane_heat_path = biomethane_file
        sp = bw.ExcelImporter(lci_biomethane_heat_path)
        sp.apply_strategies()  
        sp.match_database(fields=["name", "unit", "location"])
        sp.match_database(base_database, fields=["reference product", "name", "unit", "location"])
        sp.match_database(base_database, fields=["name", "unit", "location"])
        sp.write_database()
        
        
        lci_ccs_path = ccs_file
        
        sp = bw.ExcelImporter(lci_ccs_path)
        sp.apply_strategies()  
        sp.match_database(fields=["name", "unit", "location"])
        sp.match_database(base_database, fields=["reference product", "name", "unit", "location"])
        sp.match_database(base_database, fields=["name", "unit", "location"])
        sp.write_database()
        
        
        lci_geothermal_path = geothermal_file
        
        sp = bw.ExcelImporter(lci_geothermal_path)
        sp.apply_strategies()  
        sp.match_database(fields=["name", "unit", "location"])
        sp.match_database(base_database, fields=["reference product", "name", "unit", "location"])
        sp.match_database(base_database, fields=["name", "unit", "location"])
        sp.write_database()
        
        print('Succesfully read')
def reader(ecoinvent_file,base_database,base_project,bw):
    #Main editor functions that actually calls the functions for reading IMAGE files,
    #IMAGE DATA from posterity and updating the ecoinvent databases. 
    #it stores the updated databases in dictionary files
    
        time0 = time.time()
        reset_project(base_project, bw)
        read_ecoinvent_database(base_database, ecoinvent_file, bw)
        #read_other_databases(wave_file,biomethane_file,ccs_file,geothermal_file)
            
            
        print(time.time() - time0, flush = True)
        print("seconds")