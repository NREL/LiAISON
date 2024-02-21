import time
from pprint import pprint
from premise import *
from premise_gwp import add_premise_gwp
import bw2io

def reset_project(base_database, base_project, project_new, bw):
    """
    Copy the project directory for a certain year and scenario, creating a new project with a non-repeatable name.

    Parameters
    ----------
    base_database : str
        Database name for scenario and year.
    base_project : str
        Generic project name.
    project_new : str
        Name for the new project.
    bw : module
        Brightway2 module loaded shortcut name.

    Returns
    -------
    project_name : str
        Name of the new project.
    """
    project_name = project_new
    try:
        bw.projects.delete_project(project_name, delete_dir=True)
        pprint('Project deleted')
    except:
        pprint('Project does not exist')
        pass

    bw.projects.set_current(base_project)

    try:
        bw.projects.copy_project(project_name, switch=False)
        pprint(base_project+'_project copied successfully')
    except:
        bw.projects.purge_deleted_directories()
        bw.projects.copy_project(project_name, switch=False)
        pprint(base_project+'_project copied successfully after directory deleted')

    bw.projects.set_current(project_name)
    pprint("Entered project " + project_name)
    pprint("Databases in this project are")
    pprint(bw.databases)

    bw2io.create_default_lcia_methods(overwrite=True)
    pprint("Updated LCIA methods from bw2io=0.8.8")

def editor(updated_database, base_database, base_project, updated_project_name, iam_model, iam_model_key, bw):
    """
    Main editor function that reads IMAGE files, IMAGE DATA from posterity, and updates the ecoinvent databases.
    It stores the updated databases in dictionary files.

    Parameters
    ----------
    updated_database : str
        Updated database information.
    base_database : str
        Base database information.
    base_project : str
        Base project name.
    updated_project_name : str
        Updated project name.
    iam_model : str
        IAM model information.
    iam_model_key : str
        IAM model decryption key.
    bw : module
        Brightway2 module loaded shortcut name.
    """
    time1 = time.time()
    reset_project(base_database, base_project, updated_project_name, bw)

    key, year, scenario, version, iam_model_key = updated_database, updated_database[10:14], updated_database[15:], base_database[9:], None if len(iam_model_key) != 44 else iam_model_key

    ndb = NewDatabase(
        scenarios=[{"model": str(iam_model), "pathway": scenario, "year": year}],
        source_db=base_database,
        source_version=version,
        key=iam_model_key,
        use_multiprocessing=False
    )
    
    pprint(time.time() - time1)
    pprint('New database created, updating now')
    print(flush=True)

    time1 = time.time()
    if iam_model == "gcam" or iam_model == 'image':
            ndb.update_steel()
            ndb.update_electricity()
            ndb.update_emissions()
            ndb.update_cement()
            ndb.update_fuels()
    else:
            ndb.update_all()    

    pprint(f"Updated with {iam_model} {year}")
    pprint(time.time() - time1)
    print(flush=True)

    time1 = time.time()
    add_premise_gwp()
    pprint('Writing to Brightway')
    ndb.write_db_to_brightway(name=[key])
    pprint(f'Successfully written database {key}')
    pprint(time.time() - time1)
    pprint("Seconds")
    print(flush=True)
