import numpy as np
import pyprind
import pandas as pd
import os
import pprint
import copy
from pandas import DataFrame
import time
import pickle


def reset_project(base_project, bw):
    """
    Reset and initialize a Brightway2 project.

    Deletes the specified project if it exists and reinitializes it using bw2setup.

    Parameters:
    -----------
    base_project : str
        Name of the Brightway2 project to reset.
    bw : module
        The Brightway2 module (typically imported as `import brightway2 as bw`).
    """
    print('Creating base project ' + base_project)
    print('Projects in list:', bw.projects, flush = True)
    try:
        bw.projects.delete_project(base_project, delete_dir=True)
        print('Project deleted', flush=True)
    except:
        print('Project does not exist', flush=True)
        pass

    bw.projects.set_current(base_project)
    bw.bw2setup()


def read_ecoinvent_database(base_database, ecoinvent_file, bw):
    """
    Import the ecoinvent database into Brightway2.

    Parameters:
    -----------
    base_database : str
        Name to assign to the imported ecoinvent database.
    ecoinvent_file : str
        File path to the ecoinvent Ecospold2 directory.
    bw : module
        The Brightway2 module.
    """
    print('Reading ' + base_database, flush=True)
    ei38_path = ecoinvent_file
    print(ei38_path)

    ei_38 = bw.SingleOutputEcospold2Importer(ei38_path, base_database, use_mp=False)
    ei_38.apply_strategies()
    ei_38.statistics()
    ei_38.write_database()
    print('Successfully written ' + base_database, flush=True)


def read_other_databases(base_database, wave_file, biomethane_file, ccs_file, geothermal_file):
    """
    Import additional Excel-based LCI databases (Wave, Biomethane, CCS, Geothermal) into Brightway2.

    Parameters:
    -----------
    base_database : str
        Base database to match against (typically the ecoinvent database).
    wave_file : str
        Path to the Wave Excel file.
    biomethane_file : str
        Path to the Biomethane Excel file.
    ccs_file : str
        Path to the CCS Excel file.
    geothermal_file : str
        Path to the Geothermal Excel file.
    """
    print('Reading Wave, Geothermal, Carma CCS, Biomethane')

    for file_path in [wave_file, biomethane_file, ccs_file, geothermal_file]:
        sp = bw.ExcelImporter(file_path)
        sp.apply_strategies()
        sp.match_database(fields=["name", "unit", "location"])
        sp.match_database(base_database, fields=["reference product", "name", "unit", "location"])
        sp.match_database(base_database, fields=["name", "unit", "location"])
        sp.write_database()

    print('Successfully read')


def reader(ecoinvent_file, base_database, base_project, bw):
    """
    Main function to initialize project and import the ecoinvent database.

    Parameters:
    -----------
    ecoinvent_file : str
        Path to the ecoinvent Ecospold2 directory.
    base_database : str
        Name to assign to the imported ecoinvent database.
    base_project : str
        Name of the Brightway2 project to reset and use.
    bw : module
        The Brightway2 module.

    Notes:
    ------
    This function orchestrates the import pipeline by resetting the project
    and calling subfunctions for importing data.
    """
    time0 = time.time()
    reset_project(base_project, bw)
    read_ecoinvent_database(base_database, ecoinvent_file, bw)
    # read_other_databases(wave_file, biomethane_file, ccs_file, geothermal_file)

    print(time.time() - time0, flush=True)
    print("seconds")
