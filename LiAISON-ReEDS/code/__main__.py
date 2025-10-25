import sys
import yaml
import os
import time
import warnings
warnings.filterwarnings("ignore")
#import the config file
import argparse
parser = argparse.ArgumentParser(description='Execute LIAISON model')
parser.add_argument('--datapath', help='Path to the input and output data folder.')
parser.add_argument('--envpath', help='Path to the environments folder.')
parser.add_argument('--lca_config_file', help='Name of life cycle information config file in data folder.')
args = parser.parse_args()
tim0 = time.time()
print('Starting the Code',flush=True)
# YAML filename
config_yaml_filename = os.path.join(args.datapath,'yaml' ,args.lca_config_file)
data_yaml_filename = os.path.join(args.datapath, 'yaml','data_dir.yaml')
try:
    with open(config_yaml_filename, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        flags = config.get('flags', {})
        scenario_params = config.get('scenario_parameters', {})
        data_dirs = config.get('data_directories', {})
        inputs = config.get('input_filenames', {})
        outputs = config.get('output_filenames', {})
        options = config.get('additional_options', {})
    
    with open(data_yaml_filename, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        data_dirs = config.get('data_directories', {})
        
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

# scenario parameters from the yaml file
lca_project_name = scenario_params.get('lca_project_name')
primary_process_under_study = scenario_params.get('primary_process_to_study')
mc_runs = int(scenario_params.get('mc_runs'))
functional_unit = float(scenario_params.get('functional_unit'))
location_under_study = scenario_params.get('location_under_study')
year_of_study = scenario_params.get('year')
unit_under_study = scenario_params.get('unit')
reeds_yaml_data_filename = os.path.join(args.datapath,inputs.get('reeds_yaml_data'))
region = location_under_study

#Hardcoding these project names to reduce yaml file complexity
base_database = "ecoinvent3.8"
base_project = "premise_base"
# These modified projects and databases are used to save the large modified ecoinvent databases for future LCA calculations. 
# We can change this but then we need to copy the premise base into the updated database name and then perform edits. Takes more time. 
updated_database = "premise_base" # These project name is used to create a new project after major modifications to original ecoinvent. These can include premise updates or ReEDS grid mix updates
updated_project_name = str(inputs.get('reeds_yaml_data')) # These project name is used to create a new project after major modifications to original ecoinvent. These can include premise updates or ReEDS grid mix updates



foreground_inventory_filename = os.path.join(args.datapath,
                                  data_dirs.get('liaisondata'),
                                  inputs.get('foreground_inventory'))
ecoinvent_file = os.path.join(args.datapath,
                                  data_dirs.get('ecoinvent_data'))
                                  
results_filename = outputs.get('results_filename')
output_dir = os.path.join(args.datapath,
                          data_dirs.get('output'))
data_dir = os.path.join(args.datapath,
                          data_dirs.get('liaisondata'))
reeds_dir = os.path.join(args.datapath,data_dirs.get('liaisondata'),data_dirs.get('reeds_data'))


run_database_reader = flags.get('ecoinvent_reader')
uncertainty_corrections = flags.get('correct uncertainty')
mc_foreground_flag = options.get('mc_foreground')
lca_flag=flags.get('lca')
premise_editor= flags.get('update_ecoinvent_using_premise')
reeds_grid_mix_creator = flags.get('reeds_us_electricity_grid_mix')
region_sensitivity_flag = options.get('region_sensitivity_flag')
edit_ecoinvent_user_controlled = options.get('edit_ecoinvent_user_controlled')


if reeds_grid_mix_creator:
    # Reading the ReEDS yaml file name
    try:
        with open(reeds_yaml_data_filename+'.yaml', 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            reeds_inputs = config.get('input_filenames', {}) 

            # Filenames for inventories
            # only the reeds data is in a different folder for now. 
            reeds_inventory_filename = os.path.join(reeds_dir,
                                              reeds_inputs.get('reeds_inventory'))
            modification_inventory_filename = os.path.join(reeds_dir,
                                              reeds_inputs.get('modification_inventory'))
            modification_inventory_filename_us = os.path.join(reeds_dir,
                                              reeds_inputs.get('modification_inventory_us'))

    except IOError as err:
        print(f'Could not open {reeds_yaml_data_filename} for configuration. Exiting with status code 1.')
        exit(1)




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
if reeds_grid_mix_creator:
    print('Running db editor', flush = True)
    reeds_updater(
         year_of_study=year_of_study,
         results_filename=results_filename, 
         reeds_grid_mix_creator = reeds_grid_mix_creator,
         data_dir=data_dir,
         inventory_filename = reeds_inventory_filename,
         modification_inventory_filename = modification_inventory_filename,
         modification_inventory_filename_us = modification_inventory_filename_us,
         premise_editor=premise_editor,
         base_database=base_database,
         base_project = base_project,
         database_new = updated_database,
         project_new = updated_project_name,
         bw=bw
         )


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
             year_of_study=year_of_study,
             results_filename=results_filename, 
             mc_foreground_flag=mc_foreground_flag,
             lca_flag=lca_flag,
             region_sensitivity_flag=region_sensitivity_flag,
             edit_ecoinvent_user_controlled = edit_ecoinvent_user_controlled,
             region=region,
             data_dir=data_dir,
             primary_process=primary_process_under_study,
             process_under_study=primary_process_under_study, 
             location_under_study=location_under_study,
             unit_under_study=unit_under_study,
             updated_database=updated_database, 
             mc_runs=mc_runs,
             functional_unit=functional_unit,
             inventory_filename = foreground_inventory_filename,
             output_dir= output_dir,
             bw=bw)

print(time.time()-tim0) 
          
