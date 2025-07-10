import secrets
import time
from reeds_ecoinvent_updater.lci_creator import reeds_db_editor
from premise import *
from premise_gwp import add_premise_gwp
import pandas as pd


def correct_natural_land_transformation(bw):
    """
    Filter and correct characterization factors for natural land transformation methods.

    This function updates all impact assessment methods that include "natural land transformation"
    in their names, retaining only flows associated with acceptable land types (e.g., forest, wetland).

    Parameters
    ----------
    bw : module
        Brightway2 module.

    Returns
    -------
    None
    """
    lt = [m for m in bw.methods if "natural land transformation" in m[1]]

    white_list = [
        "forest",
        "gassland, natural",
        "sea",
        "ocean",
        "inland waterbody",
        "lake, natural",
        "river, natural",
        "seabed, natural",
        "shrub land",
        "snow",
        "unspecified",
        "wetland",
        "bare area",
    ]

    for l in lt:
        m = bw.Method(l)
        cfs = m.load()
        cfs = [cf for cf in cfs if any(n in bw.get_activity(cf[0])["name"] for n in white_list)]
        m.write(cfs)

def correct_bigcc_copper_use(bw, db):
    """
    Adjust copper use in specific BIGCC electricity production activities.

    This function searches for BIGCC power plant processes in the given database and
    modifies the exchange amount for the copper-related construction activity.

    Parameters
    ----------
    bw : module
        Brightway2 module.
    db : str
        Name of the ecoinvent database in Brightway2 to modify.

    Returns
    -------
    None
    """
    list_acts = [
        "electricity production, at BIGCC power plant, no CCS",
        "electricity production, at BIGCC power plant, pre, pipeline 200km, storage 1000m",
        "electricity production, at BIGCC power plant, pre, pipeline 400km, storage 3000m",
    ]

    for ds in bw.Database(db):
        if ds["name"] in list_acts:
            for exc in ds.exchanges():
                if exc["name"] == "Construction, BIGCC power plant 450MW":
                    exc["amount"] = 1.01e-11
                    exc.save()



def reset_project(base_database, base_project, project_new, bw):
    """
    Reset and copy a Brightway2 project for modification.

    This function deletes (if exists) and copies a base Brightway2 project to a new project,
    and sets it as the current working project.

    Parameters
    ----------
    base_database : str
        Name of the base ecoinvent database (unused, can be removed unless used later).
    base_project : str
        Name of the existing Brightway2 project to copy.
    project_new : str
        Name of the new Brightway2 project to be created.
    bw : module
        The Brightway2 module object.
    """
    project_name = project_new
    try:
        bw.projects.delete_project(project_name, delete_dir=True)
        print(project_name, ' Project deleted', flush=True)
    except:
        print(project_name, ' Project does not exist', flush=True)
        pass

    print('Setting base project as current for copying - ', base_project, flush=True)
    bw.projects.set_current(base_project)

    try:
        bw.projects.copy_project(project_name, switch=False)
        print(base_project + ' project copied successfully', flush=True)
    except:
        bw.projects.purge_deleted_directories()
        bw.projects.copy_project(project_name, switch=False)
        print(base_project + '_project copied successfully after directory deleted', flush=True)

    bw.projects.set_current(project_name)
    print("Entered project " + project_name, flush=True)
    print("Databases in this project are", flush=True)
    print(bw.databases, flush=True)


def editor(updated_database, base_database, base_project, updated_project_name, bw):
    """
    Update a Brightway2 database with IMAGE SSP2-Base scenario and integrate with PREMISE.

    This function:
    - Deletes the existing updated database if present
    - Initializes a new database using PREMISE with SSP2-Base IMAGE scenario
    - Updates all activities and adds GWP indicators
    - Writes the new database to Brightway2

    Parameters
    ----------
    updated_database : str
        Name for the updated database.
    base_database : str
        Name of the source (ecoinvent) database to modify.
    base_project : str
        Existing Brightway2 project name.
    updated_project_name : str
        New project name (currently not used).
    bw : module
        Brightway2 module object.
    """
    bw.projects.set_current(base_project)

    try:
        del bw.databases[updated_database]
        print('Deleted database: ', updated_database)
    except:
        print('No database to delete')

    time0 = time.time()

    key = updated_database
    ndb = NewDatabase(
        scenarios=[{"model": "image", "pathway": "SSP2-Base", "year": 2020}],
        source_db=base_database,
        source_version="3.8",
        key='tUePmX_S5B8ieZkkM7WUU2CnO8SmShwmAeWK9x2rTFo=',
        use_multiprocessing=False
    )

    print("new database created, updating now", flush=True)
    ndb.update_all()
    print("updated with SSP2-Base 2020", flush=True)

    add_premise_gwp()
    print('Writing to brightway', flush=True)
    ndb.write_db_to_brightway(name=[key])
    print('Successfully written database ' + key, flush=True)

    print('Correcting Natural Land Transformation Recipe method', flush = True)
    correct_natural_land_transformation(bw)
    print('Correcting BIG CC copper use',flush = True)
    correct_bigcc_copper_use(bw,key)

    print("Total update time:", time.time() - time0, "seconds", flush=True)


def reeds_updater(
    year_of_study,
    results_filename,
    reeds_grid_mix_creator,
    data_dir,
    inventory_filename,
    modification_inventory_filename,
    modification_inventory_filename_us,
    premise_editor,
    base_database,
    base_project,
    database_new,
    project_new,
    bw
):
    """
    Update and customize an ecoinvent-based database using PREMISE and ReEDS electricity mixes.

    Optionally applies PREMISE transformations, then customizes the electricity sector using
    ReEDS state- and national-level mixes.

    Parameters
    ----------
    year_of_study : str
        Label or year for the study (not currently used internally).
    results_filename : str
        File path to the ReEDS grid mix CSV output.
    reeds_grid_mix_creator : bool
        Whether to run the ReEDS-based grid mix creator.
    data_dir : str
        Path to base directory for data (currently unused).
    inventory_filename : str
        CSV file for inventory foreground data.
    modification_inventory_filename : str
        CSV file for state-specific electricity inventory modifications.
    modification_inventory_filename_us : str
        CSV file for national-level electricity inventory modifications.
    premise_editor : bool
        Whether to apply PREMISE-based scenario modifications.
    base_database : str
        Name of the source (ecoinvent) database.
    base_project : str
        Name of the base Brightway2 project.
    database_new : str
        Name for the updated database to be written.
    project_new : str
        New Brightway2 project name to be created and used.
    bw : module
        Brightway2 module.
    """
    
    def reeds_editor(db_new, r, run_filename, project_new):
        """
        Create ReEDS-based grid mix inventories within a Brightway2 database.

        Parameters
        ----------
        db_new : str
            Name of the new database.
        r : str
            Identifier for run (currently unused).
        run_filename : str
            File path to ReEDS grid mix CSV.
        project_new : str
            Name of the Brightway2 project to use.
        """
        print("Starting editing LCI using ReEDS", flush=True)

        if reeds_grid_mix_creator:
            print('Creating ReEDS Grid mix inside ecoinvent')
            reeds_db_editor(db_new, run_filename, bw)

            print('ReEDS LCI electricity generation created within ecoinvent', flush=True)
            state_df = pd.read_csv(run_filename)
            states = sorted(list(pd.unique(state_df['process_location'])))
            print('Creating market mixes for electricity grid for the states', flush=True)
            print(states)

            for st in states:
                if st != "US":
                    print("US---" + st)
                    print('Reading from ', modification_inventory_filename)
                    temp_df = pd.read_csv(modification_inventory_filename)
                    temp_df['process_location'] = "US-" + st
                    temp_df['supplying_location'] = st                    
                    reeds_db_editor(db_new, temp_df, bw)

            print('Creating market mixes for electricity grid for the US grid mix', flush=True)
            print('Reading from ', modification_inventory_filename_us,flush=True)
            reeds_db_editor(db_new, modification_inventory_filename_us, bw)
            print('Background activity modified and saved successfully', flush=True)

    r = ''
    run_filename = inventory_filename

    if premise_editor:
        editor(database_new, base_database, base_project, project_new, bw)

    reset_project(base_database, base_project, project_new, bw)
    reeds_editor(database_new, r, run_filename, project_new)
