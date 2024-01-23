# Lifecyle Analysis Integration into Scalable Opensource Numerical models (LiAISON)
![Logo](https://github.com/NREL/LiAISON/blob/dev/images/logo.png?raw=true)

Scientific publication available here: https://pubs.acs.org/doi/full/10.1021/acs.est.2c04246. 
## Objective

**Perform**
1. Life cycle assessment calculations where the foreground inventory gets linked automatically to the background inventory.
2. Prospective life cycle assessment using long-term, coherent scenarios of the energy-economy-land-climate system to quantify the effects of background system changes and foreground technology improvements for various technologies.
3. Regional life cycle assessment calculations.
4. Monte carlo sensitivity analysis of foreground inventory.
5. Coded life cycle assessment framework to add LCA to your project.



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

## How to test run LiAISON ?
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
[Soomin Chun](schun@nrel.gov)
Shubhankar Upasani
Alberta Carpenter
[Romain Sacchi](romain.sacchi@psi.ch.)

## Maintainers
Tapajyoti Ghosh

# Documentation


## LiAISON Development, Methodology and Life Cycle Assessment application
![Screenshot-2024-01-18-at-10-26-15-AM](https://github.com/NREL/LiAISON/blob/dev/images/image2.png?raw=true)
## Objectives
1. **Static life cycle assessment calculations** where the foreground inventory gets linked automatically to the background inventory.
2. **Prospective life cycle assessment** using long-term, coherent scenarios of the energy-economy-land-climate system to quantify the effects of background system changes and foreground technology improvements for various technologies.
3. **Regional life cycle assessment** calculations.
4. Monte carlo sensitivity analysis of foreground inventory.

## Benefits
1. Helps simplify life cycle assessment by automating linking of foreground inventory with background life cycle inventory
2. Large number of LCA calculations performed simultaneously with ”another” model.
    - Systems scale simulation
    - Optimization
3. Complex variations of foreground system for scenario analysis.
4. Continuous variations of input data.
5. Sensitivity analysis on individual system parameters.
6. Uncertainty analysis with larger control on your modeled activities.
7. Regional analysis
8. Variation of background data (temporally, spatially or scenario-wise).

## Methodology
![Screenshot-2024-01-18-at-11-02-05-AM](https://github.com/NREL/LiAISON/blob/dev/images/image4.png?raw=true)LiAISON framework can be separated into three separate parts - 
1. Reading the base life cycle inventory **(Life cycle inventory reader)**
2. Updating the base life cycle inventory with present and future information from Integrated Assessment models.  **(Prospective life cycle inventory updater)**
3. Performing life cycle assessment. **(Automated LCA calculator)**

Separating LiAISON into three separate parts provides several benefits.
- Reading the base life cycle inventory (*ecoinvent 3.8*) takes time. Reading it once, storing it and using the stored data significantly reduces computation time. 
- Updating base life cycle inventory with Integrated Assessment Model data takes time. Updating the inventory once for a certain scenario/time and saving it significantly reduces computation time. 
-  Users can perform simple life cycle assessment with base life cycle inventory  (*ecoinvent 3.8*) without any prospective analysis. 
- Easier to integrate with systems/simulation models to perform LCA along with other computations frameworks.
- The updated databases (for prospective LCA) can be shared for use using other LCA software. 

### What is prospective life cycle assessment?
In prospective life cycle assessment, we update the base life cycle inventory with information from predictive models ( like Integrated Assessment Models) under future energy policies to reflect projected energy policy trajectories.
It is useful for analyzing novel technologies whose large scale deployment will only take place in the future. Several future scenarios from different IAM models are available. Please check [premise.](https://github.com/polca/premise) 
In this method, we update 4 important sectors of the economy according to several future scenarios. 
![Screenshot-2024-01-18-at-11-18-51-AM](https://github.com/NREL/LiAISON/blob/dev/images/image5.png?raw=true)Rather than getting singular LCA results, prospective LCA results are **temporal**. 
![Screenshot-2024-01-18-at-11-24-14-AM](https://github.com/NREL/LiAISON/blob/dev/images/image6.png?raw=true)Results from [paper.](https://pubs.acs.org/doi/full/10.1021/acs.est.2c04246) 

## Supplied configuration files
Three configuration yaml files are provided in the *data folder*
1. **example1.yaml**: An LCA example where we perform life cycle assessment of electricity production in the United States which is already present in the base ecoinvent 3.8 life cycle inventory. Here we do not perform prospective LCA, neither do we update the base ecoinvent using IAM model. 
2. **example2.yaml**: An LCA example where a foreground inventory for polymer electrolyte membrane electrolysis for production of 1 kg of hydrogen is built inside ecoinvent3.8. We do not perform prospective LCA,
3. **example3.yaml**: An LCA example where a foreground inventory for polymer electrolyte membrane electrolysis for production of 1 kg of hydrogen is built inside ecoinvent and then LCA is performed for the year 2040 when the world follows a [SSP2 RCP2.6 climate target scenario.](https://www.carbonbrief.org/explainer-how-shared-socioeconomic-pathways-explore-future-climate-change/) 

## Usage

## Example1: 
```
data_directories:
  ecoinvent_data: ecoinvent/ecoinvent_3.8_cutoff_ecoSpold02/datasets/
  liaisondata: inputs/
  output: output/
flags:
  correct uncertainty: false
  mc_foreground: false
  lca: true
  lca_activity_modification: false
  update_base_database_with_future_information: false
  read_base_lci_database: false
  use_base_database_for_lca: true
  regional_sensitivity: false
input_filenames:
  emission_bridge: emission_name_bridge.csv
  creation_inventory: example.csv
  foreground_inventory: example1.csv #Change this for providing the name of the foreground inventory datasets
  modification_inventory: modification_inventory.csv
  location_bridge: location_bridge.csv
  process_bridge: process_name_bridge.csv
output_filenames:
  results_filename: lcia_results
scenario_parameters:
  base_database: ecoinvent3.8
  base_project: base_project_ecoinvent38
  functional_unit: 1
  initial_year: 2020
  lca_project_name: lca_project_ecoinvent
  location: US
  mc_runs: 1
  model: image
  model_key: to_be_obtained_from_developers
  primary_process_to_study: example
  process: example
  updated_database: ecoinvent_3.8
  updated_project_name: ecoinvent_3.8

```
### Description of the configuration file

 - **data_directories**
   - ecoinvent: points to ecoinvent folder and ecoinvent version to be used for the analysis. 
   - ecoinventdata: data folder location for ecoinvent data files. 
   - liaisondata: data folder for the files for running 
   - output: folder for the output results
   
 - **flags**
     - correct uncertainty: Turn on to perform correction of uncertainty issues in the ecoinvent dataset. 
     - mc_foreground: Turn on to perform monte carlo of the foreground inventory
     - lca: Turn on to perform life cycle assessment calculations
     - lca_activity_modification: Turn on to modify an activity inside the base life cycle inventory if required. Relevant for LiASON-ReEDS
     - update_base_database_with_future_information: flag for running the database editor which edits the base ecoinvent inventory database and updates it with new information from IAM models and future climate/energy scenarios for prospective lca. Also stores the database in a project. 
     - read_base_lci_database: flag for running the database reader which reads the base ecoinvent data and stores it in a project. 
     - use_base_database_for_lca: use the base lca database (ecoinvent 3.8) for lca
     - regional_sensitivity: flag for changing regions and performing sensitivity on regions without changing the input excel file. 


 - **input_filenames**:

   - emission_bridge: emission bridge file name.
   - creation_inventory: not required for liaison. Relevant for LiASON-ReEDS
   - foreground_inventory: input data file for life cycle inventory of the process under study. 
   - modification_inventory: input data file for modification of existing datasets in ecoinvent.not required for liaison. Relevant for LiASON-ReEDS 
   - location_bridge: location bridge file name.
   - process_bridge:  process bridge file name.

 - **output_filenames:**
    - results_filename: life cycle calculation results output file. 

 - **scenario_parameters**:
   - base_database: base ecoinvent database used for study.
   -  base_project: base project name for ecoinvent.
   - initial_year: first year of analysis.
   -  lca_project_name: lca study project name.
   - location: foreground process location. 
   -  mc_runs: monte carlo run numbers.
   - model: IAM model to obtained prospective information from
   - model_key: pass code to read IAM model data within PREMISE. To be requested from developers.
   - primary_process_to_study: the primary  process under study in the datasets file. 
   - process: the process name for results file.
   - updated_database: modified database name with IAM prospective information.
   - updated_project_name: modified project name with modified database ith IAM prospective information.

#### Encryption key for running LiAISON
- An encryption key is required for running LiAISON. LiAISON requires PREMISE which requires decrypting IAM data.
- Request (by email) an encryption key from the developers.

#### Important notes for reducing run time and sharing databases. 
- Reading the base ecoinvent 3.8 into brightway2 ( LiAISON LCA Core engine) takes time. 
- Once read in, the base project can be saved and used for future LCA calculations without reading it every time. 
- LiAISON does this automatically. 
- For the **first time when LiAISON reads ecoinvent, turn on the database reader.** 
```
  read_base_lci_database: True
```
- For next runs, this can be turned off (False) and the code will run faster because it will no longer read in and save the ecoinvent 3.8 database from scratch.
- If you ran *test_run.sh*, then ecoinvent 3.8 is already read and the reader can be turned to *False* also. 

###  Editing the foreground inventory file

 - The foreground inventory information is supplied with this file.  The column names are provided in the example dataset - *example1.csv* within the */data/inputs/*
 **Columns for the foreground inventory file.**
   - process: Name of the process being created
   - flow: biosphere, techno-sphere, production flows going into the foreground process being created. 
   - unit: unit of the flows
   - value: amount of the flows
   - year: process study year
   - input: boolean for showing if a flow is an input flow (True) or an output flow(False)
   - type: type of flow: production, biosphere, technosphere. 
   - comments: as required
   - process_location : location of the foreground process under study
   - supplying_location : location of the processes supplying the technosphere flows to the process under study. The supplying location should match with the location name in ecoinvent3.8. If it does not, then the supplying process for this input flow will not be found and LiAISON will revert to RoW or GLO locations. 
![Screenshot-2024-01-18-at-12-30-16-PM](https://github.com/NREL/LiAISON/blob/dev/images/image8.png?raw=true)
- In this picture, we see an example of a foreground inventory file. 
- The name of the process under study is *example*. So we have *example* in both the rows. This process name should match the name provided in the configuration file *primary_process_under_study* parameter.
- The production flow (output flow) of this *example* process is also called *example*. Thus under the flow column, we have *example* as a flow and its boolean value for the input column is *False*
- The location of this *example* process is the US. So both of the rows show the process location as US. 
- The only technosphere flow input to this *example* process is electricity. The flow is called *electricity from US grid*. Its an input flow. So the boolean value in the input column is *True*.  The supplying location for the electricity grid flow is also the *US*. So the supplying location is *US*. The supplying location for the product flow does not matter as it is an output. Its saved as US as a placeholder. 
- Biosphere/pollutant/emission flows can be put as outflows in this file. These emissions are in-situ emissions of the *example* activity. 
- In this scenario, we created a dummy activity called *example*, said it as an output flow of *example* whose value is 1 kilowatt hour and it takes in 1 kilowatt hour of electricity as input from the US electricity grid mix. Essentially we created a dummy activity to perform LCA of the US electricity grid mix. Performing LCA without creating dummy activities is possible. Will be explained in later examples. 
![Screenshot-2024-01-18-at-12-54-38-PM](https://github.com/NREL/LiAISON/blob/dev/images/image11.png?raw=true)
### Editing the process bridge file

- The process bridge file is used for linking the names of the **technosphere/input** flows in the foreground inventory dataset to the **processes in ecoinvent** supplying the required input flow as an output product. 
- The columns in this file consist of *Common name*, *Ecoinvent name*, *Ecoinvent_code* and *type* of flow. - Common name is the one given by process, Ecoinvent name is the matched name from the ecoinvent activity, Ecoinvent code is the key code of the process from ecoinvent and the type of flow. 
- For the provided example, we had only one technosphere/input flow. *electricity from US grid*. We need to match it to the proper ecoinvent flow. That is performed in the process_bridge_file.
- Using the activity browser or ecoquery, we find the proper electricity supplying process from ecoinvent 3.8 data base. We find the the process is *market for electricity, high voltage*. We use this in the process bridge file as shown.
![Screenshot-2024-01-18-at-12-35-59-PM](https://github.com/NREL/LiAISON/blob/dev/images/image9.png?raw=true)- It is **highly recommended** to fill up the ecoinvent_code column with the actual process id from ecoinvent. However, putting it as 0 will also work in most cases and the code will search for the process at the preferred supplying location (from the foreground inventory file). 

### Editing the emissions bridge file
- The emissions bridge file is used for linking the names of the biosphere flows from the foreground inventory dataset to the emissions in the biosphere of brightway2 and ecoinvent. 
- The columns in this file consist of *Common name*, *Ecoinvent name*, *Ecoinvent code*. Common name is the one given by process, Ecoinvent name is the matched name from the ecoinvent biosphere emission, Ecoinvent code is the key code of the emission from ecoinvent biosphere.

![Screenshot-2024-01-18-at-12-47-07-PM](https://github.com/NREL/LiAISON/blob/dev/images/image10.png?raw=true)

### Running LiAISON
- Edit the run.sh file with relevant directory information
   - *DATADIR*: This is the path to the data folder of the liaison repository. 
   - *CODEDIR*: This is the path to the code directory within the LiASON root folder. 
   - *yaml*: The name of the config yaml file being used for the run. 
- **Type the following commands in the terminal**
  - `chmod +x run.sh`
  - `./run.sh`
 - the *chmod* command is just required for the first time/run. 

### Results
- After running, csv result files are written in the *data/output/* file. 
- */plotting* folder contains a visualizer.py file to create plots based on the result files in the */data/output* folder 


## Example 2:

### Configuration file: example2.yaml
- An LCA example where a foreground inventory for polymer electrolyte membrane electrolysis for production of 1 kg of hydrogen with 3 activities is built inside ecoinvent 3.8. We do not perform prospective LCA.
```
data_directories:
  ecoinvent_data: ecoinvent/ecoinvent_3.8_cutoff_ecoSpold02/datasets/
  liaisondata: inputs/
  output: output/
flags:
  correct uncertainty: false
  mc_foreground: false
  lca: true
  update_base_database_with_future_information: false
  read_base_lci_database: false
  use_base_database_for_lca: true
  regional_sensitivity: false
input_filenames:
  emission_bridge: emission_name_bridge.csv
  creation_inventory: N/A
  foreground_inventory: example2.csv
  modification_inventory: N/A
  location_bridge: location_bridge.csv
  process_bridge: process_name_bridge.csv
output_filenames:
  results_filename: lcia_results
scenario_parameters:
  base_database: ecoinvent3.8
  base_project: base_project_ecoinvent38
  functional_unit: 1
  initial_year: 2020
  lca_project_name: lca_project_ecoinvent
  location: US
  mc_runs: 1
  model: image
  model_key: #askfromdeveloper
  primary_process_to_study: PEWE electrolysis plant, operation
  process: hydrogen
  updated_database: ecoinvent3.8
  updated_project_name: ecoinvent_3.8
  ```

- *run_lci_reader*: false because we already have stored project with base ecoinvent3.8 database
- *run_prospective_lca_updater*: false we do not need prospective LCA and performing calculations in base ecoinvent 3.8
### Foreground inventory:
![Screenshot-2024-01-18-at-12-47-07-PM](https://github.com/NREL/LiAISON/blob/dev/images/foreground1.png?raw=true)
- The inventory for PEME process consists of 3 separate activities:
  - stack production
  - plant production
  - operation
- These three foreground activities needs to be connected according to the figure to produce the complete foreground system. 
- Each of these activities have their own outputs which are inputs to other foreground systems. stack --> plant --> operation
- We provided all supplying locations as US. However, if not found they will display error messages. 
- The **unit for the flows has to be the same unit** as ecoinvent. 
- Our primary process to study is *PEWE electrolysis plant, operation* because this activity produces hydrogen. We perform LCA for 1kg of hydrogen production. 

### Editing the process bridge file
- All technosphere flows should be matched with proper ecoinvent provider activities in this file. 
- Flows such as *PEWE electrolysis stack 1 MW* is both an output (production) and an input (technosphere) in the foreground inventory. As its listed as input, it has to be included in the process_bridge file. 

### Editing emissions bridge file
- The PEME process has an oxygen emission output. That is included in the emission_bridge file. 

### Running LiAISON
- Edit the run.sh file with relevant directory information
   - *DATADIR*: This is the path to the data folder of the liaison repository. 
   - *CODEDIR*: This is the path to the code directory within the LiASON root folder. 
   - *yaml*: The name of the config yaml file being used for the run. 
- **Type the following commands in the terminal**
  - `chmod +x run.sh`
  - `./run.sh`
 - the *chmod* command is just required for the first time/run. 

### Results
- After running, csv result files are written in the *data/output/* file. 
- */plotting* folder contains a visualizer.py file to create plots based on the result files in the */data/output* folder 


## Example 3:
We perform prospective LCA of hydrogen production using the PEME electrolytic method. The LCA is done for year 2040 and future energy/climate scenario is chose as SSP2 RCP26. This information is provided through the name of the project and database in the configuration yaml file for this run - example3.yaml. 

### Configuration file:
```
data_directories:
  ecoinvent_data: ecoinvent/ecoinvent_3.8_cutoff_ecoSpold02/datasets/
  liaisondata: inputs/
  output: output/
flags:
  correct uncertainty: false
  mc_foreground: false
  lca: true
  update_base_database_with_future_information: true
  read_base_lci_database: false
  use_base_database_for_lca: false
  regional_sensitivity: false
input_filenames:
  emission_bridge: emission_name_bridge.csv
  creation_inventory: N/A
  foreground_inventory: example2.csv
  modification_inventory: N/A
  location_bridge: location_bridge.csv
  process_bridge: process_name_bridge.csv
output_filenames:
  results_filename: lcia_results
scenario_parameters:
  base_database: ecoinvent3.8
  base_project: base_project_ecoinvent38
  functional_unit: 1
  initial_year: 2040
  lca_project_name: lca_project_ecoinvent
  location: US
  mc_runs: 1
  model: image
  model_key: #askfromdeveloper
  primary_process_to_study: PEWE electrolysis plant, operation
  process: hydrogen
  updated_database: ecoinvent_2040_SSP2-RCP26
  updated_project_name: ecoinvent_2040_SSP2-RCP26_image
  ```
- The updated database and updated project name **has to follow the provided format** as because year and time information is extracted out by splitting the names. 
- run_prospective_lca_updater is set to *True*.
- Run LiAISON using the run.sh file and change the yaml variable to example3. 

## Messages while running LiAISON and how to interpret them
- **Complete Success** - This message means the process and the location provided in the foreground inventory dataset was found inside the ecoinvent inventory and properly linked. 
  - Example: *Complete Success - Provided location US for market group for electricity, low voltage was found. Chosen location was US . Chosen process was market group for electricity, low voltage*
- **Minor Success** - This message means the process and the location provided in the foreground inventory dataset was found **not** inside the ecoinvent inventory
  - Rather than skipping the flow, LiAISON searches for two other locations for the requested process, **RoW**and **GLO**. 
  - If found minor success is displayed
  - Example - *Minor Success - Provided location US for low alloyed steel was not found. Shifting to market for steel, low-alloyed GLO*

- **Failed** - This means that this activity was not found at all in the ecoinvent inventory. 
  - Example: *Not found nitrogen, from air separation US b55af830951a9c677d170aea498425bf*


## Trouble shoot

### Existence of multiple processes of a given name and location
- There  might be instances where there are several processes with the same name and location inside ecoinvent. 
- If the user does not provide a code/id for the process in the process_bridge file, LiAISON will search for all these processes and after finding, will include the first one by default. However, due to list order randomization, different processes may be chosen different times resulting in random LCA results.
- To prevent this it is best to provide the code for the exact process to link to in the process_bridge file. 
- LiAISON will display the troublesome process and the options it found for that process for easier debugging. 
- Example: *Multiple processes exist for -*

### Having more than one production flow in your foreground_inventory dataset will result in error
- *Issue!!!:Production flows for an activity more than 1!!*

### Not adding technosphere flow in the process_bridge file will result in code failure with this message. Similar error message for missing emission/pollutant in the emission_bridge file
- *Did not find this process/location in the process bridge*
- *Emission match not found from Emission Bridge*

### Mismatch of units between foreground inventory and ecoinvent will results in error. 
- *UNIT ERROR*
- *Correct unit should be*
- *Unit Error occured please check*
- *Emission unit Error occured please check*

