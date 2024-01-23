import sys
import yaml
import os
import time
import warnings
import shutil
warnings.filterwarnings("ignore")
#import the config file
import argparse
parser = argparse.ArgumentParser(description='Execute LIAISON model')
parser.add_argument('--datapath', help='Path to the input and output data folder.')
parser.add_argument('--lca_config_file', help='Name of life cycle information config file in data folder.')
args = parser.parse_args()
tim0 = time.time()
print('Starting the Code',flush=True)
# YAML filename
config_yaml_filename = os.path.join(args.datapath, args.lca_config_file)

try:
    with open(config_yaml_filename, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        flags = config.get('flags', {})
        scenario_params = config.get('scenario_parameters', {})
        data_dirs = config.get('data_directories', {})
        inputs = config.get('input_filenames', {})
        outputs = config.get('output_filenames', {})
        
        
except IOError as err:
    print(f'Could not open {config_yaml_filename} for configuration. Exiting with status code 1.')
    exit(1)


#importing brightway modules from saved location
print('Importing brightway module.....',flush=True)

import brightway2 as bw
print('Imported',flush= True)
from liaison.liaison_model import main_run
from image_ecoinvent_updater.main_database_reader import reader
from image_ecoinvent_updater.main_database_editor import editor
from liaison.ecoinvent_explorer import electricity_mix


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

creation_inventory_filename = os.path.join(args.datapath,
                                  data_dirs.get('liaisondata'),
                                  inputs.get('creation_inventory'))
foreground_inventory_filename = os.path.join(args.datapath,
                                  data_dirs.get('liaisondata'),
                                  inputs.get('foreground_inventory'))
modification_inventory_filename = os.path.join(args.datapath,
                                  data_dirs.get('liaisondata'),
                                  inputs.get('modification_inventory'))
process_name_bridge = os.path.join(args.datapath,
                                  data_dirs.get('liaisondata'),
                                  inputs.get('process_bridge'))
emission_name_bridge = os.path.join(args.datapath,
                                  data_dirs.get('liaisondata'),
                                  inputs.get('emission_bridge'))
location_name_bridge = os.path.join(args.datapath,
                                  data_dirs.get('liaisondata'),
                                  inputs.get('location_bridge'))
ecoinvent_file = os.path.join(args.datapath,
                                  data_dirs.get('liaisondata'),
                                  data_dirs.get('ecoinvent_data'))

results_filename = outputs.get('results_filename')

output_dir = os.path.join(args.datapath,
                          data_dirs.get('output'))

data_dir = os.path.join(args.datapath,
                          data_dirs.get('liaisondata'))


run_database_reader = flags.get('read_base_lci_database')
run_database_editor = flags.get('update_base_database_with_future_information')
run_lca_on_base_database = flags.get('use_base_database_for_lca')
uncertainty_corrections = flags.get('correct uncertainty')
mc_foreground_flag = flags.get('mc_foreground')
lca_flag=flags.get('lca')
lca_activity_modification=flags.get('lca_activity_modification')
regional_sensitivity_flag=flags.get('regional_sensitivity')

print('All input data parameters read', flush = True)

#Running database reader for reading ecoinvent base database    
if run_database_reader:
    print('Running db reader', flush = True)
    reader(
           ecoinvent_file = ecoinvent_file,
           base_database = base_database,
           base_project = base_project,
           bw = bw           
           )

#Running database editor for modifying base databases with IMAGE information and future scenario    
if run_database_editor:
    print('Running db editor', flush = True)
    editor(updated_database = updated_database,
           base_database = base_database,
           base_project = base_project,
           updated_project_name = updated_project_name,
           iam_model=iam_model,
           iam_model_key=iam_model_key,
           bw = bw
           )           
#Copies the base project if updater is not required for LCA calculations)
#Stores the base database in a new project name for lca calculations. 
#If false LCA is done on updated database. 
if run_lca_on_base_database:
    updated_database = base_database
    updated_project_name = base_project
else:
    pass

#Create results directory
try:
    os.makedirs(output_dir)
except:
    pass

#Removing results file
remove_old_results= False
if remove_old_results:
    try:
        for f in os.listdir(output_dir):
           os.remove(os.path.join(output_dir, f))
    except:
        pass

if lca_flag:
    
    main_run(lca_project=lca_project_name,
             updated_project_name=updated_project_name,
             initial_year=initial_year,
             results_filename=results_filename, 
             mc_foreground_flag=mc_foreground_flag,
             lca_flag=lca_flag,
             lca_activity_modification=lca_activity_modification,
             regional_sensitivity_flag=regional_sensitivity_flag,
             region=region,
             data_dir=data_dir,
             primary_process=primary_process,
             process_under_study=process_under_study, 
             location_under_study=location_under_study,
             functional_unit=functional_unit,
             updated_database=updated_database, 
             mc_runs=mc_runs,
             inventory_filename = foreground_inventory_filename,
             modification_inventory_filename = modification_inventory_filename,
             process_name_bridge = process_name_bridge,
             emission_name_bridge = emission_name_bridge,
             location_name_bridge = location_name_bridge,
             output_dir= output_dir,
             bw=bw)

electricity_mix_output=False
if electricity_mix_output:

    electricity_mix(updated_project_name=updated_project_name,
                        output_dir= output_dir,
                        results_filename=results_filename, 
                        updated_database=updated_database, 
                        bw = bw)




print(time.time()-tim0) 