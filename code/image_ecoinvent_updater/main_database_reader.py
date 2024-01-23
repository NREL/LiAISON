import time

def reset_project(database, bw2):
    """
    Reset the project by deleting and recreating it.

    Args:
        database (str): Name of the project to reset.
        bw2 (brightway2.Brightway2Project): Brightway2 project instance.
    """
    project_name = database
    try:
        bw2.projects.delete_project(project_name, delete_dir=True)
        print('Project deleted', flush=True)
    except:
        print('Project does not exist', flush=True)
        pass
    
    print("Creating base project ", database)
    bw2.projects.set_current(project_name)
    bw2.bw2setup()

def read_ecoinvent_database(base_database, ecoinvent_file, bw2):
    """
    Read and import an ecoinvent database.

    Args:
        base_database (str): Name of the base database.
        ecoinvent_file (str): Path to the ecoinvent database file.
        bw2 (brightway2.Brightway2Project): Brightway2 project instance.
    """
    print('Reading', base_database, flush=True)
    
    ei38_path = ecoinvent_file
    print(ei38_path)

    ei_38 = bw2.SingleOutputEcospold2Importer(ei38_path, base_database, use_mp=False)
    ei_38.apply_strategies()
    ei_38.statistics()
    ei_38.write_database()
    
    print('Successfully written', base_database, flush=True)

def reader(ecoinvent_file, base_database, base_project, bw):
    """
    Main function for reading IMAGE files, IMAGE DATA from posterity,
    and updating the ecoinvent databases.

    Args:
        ecoinvent_file (str): Path to the ecoinvent database file.
        base_database (str): Name of the base database.
        base_project (str): Name of the base project.
        bw (brightway2.Brightway2Project): Brightway2 project instance.
    """
    time0 = time.time()
    reset_project(base_project, bw)
    read_ecoinvent_database(base_database, ecoinvent_file, bw)
    
    print(time.time() - time0, flush=True)
    print("seconds")
