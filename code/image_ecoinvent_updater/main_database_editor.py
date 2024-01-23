import time
from premise import *
from premise_gwp import add_premise_gwp
import bw2io
import secrets

def reset_project(base_database,base_project,project_new,bw):
    
    """
    This function copies the project directory of a certain year and scenario, for example
    ecoinvent RCP 19 2030 and creates a copy of the project using a non repeatable name
    using 


    Parameters
    ----------
    db: str
        database name for scenario and year
    
    number : str
        random number generated by uuid to create no duplicate databases
    
    project : str 
        generic project name
        
    bw : module
        brightway2 module loaded shortcut name
        

    
    Returns
    -------
    project name : str
        Name of the project
    """

    project_name = project_new
    try:
      bw.projects.delete_project(project_name,delete_dir = True)
      print('Project deleted',flush=True)
    except:
      print('Project does not exist',flush=True)
      pass
    bw.projects.set_current(base_project)
    try:
        bw.projects.copy_project(project_name,switch = False)
        print(base_project+'_project copied successfully',flush=True)
    except:
        bw.projects.purge_deleted_directories()
        bw.projects.copy_project(project_name,switch = False)
        print(base_project+'_project copied successfully after directory deleted',flush=True)    
    

    bw.projects.set_current(project_name)
    print("Entered project " + project_name,flush = True)
    print("Databases in this project are",flush = True)
    print(bw.databases,flush = True) 
    #updating LCIA methods 
    bw2io.create_default_lcia_methods(overwrite=True)

def editor(updated_database,base_database,base_project,updated_project_name,iam_model,iam_model_key,bw):
    #Main editor functions that actually calls the functions for reading IMAGE files,
    #IMAGE DATA from posterity and updating the ecoinvent databases. 
    #it stores the updated databases in dictionary files
 
        reset_project(base_database,base_project,updated_project_name,bw)   

        time0 = time.time()
        key = updated_database
        year = updated_database[10:14]
        scenario = updated_database[15:]
        version = base_database[9:] 
        iam_model = iam_model         
        time1 = time.time()
        if len(iam_model_key) != 44:
           iam_model_key = None
        
        ndb = NewDatabase(
            scenarios=[
                {"model":str(iam_model), "pathway":scenario, "year":year}
            ],
            source_db=base_database, # <-- name of the database in the BW2 project. Must be a string.
            source_version=version, # <-- version of ecoinvent. Can be "3.5", "3.6", "3.7" or "3.7.1". Must be a string.
            key=iam_model_key,# <-- decryption key
            use_multiprocessing=False, 
            # to be requested from the library maintainers if you want ot use default scenarios included in `premise`
        )
        print(time.time() - time1, flush = True)
        print('new database created, updating now', flush = True)

        time1 = time.time()

        if iam_model == "gcam" or iam_model == 'image':

            ndb.update_steel()
            ndb.update_electricity()
            ndb.update_emissions()
            ndb.update_cement()
            ndb.update_fuels()
        else:

            ndb.update_all()
        
        print("updated with " +iam_model+str(year), flush = True)
        print(time.time() - time1, flush = True)

        time1 = time.time()
        add_premise_gwp()
        print('Writing to brightway', flush = True)
        ndb.write_db_to_brightway(name=[key])
        print('Sucessfully written database '+ key, flush = True) 
        print(time.time() - time1, flush=True)

            
        print(time.time() - time0)
        print("seconds", flush = True)
     

