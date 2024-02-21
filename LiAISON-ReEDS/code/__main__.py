import sys
import yaml
import os
import time
import warnings
warnings.filterwarnings("ignore")
#import the config file
import argparse
parser = argparse.ArgumentParser(description='Execute LIAISON model')
parser.add_argument('--database', help='Name of database to be created.')
parser.add_argument('--datapath', help='Path to the input and output data folder.')
parser.add_argument('--envpath', help='Path to the environments folder.')
parser.add_argument('--lca_config_file', help='Name of life cycle information config file in data folder.')
args = parser.parse_args()
tim0 = time.time()
print('Starting the Code',flush=True)
# YAML filenameß
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



brwtway2 = str(args.envpath)
#importing brightway modules from saved location
os.environ['BRIGHTWAY2_DIR']= str(brwtway2)
print('Importing brightway module.....',flush=True)
import brightway2 as bw
print('Imported',flush= True)
from reeds_ecoinvent_updater.main_database_reader import reader
from reeds_ecoinvent_updater.main_database_editor import reeds_updater
from liaison.liaison_model import main_run

lca_project_name = scenario_params.get('lca_project_name')
primary_process = scenario_params.get('process')
process_under_study = scenario_params.get('primary_process_to_study')
location_under_study = scenario_params.get('location')
updated_database = scenario_params.get('updated_database')
updated_project_name = scenario_params.get('updated_project_name')
mc_runs = int(scenario_params.get('mc_runs'))
base_database = scenario_params.get('base_database')
base_project = scenario_params.get('base_project')
region = scenario_params.get('region')
initial_year = scenario_params.get('initial_year')



creation_inventory_filename = os.path.join(args.datapath,
                                  data_dirs.get('liaisondata'),
                                  data_dirs.get('reeds_data'),
                                  inputs.get('creation_inventory'))
foreground_inventory_filename = os.path.join(args.datapath,
                                  data_dirs.get('liaisondata'),
                                  inputs.get('foreground_inventory'))
modification_inventory_filename = os.path.join(args.datapath,
                                  data_dirs.get('liaisondata'),
                                  data_dirs.get('reeds_data'),
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
                                  data_dirs.get('ecoinvent_data'))

## Fix this
ecoinvent_file = "/projects/liaison/ecoinvent/ecoinvent_3.8_cutoff_ecoSpold02/datasets/"
                                  
results_filename = outputs.get('results_filename')
output_dir = os.path.join(args.datapath,
                          data_dirs.get('output'))
data_dir = os.path.join(args.datapath,
                          data_dirs.get('liaisondata'))
## Fix this
creation_inventory_filename = os.path.join("/projects/liaison/hipster_data/reeds_to_hipster_dev/reedsdata/",inputs.get('creation_inventory'))

run_database_reader = flags.get('run_database_reader')
run_database_editor = flags.get('run_database_editor')
uncertainty_corrections = flags.get('correct uncertainty')
mc_foreground_flag = flags.get('mc_foreground')
lca_flag=flags.get('lca')
lca_activity_modification=flags.get('lca_activity_modification')
regional_sensitivity_flag=flags.get('regional_sensitivity')
create_new_database=flags.get('create_new_database')
premise_editor= flags.get('premise_editor')

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
    reeds_updater(
         process_name_bridge = process_name_bridge,
         emission_name_bridge = emission_name_bridge,
         location_name_bridge = location_name_bridge,
         initial_year=initial_year,
         results_filename=results_filename, 
         lca_activity_modification=lca_activity_modification,
         create_new_database=create_new_database,
         data_dir=data_dir,
         inventory_filename = creation_inventory_filename,
         modification_inventory_filename = modification_inventory_filename,
         premise_editor=premise_editor,
         base_database=base_database,
         base_project = base_project,
         database_new = updated_database,
         project_new = updated_project_name,
         bw=bw)


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
             updated_database=updated_database, 
             mc_runs=mc_runs,
             inventory_filename = foreground_inventory_filename,
             modification_inventory_filename = modification_inventory_filename,
             process_name_bridge = process_name_bridge,
             emission_name_bridge = emission_name_bridge,
             location_name_bridge = location_name_bridge,
             output_dir= output_dir,
             bw=bw)

print(time.time()-tim0) 
      
