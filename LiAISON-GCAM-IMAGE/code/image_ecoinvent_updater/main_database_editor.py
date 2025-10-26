import time
from pprint import pprint
from premise import *
from premise_gwp import add_premise_gwp
import bw2io
from typing import Any, Union


def correct_natural_land_transformation(bw: Any) -> None:
    """
    Corrects the namation method in the Brightway2 database.
    Removes flows not related to specific land types in a whitelist.

    Parameters:
    -----------
    bw : module
        Brightway2 module loaded as a shortcut name.
    """
    lt_methods = [m for m in bw.methods if "natural land transformation" in m[1]]
    white_list = ["forest", "grassland, natural", "sea", "ocean", "inland waterbody", "lake, natural",
                  "river, natural", "seabed, natural", "shrub land", "snow", "unspecified", "wetland", "bare area"]
    # l_flows = [cf for lt_method in lt_methods for cf in bw.Method(lt_method).load() if any(n in bw.get_activity(cf[0])["name"] for n in white_list)]
    l_flows = []
    l_flow_dic = {}
    # Iterate through each impact assessment method
    for lt_method in lt_methods:
        method = bw.Method(lt_method)  # Load the method
        cf_data = method.load()  # Retrieve the characterization factors
        
        # Iterate through each characterization factor
        for cf in cf_data:
            activity = bw.get_activity(cf[0])  # Get the activity associated with the CF
            activity_code = activity['code']
            activity_name = activity["name"]  # Extract the activity name
            # print(cf,activity_name,2)
            
            
            # Check if any of the names in white_list are in the activity name
            if any(n in activity_name for n in white_list):
                # l_flows.append(cf)  # Append the matching characterization factor
                l_flow_dic[activity_code] = cf
    
    l_flows = []
    #adding the l_flows to a list in a unique manner
    for l_flow_key in l_flow_dic.keys():
        l_flows.append(l_flow_dic[l_flow_key])
    for lt_method in lt_methods:
        bw.Method(lt_method).write(l_flows)

def correct_bigcc_copper_use(bw: Any, db: str) -> None:
    """
    Corrects the copper use in the BIGCC power plant construction exchange.
    Modifies the amount to a specific value.

    Parameters:
    -----------
    bw : module
        Brightway2 module loaded as a shortcut name.
    db : str
        Name of the database for the scenario and year.
    """
    list_dbs = [db]
    list_acts = [
        "electricity production, at BIGCC power plant, no CCS",
        "electricity production, at BIGCC power plant, pre, pipeline 200km, storage 1000m",
        "electricity production, at BIGCC power plant, pre, pipeline 400km, storage 3000m",
    ]
    for db_name in list_dbs:
        for ds in bw.Database(db_name):
            if ds["name"] in list_acts:
                for exc in ds.exchanges():
                    if exc["name"] == "Construction, BIGCC power plant 450MW":
                        exc["amount"] = 1.01e-11
                        exc.save()

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
    pprint("Entered project " + base_project)
    pprint("Databases in this project are")
    pprint(bw.databases)

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
    pprint("Updated LCIA methods from bw2io=0.8.7")

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

    print(f"Trying to update with {iam_model} {scenario} {year}",flush=True)
    ndb = NewDatabase(
        scenarios=[{"model": str(iam_model), "pathway": scenario, "year": year}],
        source_db=base_database,
        source_version=version,
        key=iam_model_key,
    )
    
    pprint(time.time() - time1)
    pprint('New database created, updating now')
    print(flush=True)

    time1 = time.time()
    try:
        if iam_model == "gcam" or iam_model == 'image':
                ndb.update_all()  
    except:
                ndb.update()  

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

    
    bw.projects.set_current(updated_project_name)
    print(f"Current project after premise update is {updated_project_name}",flush=True)
    print("Databases in this project are",flush=True)
    print(bw.databases,flush=True)
    print('Premise updated database is ',updated_database)

    start_time = time.perf_counter()
     
    print('Correcting Natural Land Transformation Recipe method',flush=True)
    correct_natural_land_transformation(bw)
    print('Correcting BIG CC copper use',flush=True)
    correct_bigcc_copper_use(bw, updated_database)
    add_premise_gwp()
    end_time = time.perf_counter()
    print(f"Time taken for NLT recipe update and BIG CC copper use: {end_time - start_time} seconds",flush=True)
    


