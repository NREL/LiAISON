
import time



def reset_project(db,bw):
    #Creating a new fresh project for calculations for storing the modified databases. 
    
    project_name = db
    try:
      bw.projects.delete_project(project_name,delete_dir = True)
      print('Project deleted',flush=True)
    except:
      print('Project does not exist',flush=True)
      pass
    print("Creating base project ",db)
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

def reader(ecoinvent_file,base_database,base_project,bw):
    #Main editor functions that actually calls the functions for reading IMAGE files,
    #IMAGE DATA from posterity and updating the ecoinvent databases. 
    #it stores the updated databases in dictionary files
    
       
        time0 = time.time()
        reset_project(base_project, bw)
        read_ecoinvent_database(base_database, ecoinvent_file, bw)
            
            
        print(time.time() - time0, flush = True)
        print("seconds")