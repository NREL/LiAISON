import os
import shutil
import argparse
import time
import warnings
from pprint import pprint
from typing import Dict, Any
import yaml

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
    except:
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
    pprint('Starting the Code')

    set_brightway2_dir(args.envpath)


    pprint('Importing brightway module.....')
    import brightway2 as bw

    import bw2io

    updated_project_name = args.lca_config_file
    bw2io.backup.backup_project_directory(project= updated_project_name)


    pprint(time.time() - tim0)

if __name__ == "__main__":
    main()
