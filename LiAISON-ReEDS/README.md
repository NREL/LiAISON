## LiAISON-ReEDS

# Lifecyle Analysis Integration into Scalable Opensource Numerical models (LiAISON) with ReEDS

## Objective

**Perform**
1. Life cycle assessment calculations of standard ReEDS scenarios. 
2. Perform life cycle assessment using predicted grid energy system based on standard ReEDS scenarios. 


## Requirements
-   **Python 3.9, 3.10 or 3.11**
-   License for [ecoinvent 3](https://www.ecoinvent.org/)
-   To use prospective life cycle assessment, LiAISON requires [premise](https://github.com/polca/premise). If you wish to use those premise, **you need to request (by [email](mailto:romain.sacchi@psi.ch)) an encryption key from the developers**
-   [brightway2](https://brightway.dev/) 

## How to install this package?
### Root Folder 
folder-LiAISON repository : */LiAISON*


### Setup
- Install [anaconda prompt](https://www.anaconda.com/products/individual) (Windows) or conda on Mac and Linux Machines. 

- Open Terminal (MAC and Linux) or Anaconda prompt(Windows).

- Navigate to the */conda* folder of LiAISON repository in the terminal.

- Type following commands 

  - ```conda env create -f environment_tutorial.yml -n liaison-24```
  - ```conda activate liaison-24```
  - ```pip install premise==1.8.1```

- You will get an error message that the version of bw2io is not compatible. bw2io package will get upgraded to the latest version. However, we need to install a lower version as ```bw2io==0.8.7``` is the correct version required for Ecoinvent 3.8. For other versions, use ```bw2io > 0.8.8```
- ```pip install bw2io==0.8.7```

- If you have problems with installation of premise, please try 
- ```conda install conda-forge::premise=1.8.1```
#### If environment building does not work from yaml file

- Type following commands

  - ```conda create -n liaison-24 python=3.10```
  - ```conda activate liaison-24```
  - ```pip install brightway2==2.4.3```
  - ```pip install pyyaml==5.4.1```
  - ```pip install premise==1.8.1``` or  ```conda install conda-forge::premise=1.8.1```
  - ```pip install openpyxl==3.1.2```
  - ```pip install bw2io==0.8.7```
  - ```pip install bw2analyzer==0.10```
  

### Extracting Ecoinvent
- Download **ecoinvent version 3.8 allocation cutoff by substitution** from the website. The filename is ```ecoinvent 3.8_cutoff_ecoSpold02.7z``` and is around 61MB in size.
- Extract required ecoinvent database from ```ecoinvent 3.8_cutoff_ecoSpold02.7z``` into a folder in */data/inputs/ecoinvent.*
- Rename the extracted folder name to *ecoinvent_3.8_cutoff_ecoSpold02.7z*. Add an underscore between ecoinvent and 3.8.

## How to test run LiAISON-ReEDS ?
Perform a complete test run through these following steps - 
- Open a terminal in the root folder. 
- Type the following commands in the terminal
  - `chmod +x test_run.sh`
  - `./test_run.sh`
 
### Results
- After running, csv result files are written in the *data/output/* file. 
- */plotting* folder contains a visualizer.py file to create plots based on the result files in the */data/output* folder 

**Details of life cycle assessment calculations, developer options, prospective life cycle assessment calculations and other relevant information are provided in the documentation.** 

## Support
Email: tghosh@nrel.gov. 

## Contributors
[Patrick Lamers](plamers@nrel.gov)
[Teagan Goforth](tgoforth@cmu.edu)

## Maintainers
Tapajyoti Ghosh



# LiAISON-ReEDS 

Harmonized Impacts of Products, Scenarios, and Technologies across Environmental and Resource use metrics (LiAISON-ReEDS).Prospective Life cycle assessment 

## ReEDS

We connect the Regional Energy Deployment System (ReEDS), a capacity expansion model, to EcoInvent inventories to account for life cycle impacts given different electricity system outcomes. We use generation, emissions, and heat rate data from ReEDS to update EcoInvent databases with generation, emissions, and fuel rate information specific to each ReEDS technology. Harmonized Impacts of Products, Scenarios, and Technologies across Environmental and Resource use metrics (LiAISON-ReEDS).

/Root folder-LiAISON-ReEDS repository - **LiAISON-ReEDS**


## Setup
- Install [anaconda prompt](https://www.anaconda.com/products/individual) (Windows) or conda on Mac and Linux Machines. 

- Open Terminal (MAC and Linux) or Anaconda prompt(Windows).

- Navigate to the */conda* folder of LiAISON-ReEDS repository in the terminal.

- Type following commands for windows pc

  - ```conda env create -f environment_tutorial.yml -n LiAISON-ReEDS-23```


  - ```conda activate LiAISON-ReEDS-23```

- Type following commands for mac

  - ```conda env create -f environment_tutorial.yml -n LiAISON-ReEDS-23```

  - ```conda activate LiAISON-ReEDS-23```


### If environment building does not work from yaml file

- Type following commands

  - ```conda create -n LiAISON-ReEDS-23 python=3.9```
  - ```conda activate LiAISON-ReEDS-23```
  - ```pip install brightway2==2.3```
  - ```pip install pyyaml==5.4.1```
  - ```pip install premise==1.5.7```
  - ```pip install openpyxl==3.0.9```
  - ```pip install bw2io==0.8.7```
  - ```pip install bw2analyzer==0.10```
  

## Extracting Ecoinvent
Extract required ecoinvent database from the **ecoinvent3.x.7z** file and store in within a folder for running LiAISON-ReEDS in the next steps. By default, the file is in the **ecoinvent.7z** file in */data/inputs/ecoinvent.*

## Running LiAISON-ReEDS

LiAISON-ReEDS can be run through these following steps - 

 - Create a **conda environment** with the suitable packages on your machine. 
 - In the */data* folder, edit the **configuration yaml file**. (Check step 2 *OR* step 3)
 - Make sure the **reeds data files and market updated reeds inventory** files are present in the */data/inputs/reeds_data/* folder. ( Will be updated later on integration of ReEDS-LiAISON-ReEDS framework and LiAISON-ReEDS)
 - Make sure the **emission_bridge, process_name_bridge, location_bridge** files located in the */data/inputs* folder are present and properly formatted. 
 - Make sure the **foreground inventory** is present in the */data/inputs* folder and properly formatted. 
 - Make sure the **ecoinvent folder** with the **ecoinvent files** are present in a specific directory. 
 - Run **LiAISON-ReEDS** (check step 3).
 - Check results in in the */data/outputs* folder.

### Step 1:  Creation of brightway2 environment folder. 
Create an environment folder for brightway2 environments in an address with enough disk space. Can be created in the root. Brightway2 creates an environment folder in the system path of your machine. (*Appdata* for Windows, *Library* for MAC).  The environment folder can be changed to user specified directory if needed. Create a directory if required and point to that directory path. Create an environment folder for brightway2 environments in an address with enough disk space

### Step 2: Build databases / Run for the first time

- For a first time run or when new scenario/year case studies are required three parameters needs to be switched to the True position in the **config_yaml file**
```
  lca: True
  run_database_reader: True
  run_database_editor: True 
```  

### OR 
### Step 3: Run for life cycle assessment analysis on existing databases

- Change to false for faster compilation 
```
  run_database_reader: False
  run_database_editor: False 
```


### Step 4_1: LiAISON-ReEDS run command through run.sh file
- Edit the run.sh file with relevant directory information
  
      ENVPATH="/Users/tghosh/Desktop/LiAISON-ReEDS/env"
      CODEDIR="/Users/tghosh/Desktop/LiAISON-ReEDS/code"
      DATADIR="/Users/tghosh/Desktop/LiAISON-ReEDS/data"
      yaml="simplelca"
      
   - **DATADIR**: This is the path to the data folder of the LiAISON-ReEDS repository. 
   - **ENVPATH**: This is the path to the environment folder of Brightway2. Brightway2 creates an environment folder in the system path of your machine. (Appdata for Windows, Library for MAC).  The environment folder can be changed to user specified directory if needed. Create a directory if required and point to that directory path. Create an environment folder for brightway2 environments in an address with enough disk space
   - **CODEDIR**: This is the path to the code directory within the LiASON root folder. 
   - **yaml**: The name of the config yaml file being used for the run. 
- **Type the following commands in the terminal**
  - `chmod +x run.sh`
  - `./run.sh`
  
### Step 4_2: LiAISON-ReEDS run command through command line

```python __main__.py --datapath=*path-to-data-folder* --envpath=*path-to-environment-folder* --lca_config_file=*path-to-scenario-yaml-file*```

 - **path-to-data-folder**: This is the path to the data folder of the LiAISON-ReEDS repository. 
 - **path-to-enviroment-folder**: This is the path to the environment folder of Brightway2. Brightway2 creates an environment folder in the system path of your machine. (Appdata for Windows, Library for MAC).  The environment folder can be changed to user specified directory if needed. Create a directory if required and point to that directory path. Create an environment folder for brightway2 environments in an address with enough disk space
 - **path-to-scenario-yaml-file**: This is the path to the scenario yaml file. Two files are provided within the data folder. 
 - **Example for MAC Users** : ```python __main__.py --datapath=/Users/myname/LiAISON-ReEDS/data --envpath=/Users/myname/env --lca_config_file=/Users/myname/Dynamic-LCA-with-LiAISON-ReEDS/data/simplelca.yaml```

 - **Example for Windows Users** : ```python __main__.py --datapath="C:\documents\myname\Dynamic-LCA-with-LiAISON-ReEDS\data" --envpath="C:\documents\myname\env" --lca_config_file="C:\documents\myname\LiAISON-ReEDS\data\peme.yaml"```

## Results
- After running, csv result files are written in the *data/output/* file. 
- */plotting* folder contains a visualizer.py file to create plots based on the result files in the */data/output* folder 

## Developer information

The next part of the tutorial is helpful for LCA researchers to build **inventories, bridging core and configuration files** for life cycle analysis. It also focuses on discussion of the **ReEDS LiAISON-ReEDS framework.**

### ReEDS LiAISON-ReEDS Framework
 - Discussion on core input files.
 - Discussion of ReEDS output files.
 - Discussion of ReEDS scenarios.
 - Discussion of ReEDS regions.
 - Discussion of matching of technologies between ReEDS and Ecoinvent. 
 - Discussion of caveats and assumptions. 
 - Discussion of creation of grid mix at different spatial levels. 
 - Linking of this framework with LiAISON-ReEDS. 


###  Details of the config_yaml file

- Two yaml files are provided in the data folder corresponding to
  - SimpleLCA process for doing an LCA for electricity production
  - ForegroundBuilderLCA process for building a foreground inventory and then performing  LCA for an hydrogen electrolysis process. 

Example: **simplelca.yaml**
```
data_directories:
  ecoinvent_data: ecoinvent/ecoinvent_3.8_cutoff_ecoSpold02/datasets/
  liaisondata: inputs/
  reeds_data: reeds_data/
  output: output/
flags:
  correct uncertainty: false
  mc_foreground: false
  lca: true
  lca_activity_modification: true
  run_database_editor: true
  run_database_reader: false
  regional_sensitivity: false
input_filenames:
  emission_bridge: emission_name_bridge.csv
  creation_inventory: Mid_Case2020_reeds_data.csv
  foreground_inventory: example.csv
  modification_inventory: market_updated_reeds_inventory.csv
  location_bridge: location_bridge.csv
  process_bridge: process_name_bridge.csv
output_filenames:
  results_filename: lcia_results
scenario_parameters:
  base_database: ecoinvent3.8
  base_project: base_project_ecoinvent38
  initial_year: 2020
  lca_project_name: LiAISON-ReEDS_training
  location: US
  mc_runs: 1
  primary_process_to_study: market group for electricity, high voltage new test
  process: electricity
  updated_database: ecoinvent_2020_ReedsMidCase
  updated_project_name: reed_grid_2020

```

 - **data_directories**
   - ecoinvent: points to ecoinvent folder and ecoinvent version to be used for the analysis. 
   - ecoinventdata: data folder location for ecoinvent data files. 
   - image: data folder for the IMAGE files
   - LiAISON-ReEDSdata: data folder for the files for running 
   - reeds_data: data folder for the ReEDS input files from the ReEDS-LiAISON-ReEDS framework.
   - output: folder for the output results
   
 - **flags**
     - correct uncertainty: correction of uncertainty issues in the ecoinvent dataset. 
     - mc_foreground: monte carlo of the foreground inventory to be done.
     - lca: flag for doing life cycle assessment calculations
     - lca_activity_modification: life cycle inventory needs to be modified if required. This is required for developing LiAISON-ReEDS because this makes sure the market mix for US grid mix electricity within ecoinvent is updated with the ReEDS generated US grid mix. Thus all activities in the background LCI uses ReEDS grid mix. 
     - run_database_editor: flag for running the database editor which edits the old database and updates it with new information. Also stores the database in a project. 
     - run_database_reader: flag for running the database reader which reads the ecoinvent data and stores it in a project. 
     - regional_sensitivity: flag for changing regions and performing sensitivity on regions without changing the input excel file. 

 - **input_filenames**:

   - emission_bridge: emission bridge file name.
   - creation_inventory: This points to the ReEDS input files from the ReEDS LiAISON-ReEDS framework with the ReEDS output data, grid mixes at different spatial levels, etc. 
   - foreground_inventory: input data file for life cycle inventory of the process under study. 
   - modification_inventory: input data file for modification of existing datasets in ecoinvent. Required for LiAISON-ReEDS to modify the US grid mix within the ecoinvent database. 
   - location_bridge: location bridge file name.
   - process_bridge:  process bridge file name.


 - **output_filenames:**
    - results_filename: life cycle calculation results output file. 

 - **scenario_parameters**:
   - base_database: base ecoinvent database used for study.
   -  base_project: base project name for ecoinvent.
   - initial_year: first year of analysis.
   -  lca_project_name: lca study project name.
   - learning_rate: learning rate for technology efficiency. Currently removed from the model because too aligned to case study. 
   - location: foreground study location. 
   -  mc_runs: monte carlo run numbers
   - primary_process_to_study: the primary  process under study in the datasets file. 
   - process: the process name for results file.
   - technology_efficiency: efficiency of the technology under study. Currently removed from the model because too aligned to case study. 
   - updated_database: modified database name.
   - updated_project_name: modified project name with modified database.

- For a first time run or when new scenario/year case studies are required three parameters needs to be switched to the on position. 
```
  run_database_reader: True
  run_database_editor: True
```

###  Editing the foreground inventory file

 - The foreground inventory needs to be edited according to the dataset provided.  The column names are provided in the example dataset - *example.csv*
 - Columns for the foreground inventory file.
   - process: Name of the process being created
   - flow: biosphere, techno-sphere, production flows going into the foreground process being created. 
   - unit: unit of the flows
   - value: amount of the flows
   - year: process study year
   - input: boolean for showing if a flow is an input flow (True) or an output flow(False)
   - type: type of flow: production, biosphere, technosphere. 
   - comments
   - process_location : location of the process under study
   - supplying_location : location of the processes supplying the technosphere flows to the process under study. 

### Editing the process bridge file

- The process bridge file is used for linking the names of the technosphere flows in the foreground inventory dataset to the processes in ecoinvent supplying the required input flow as an output product. 
- The columns in this file consist of Common name, Ecoinvent name, Ecoinvent code and type of flow. Common name is the one given by process, Ecoinvent name is the matched name from the ecoinvent activity, Ecoinvent code is the key code of the process from ecoinvent and the type of flow. 

### Editing the location bridge file

- The location bridge file is used for linking the names of the locations in the foreground inventory dataset. location_common ( provided by the user) and location_ecoinvent (matched with the location from ecoinvent). 

### Editing the emissions bridge file
- The emissions bridge file is used for linking the names of the biosphere flows from the foreground inventory dataset to the emissions in the biosphere of brightway2 and ecoinvent. 
- The columns in this file consist of Common name, Ecoinvent name, Ecoinvent code. Common name is the one given by process, Ecoinvent name is the matched name from the ecoinvent activity, Ecoinvent code is the key code of the process from ecoinvent.




