import numpy as np
import pyprind
import pandas as pd
import os
import pprint
import copy
import time
import pickle
from premise import *
from premise_gwp import add_premise_gwp


def editor(eco_databases,ecoinvent_file,base_database,bw):
    #Main editor functions that actually calls the functions for reading IMAGE files,
    #IMAGE DATA from posterity and updating the ecoinvent databases. 
    #it stores the updated databases in dictionary files
    

        time0 = time.time()
        for eco in eco_databases:
            key = eco
            year = eco[10:14]
            scenario = eco[15:]
            version = base_database[9:]          
            bw.projects.set_current(key)
            print(key, flush = True)          
            
            time1 = time.time()
            ndb = NewDatabase(
                scenarios=[
                    {"model":"image", "pathway":scenario, "year":year}
                ],
                source_db=base_database, # <-- name of the database in the BW2 project. Must be a string.
                source_version=version, # <-- version of ecoinvent. Can be "3.5", "3.6", "3.7" or "3.7.1". Must be a string.
                key='tUePmX_S5B8ieZkkM7WUU2CnO8SmShwmAeWK9x2rTFo=' # <-- decryption key
                # to be requested from the library maintainers if you want ot use default scenarios included in `premise`
            )
            print(time.time() - time1, flush = True)
            print('new database created, updating now', flush = True)

            time1 = time.time()
            ndb.update_all()
            
            print("updated with image" + str(year), flush = True)
            print(time.time() - time1, flush = True)

            time1 = time.time()
            add_premise_gwp()
            print('Writing to brightway', flush = True)
            ndb.write_db_to_brightway(name=[key])
            print('Sucessfully written database '+ key, flush = True) 
            print(time.time() - time1, flush=True)

            
        print(time.time() - time0)
        print("seconds", flush = True)

        

