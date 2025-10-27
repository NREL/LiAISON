import os
import shutil
import argparse
import time
import warnings
from pprint import pprint
from typing import Dict, Any
import yaml
import sys

warnings.filterwarnings("ignore")

def load_config_file(datapath: str, lca_config_file: str) -> Dict[str, Any]:
    """
    Load configuration settings from a YAML file.

    Parameters:
    - datapath (str): Path to the input and output data folder.
    - lca_config_file (str): Name of the life cycle information config file in the data folder.

    Returns:
    - dict: Loaded configuration settings.
    """
    config_yaml_filename = os.path.join(datapath, lca_config_file)
    try:
        with open(config_yaml_filename, 'r') as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except IOError as err:
        pprint(f'Could not open {config_yaml_filename} for configuration. Exiting with status code 1.')
        exit(1)

def set_brightway2_dir(envpath: str) -> None:
    """
    Set the BRIGHTWAY2_DIR environment variable.

    Parameters:
    - envpath (str): Path to the environments folder.
    """
    os.environ['BRIGHTWAY2_DIR'] = str(envpath)

def remove_directory(directory: str) -> None:
    """
    Remove a directory and its contents if it exists.

    Parameters:
    - directory (str): Path to the directory to be removed.
    """
    try:
        shutil.rmtree(directory)
    except:
        pprint(f'{directory} directory does not exist')
        pass

def create_directory(directory: str) -> None:
    """
    Create a directory if it does not exist.

    Parameters:
    - directory (str): Path to the directory to be created.
    """
    try:
        os.makedirs(directory)
    except:
        pass

def remove_old_results(output_dir: str) -> None:
    """
    Remove old results from the specified output directory.

    Parameters:
    - output_dir (str): Path to the output directory.
    """
    try:
        for f in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, f))
            pprint(f'{output_dir} removed old results')
    except:      
            pprint(f'{output_dir}  old results not removed')
            pass

def run_database_reader(ecoinvent_file: str, base_database: str, base_project: str, bw: Any) -> None:
    """
    Run the database reader to read the ecoinvent base database.

    Parameters:
    - ecoinvent_file (str): Path to the ecoinvent data file.
    - base_database (str): Name of the base database.
    - base_project (str): Name of the base project.
    - bw: Brightway2 instance.
    """
    from image_ecoinvent_updater.main_database_reader import reader
    reader(ecoinvent_file=ecoinvent_file, base_database=base_database, base_project=base_project, bw=bw)

def run_database_editor(updated_database: str, base_database: str, base_project: str, updated_project_name: str,
                        iam_model: str, iam_model_key: str, bw: Any) -> None:
    """
    Run the database editor to modify base databases with IMAGE information and future scenarios.

    Parameters:
    - updated_database (str): Name of the updated database.
    - base_database (str): Name of the base database.
    - base_project (str): Name of the base project.
    - updated_project_name (str): Name of the updated project.
    - iam_model (str): IAM model name.
    - iam_model_key (str): IAM model key.
    - bw: Brightway2 instance.
    """
    from image_ecoinvent_updater.main_database_editor import editor
    editor(updated_database=updated_database, base_database=base_database, base_project=base_project,
           updated_project_name=updated_project_name, iam_model=iam_model, iam_model_key=iam_model_key, bw=bw)

def main() -> None:
    """
    Main function to execute the LIAISON model.
    """
    parser = argparse.ArgumentParser(description='Execute LIAISON model')
    parser.add_argument('--datapath', help='Path to the input and output data folder.')
    parser.add_argument('--envpath', help='Path to the environments folder.')
    parser.add_argument('--lca_config_file', help='Name of life cycle information config file in data folder.')
    args = parser.parse_args()

    tim0 = time.time()
    print('Starting the Code',flush=True)

    config = load_config_file(args.datapath, args.lca_config_file)
    flags = config.get('flags', {})
    scenario_params = config.get('scenario_parameters', {})
    data_dirs = config.get('data_directories', {})
    inputs = config.get('input_filenames', {})
    outputs = config.get('output_filenames', {})

    set_brightway2_dir(args.envpath)



    print('Importing brightway module.....',flush=True)
    import brightway2 as bw
    from liaison.liaison_model import main_run
    from liaison.ecoinvent_explorer import extract_electricity_mix

    # Project parameters
    project = scenario_params.get('project_name')
    primary_process = scenario_params.get('process')
    process_under_study = scenario_params.get('primary_process_to_study')
    location_under_study = scenario_params.get('location')
    updated_database = scenario_params.get('updated_database')
    updated_project_name = scenario_params.get('updated_project_name')
    lca_project_name = scenario_params.get('lca_project_name')
    mc_runs = int(scenario_params.get('mc_runs'))
    base_database = scenario_params.get('base_database')
    base_project = scenario_params.get('base_project')
    region = scenario_params.get('region')
    initial_year = scenario_params.get('initial_year')
    iam_model = scenario_params.get('model')
    iam_model_key = scenario_params.get('model_key')
    functional_unit = scenario_params.get('functional_unit')
    unit_under_study = scenario_params.get('unit')

    # File paths
    data_path = os.path.join(args.datapath, data_dirs.get('liaisondata'))
    creation_inventory_filename = os.path.join(data_path, inputs.get('creation_inventory'))
    foreground_inventory_filename = os.path.join(data_path, inputs.get('foreground_inventory'))
    modification_inventory_filename = os.path.join(data_path, inputs.get('modification_inventory'))
    process_name_bridge = os.path.join(data_path, inputs.get('process_bridge'))
    emission_name_bridge = os.path.join(data_path, inputs.get('emission_bridge'))
    location_name_bridge = os.path.join(data_path, inputs.get('location_bridge'))
    ecoinvent_file = os.path.join(data_path, data_dirs.get('ecoinvent_data'))
    results_filename = outputs.get('results_filename')
    output_dir = os.path.join(args.datapath, data_dirs.get('output'))
    data_dir = os.path.join(args.datapath, data_path)

    # Flags
    run_database_reader_flag = flags.get('read_base_lci_database')
    run_database_editor_flag = flags.get('update_base_database_with_future_information')
    run_lca_on_base_database_flag = flags.get('use_base_database_for_lca')
    uncertainty_corrections = flags.get('correct uncertainty')
    mc_foreground_flag = flags.get('mc_foreground')
    lca_flag = flags.get('lca')
    lca_activity_modification = flags.get('lca_activity_modification')
    regional_sensitivity_flag = flags.get('regional_sensitivity')

    print('All input data parameters read',flush=True)

    # Running database reader for reading ecoinvent base database
    if run_database_reader_flag:
        print('Running db reader',flush=True)
        run_database_reader(ecoinvent_file=ecoinvent_file, base_database=base_database, base_project=base_project, bw=bw)

    # Running database editor for modifying base databases with IMAGE information and future scenario
    if run_database_editor_flag:
        print('Running db editor',flush=True)
        run_database_editor(updated_database=updated_database, base_database=base_database, base_project=base_project,
                            updated_project_name=updated_project_name, iam_model=iam_model, iam_model_key=iam_model_key, bw=bw)
    # Copies the base project if updater is not required for LCA calculations, Stores the base database in a new project name for lca calculations. 
    if run_lca_on_base_database_flag:
        updated_database = base_database
        updated_project_name = base_project

    create_directory(output_dir)
    #remove_old_results(output_dir)

    if lca_flag:
        print('extracing_electricity_mix',flush=True)
        extract_electricity_mix(updated_project_name=updated_project_name, output_dir=output_dir, results_filename=results_filename,
                       updated_database=updated_database, bw=bw)
        print('electricity_mix_extracted',flush=True)
        print('lca calculation starts',flush=True)
        main_run(
                lca_project=lca_project_name,
                updated_project_name=updated_project_name,
                year_of_study=str(initial_year),                      # renamed from initial_year
                results_filename=results_filename,
                mc_foreground_flag=mc_foreground_flag,
                lca_flag=lca_flag,
                region_sensitivity_flag=regional_sensitivity_flag,    # renamed from regional_sensitivity_flag
                edit_ecoinvent_user_controlled=lca_activity_modification,  # renamed from lca_activity_modification
                region=region,
                data_dir=data_dir,
                primary_process=primary_process,
                process_under_study=process_under_study,
                location_under_study=location_under_study,
                unit_under_study=unit_under_study,                    # required in old definition
                updated_database=updated_database,
                mc_runs=mc_runs,
                functional_unit=functional_unit,
                inventory_filename=foreground_inventory_filename,
                output_dir=output_dir,
                bw=bw
            )


    pprint(time.time() - tim0)

if __name__ == "__main__":
    main()
