# LiAISON: Life Cycle Analysis Integration into Scalable Open-source Numerical Models

[![DOI](https://img.shields.io/badge/DOI-10.1021%2Facs.est.2c04246-blue)](https://pubs.acs.org/doi/full/10.1021/acs.est.2c04246)

LiAISON is a Python framework for performing automated, scalable life cycle assessment (LCA) with support for prospective analysis using integrated assessment model (IAM) scenarios.

## Key Features

- **Automated LCA Calculations**: Automatically link foreground inventory processes to background ecoinvent database
- **Prospective LCA**: Integrate future scenarios from IAM models (IMAGE, GCAM) via [premise](https://github.com/polca/premise)
- **Regional Analysis**: Perform location-specific LCA calculations with automatic fallback to alternative geographies
- **Monte Carlo Analysis**: Uncertainty quantification for foreground inventory
- **Batch Processing**: Execute multiple LCA scenarios programmatically for optimization and systems modeling
- **Flexible Configuration**: YAML-based configuration for easy scenario management

## Methodology

![LiAISON Framework](https://github.com/NREL/LiAISON/blob/main/images/image2.png?raw=true)

The LiAISON framework consists of three modular components:

1. **Life Cycle Inventory Reader**: Imports and stores the base ecoinvent database in Brightway2
2. **Prospective LCA Updater**: Modifies the base database with future scenarios from IAM models using premise
3. **Automated LCA Calculator**: Links user-defined foreground processes to background inventory and performs LCIA

This modular design enables:
- One-time database import with reusable projects
- Separation of database updates from LCA calculations
- Integration with systems models and optimization frameworks

### Prospective Life Cycle Assessment

![Prospective LCA](https://github.com/NREL/LiAISON/blob/main/images/image4.png?raw=true)

Prospective LCA updates the background database with future projections of:
- Electricity generation mixes
- Transportation technologies
- Industrial processes
- Material production

Multiple IAM models and Shared Socioeconomic Pathways (SSPs) are supported through premise.

## Requirements

### System Requirements
- **Operating System**: Linux, macOS, or Windows with Anaconda
- **Python**: 3.10 or 3.11
- **RAM**: Minimum 8 GB (16 GB recommended for large analyses)

### Data Requirements
- **ecoinvent license**: [ecoinvent 3.8](https://www.ecoinvent.org/) database (cutoff allocation)
- **IAM Access Key** (for prospective LCA): Contact developers for premise decryption key

### Software Dependencies
The environment includes:
- `brightway2==2.4.7` - LCA calculation engine
- `bw2data==3.6.6` - Brightway2 data management
- `bw2calc==1.8.2` - Brightway2 calculation module
- `bw2io==0.8.7` - Brightway2 input/output (required for ecoinvent 3.8)
- `premise==2.3.0.dev1` - Prospective database scenarios
- `premise-gwp==0.9.7` - GWP methods for premise

## Installation

### Step 1: Install Anaconda/Miniconda

Download and install [Anaconda](https://www.anaconda.com/products/individual) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for your operating system.

### Step 2: Clone the Repository

```bash
git clone https://github.com/NREL/LiAISON.git
cd LiAISON
```

### Step 3: Create the Environment

```bash
# Create environment from file
conda env create -f environment.yml -n liaison

# Activate the environment
conda activate liaison
```

### Step 4: Verify Installation

```bash
# Check brightway2 installation
python -c "import brightway2 as bw; print(f'Brightway2 version: {bw.__version__}')"

# Check premise installation
python -c "import premise; print(f'Premise installed successfully')"
```

### Important Notes on Dependencies

**Ecoinvent 3.8 Compatibility**: The environment includes `bw2data==3.6.6`, `bw2calc==1.8.2`, and `bw2io==0.8.7` which are specifically required for ecoinvent 3.8. These versions are automatically installed via the environment file.

**For Other ecoinvent Versions**: If you plan to use ecoinvent versions newer than 3.8, you will need:
```bash
pip install --upgrade bw2io  # Install latest version (>0.8.8)
```

### Step 5: Prepare ecoinvent Database

1. Download **ecoinvent 3.8 cutoff allocation, ecoSpold02** from the [ecoinvent website](https://ecoinvent.org/)
   - File: `ecoinvent 3.8_cutoff_ecoSpold02.7z` (~61 MB)

2. Extract the database:
   ```bash
   # Extract to the data/inputs/ecoinvent directory
   7z x "ecoinvent 3.8_cutoff_ecoSpold02.7z" -o"data/inputs/ecoinvent/"
   ```

3. Rename the extracted folder:
   ```bash
   # Ensure underscore between 'ecoinvent' and '3.8'
   mv "data/inputs/ecoinvent/ecoinvent 3.8_cutoff_ecoSpold02" \
      "data/inputs/ecoinvent/ecoinvent_3.8_cutoff_ecoSpold02"
   ```

**Directory Structure**:
```
LiAISON/
├── data/
│   ├── inputs/
│   │   ├── ecoinvent/
│   │   │   └── ecoinvent_3.8_cutoff_ecoSpold02/
│   │   │       └── datasets/
│   │   ├── example1.csv
│   │   ├── example2.csv
│   │   ├── emission_name_bridge.csv
│   │   ├── process_name_bridge.csv
│   │   └── location_bridge.csv
│   └── output/
├── environment.yml
├── run.sh
└── __main__.py
```

## Quick Start

### Test Run

Execute a complete test run to verify installation:

```bash
# Make the script executable
chmod +x run.sh

# Run with test configuration
./run.sh
```

This will:
1. Read the ecoinvent 3.8 database (first time only, ~10-15 minutes)
2. Create a simple foreground inventory
3. Perform LCA with TRACI and ReCiPe methods
4. Generate results in `data/output/`

### Running Custom Analyses

Edit the `run.sh` script to specify your configuration file:

```bash
#!/usr/bin/env bash
PATH_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
DATADIR=$PATH_DIR"/data"
yaml="example1"  # Change to your YAML file name (without .yaml extension)

python __main__.py --datapath=$DATADIR --lca_config_file=$DATADIR/$yaml.yaml
```

Then execute:
```bash
./run.sh
```

## Configuration

LiAISON uses YAML files for configuration. Three example configurations are provided:

### Example 1: Basic LCA (example1.yaml)
Performs LCA on an existing ecoinvent process (US electricity grid).

**Key Settings**:
- `read_base_lci_database: true` (first run only)
- `update_base_database_with_future_information: false`
- `use_base_database_for_lca: true`
- No foreground inventory creation

### Example 2: Foreground Inventory Creation (example2.yaml)
Creates a complex foreground system for hydrogen production via polymer electrolyte water electrolysis (PEWE).

**Key Settings**:
- Creates 3 linked activities (stack → plant → operation)
- `foreground_inventory: example2.csv`
- Links to ecoinvent background processes

### Example 3: Prospective LCA (example3.yaml)
Performs future-oriented LCA for hydrogen production in 2040 under SSP2-RCP26 scenario.

**Key Settings**:
- `update_base_database_with_future_information: true`
- `updated_database: ecoinvent_2040_SSP2-RCP26`
- `model: image` (or `gcam`)
- Requires `model_key` for premise access

## Configuration Reference

### Complete YAML Structure

```yaml
data_directories:
  ecoinvent_data: ecoinvent/ecoinvent_3.8_cutoff_ecoSpold02/datasets/
  liaisondata: inputs/
  output: output/

flags:
  correct_uncertainty: false          # Apply uncertainty corrections
  mc_foreground: false                # Monte Carlo on foreground
  lca: true                           # Perform LCA calculation
  lca_activity_modification: false   # Edit ecoinvent activities
  update_base_database_with_future_information: false  # Run prospective updater
  read_base_lci_database: true       # Import ecoinvent (first time only)
  use_base_database_for_lca: true    # Use base ecoinvent (vs updated)
  regional_sensitivity: false         # Regional analysis

input_filenames:
  emission_bridge: emission_name_bridge.csv
  creation_inventory: N/A
  foreground_inventory: example1.csv
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
  unit: kilowatt hour
  mc_runs: 1
  model: image                       # IAM model: 'image' or 'gcam'
  model_key: your_key_here          # Request from developers
  primary_process_to_study: example  # Main process for LCA
  process: example                   # Process name for results
  updated_database: ecoinvent3.8
  updated_project_name: ecoinvent_3.8
```

### Configuration Parameters Explained

#### Flags

| Flag | Description | When to Use |
|------|-------------|-------------|
| `read_base_lci_database` | Import ecoinvent into Brightway2 | **true** only on first run; **false** afterwards |
| `update_base_database_with_future_information` | Run premise updater | **true** for prospective LCA |
| `use_base_database_for_lca` | Use base ecoinvent (not updated) | **true** for static LCA; **false** for prospective |
| `lca` | Perform LCIA calculation | **true** to calculate impacts |
| `mc_foreground` | Monte Carlo on foreground | **true** for uncertainty analysis |
| `regional_sensitivity` | Regional analysis | **true** to test location sensitivity |

#### Scenario Parameters

| Parameter | Description | Notes |
|-----------|-------------|-------|
| `base_database` | Ecoinvent version | Use `ecoinvent3.8` |
| `base_project` | Project name for base DB | Auto-created on first run |
| `updated_database` | Name for updated DB | Format: `ecoinvent_YYYY_SCENARIO` |
| `updated_project_name` | Project for updated DB | Format: `ecoinvent_YYYY_SCENARIO_model` |
| `model` | IAM model | `image` or `gcam` |
| `model_key` | Premise decryption key | Contact developers |
| `location` | Process location | ISO country codes or ecoinvent locations |
| `unit` | Functional unit | Must match ecoinvent units |
| `functional_unit` | FU quantity | Typically 1 |

**Important**: For prospective LCA, the naming convention is critical:
- `updated_database`: `ecoinvent_[YEAR]_[SCENARIO]`
- `updated_project_name`: `ecoinvent_[YEAR]_[SCENARIO]_[model]`

Example:
```yaml
updated_database: ecoinvent_2040_SSP2-RCP26
updated_project_name: ecoinvent_2040_SSP2-RCP26_image
```

## Creating Foreground Inventories

### Foreground Inventory CSV Format

Create a CSV file with the following columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| `process` | Name of your process | Yes | `PEWE electrolysis stack production` |
| `flow` | Input/output flow name | Yes | `Titanium` |
| `value` | Flow amount | Yes | `0.000201` |
| `unit` | Flow unit | Yes | `kilogram` |
| `input` | TRUE for inputs, FALSE for outputs | Yes | `TRUE` |
| `year` | Year of analysis | Yes | `2020` |
| `comments` | Notes/documentation | No | `none` |
| `type` | `production`, `technosphere`, or `biosphere` | Yes | `technosphere` |
| `process_location` | Where your process occurs | Yes | `US` |
| `supplying_location` | Where inputs come from | Yes | `US` |

### Example: Simple Process

```csv
process,flow,value,unit,input,year,comments,type,process_location,supplying_location
my_process,my_product,1,kilogram,FALSE,2020,none,production,US,US
my_process,electricity,50,kilowatt hour,TRUE,2020,none,technosphere,US,US
```

### Multi-Activity Inventories

For complex systems with multiple linked activities (see `example2.csv`):

1. **Define all production flows** (one per activity)
2. **Link activities** by using production flows as technosphere inputs
3. **Specify location** for each process and input source
4. **Include biosphere flows** (emissions) as needed

Example structure:
```csv
# Activity 1: Component Production
component_production,component,1,unit,FALSE,2020,none,production,US,US
component_production,steel,10,kilogram,TRUE,2020,none,technosphere,US,US

# Activity 2: Plant Construction (uses component)
plant_construction,plant,1,unit,FALSE,2020,none,production,US,US
plant_construction,component,0.5,unit,TRUE,2020,none,technosphere,US,US

# Activity 3: Operation (uses plant)
operation,hydrogen,1,kilogram,FALSE,2020,none,production,US,US
operation,plant,3.18E-07,unit,TRUE,2020,none,technosphere,US,US
operation,electricity,55,kilowatt hour,TRUE,2020,none,technosphere,US,US
```

## Bridge Files

Bridge files map your custom names to ecoinvent nomenclature.

### Process Bridge (process_name_bridge.csv)

Maps foreground technosphere flows to ecoinvent activities:

```csv
Common_name,Ecoinvent_name,Ecoinvent_code
electricity,market group for electricity, high voltage,abc123...
steel,market for steel, low-alloyed,def456...
```

**Best Practice**: Always include the `Ecoinvent_code` (activity UUID) to ensure exact matches. Find codes using:
- [Activity Browser](https://github.com/LCA-ActivityBrowser/activity-browser)
- [ecoQuery](https://www.ecoquery.ecoinvent.org/)
- Brightway2: `activity['code']`

### Emission Bridge (emission_name_bridge.csv)

Maps biosphere flows to ecoinvent elementary flows:

```csv
Common_name,Ecoinvent_name,Ecoinvent_code
CO2,Carbon dioxide, fossil,ghi789...
NOx,Nitrogen oxides,jkl012...
```

### Location Bridge (location_bridge.csv)

Maps location names (typically not needed if using standard ISO codes):

```csv
location_common,location_ecoinvent
United States,US
California,US-WECC
```

## Running LiAISON

### Command Line Execution

```bash
python __main__.py \
  --datapath=/path/to/data \
  --envpath=/path/to/brightway_env \
  --lca_config_file=/path/to/data/config.yaml
```

**Parameters**:
- `--datapath`: Directory containing input/output folders
- `--envpath`: (Optional) Custom Brightway2 data directory
- `--lca_config_file`: Path to YAML configuration file

### Using run.sh Script

The provided script simplifies execution:

```bash
#!/usr/bin/env bash
PATH_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
DATADIR=$PATH_DIR"/data"
yaml="your_config"  # Without .yaml extension

python __main__.py --datapath=$DATADIR --lca_config_file=$DATADIR/$yaml.yaml
```

### Execution Workflow

1. **First Time Setup** (~10-15 minutes):
   - Set `read_base_lci_database: true`
   - Imports ecoinvent 3.8 into Brightway2
   - Creates base project

2. **Subsequent Runs** (seconds to minutes):
   - Set `read_base_lci_database: false`
   - Uses stored base project
   - Performs LCA calculations

3. **Prospective LCA** (15-45 minutes per scenario):
   - Set `update_base_database_with_future_information: true`
   - Downloads IAM data via premise
   - Updates database for future year/scenario
   - Stores updated project for reuse

## Understanding LiAISON Messages

LiAISON provides informative console messages during execution:

### Success Messages

**Complete Success**
```
Complete Success - Provided location US for market group for electricity, low voltage was found.
Chosen location was US. Chosen process was market group for electricity, low voltage
```
→ Exact match found at requested location

**Minor Success**
```
Minor Success - Provided location US for low alloyed steel was not found.
Shifting to market for steel, low-alloyed GLO
```
→ Process found at alternative location (RoW, GLO, RER, etc.)

### Warning Messages

**Activity Not Found**
```
Failed - Not found nitrogen, from air separation US b55af830...
```
→ Activity doesn't exist in ecoinvent; check spelling or add to bridge file

**Multiple Activities**
```
INFO: Process dictionary length when [process]@[location]@[unit] is chosen is 3
INFO Multiple activities found ---- [activity1] [code1]
INFO Multiple activities found ---- [activity2] [code2]
```
→ Multiple matches; first is chosen by default. Specify `Ecoinvent_code` in bridge file to select exact match.

**Unit Mismatch**
```
Warning --- UNIT ERROR US for market group for electricity
Warning --- Correct unit should be kilowatt hour
```
→ Your unit doesn't match ecoinvent. Update foreground inventory.

### Location Fallback Hierarchy

When an activity isn't found at the specified location, LiAISON searches in order:
1. Requested location (e.g., `US`)
2. North America (`USA`, `RNA`)
3. Rest of World (`RoW`)
4. Global (`GLO`)
5. Europe (`RER`)

## Results and Outputs

### Output Files

Results are saved in `data/output/`:

**LCIA Results** (`lcia_results_[database]_[process].csv`):
```csv
lcia,value,unit,year,method
Global Warming,100.5,kg CO2 eq,ecoinvent_2020_SSP2-Base,TRACI2.1
Acidification,0.25,kg SO2 eq,ecoinvent_2020_SSP2-Base,TRACI2.1
...
```

**Electricity Mix** (`[database]_electricity_mix.csv`):
- Breakdown of electricity generation sources
- Useful for understanding background electricity impacts

### LCIA Methods Included

LiAISON calculates impacts using multiple methods:

**TRACI 2.1** (9 categories):
- Global warming
- Acidification
- Eutrophication
- Ecotoxicity
- Human health - Carcinogenic
- Human health - Non-carcinogenic
- Ozone depletion
- Photochemical oxidation
- Respiratory effects

**ReCiPe Midpoint (H)** (18 categories):
- Climate change
- Ozone depletion
- Human toxicity
- Particulate matter formation
- Ionising radiation
- Photochemical oxidant formation
- Terrestrial acidification
- Freshwater eutrophication
- Marine eutrophication
- Terrestrial ecotoxicity
- Freshwater ecotoxicity
- Marine ecotoxicity
- Agricultural land occupation
- Urban land occupation
- Natural land transformation
- Water depletion
- Mineral resource depletion
- Fossil resource depletion

**IPCC 2013** (via premise, for prospective LCA):
- GWP 100a (various accounting methods)

## Advanced Features

### Monte Carlo Uncertainty Analysis

Enable uncertainty propagation on foreground inventory:

```yaml
flags:
  mc_foreground: true
  
scenario_parameters:
  mc_runs: 1000  # Number of Monte Carlo iterations
```

**Note**: This applies uncertainty only to foreground processes. Background ecoinvent uncertainties are always included in stochastic calculations.

### Regional Sensitivity Analysis

Test how location affects results without modifying CSV:

```yaml
flags:
  regional_sensitivity: true
  
scenario_parameters:
  location: CA  # Override all locations to California
```

### Activity Modification

Edit existing ecoinvent activities directly (advanced):

```yaml
flags:
  lca_activity_modification: true
```

This extracts an ecoinvent activity, allows modification, and uses the modified version for LCA.

### Prospective Database Naming

For prospective LCA, follow the naming convention:

**SSP Scenarios**:
```yaml
# Format: ecoinvent_[YEAR]_[SSP]-[RCP]
updated_database: ecoinvent_2030_SSP2-Base
updated_database: ecoinvent_2050_SSP1-RCP19
updated_database: ecoinvent_2040_SSP2-RCP26
```

**Available Scenarios** (depends on IAM model):
- SSP1-RCP19 (Sustainability, 1.5°C pathway)
- SSP2-Base (Middle of the road, baseline)
- SSP2-RCP26 (Middle of the road, 2°C pathway)
- SSP2-RCP45 (Middle of the road, moderate mitigation)
- SSP5-Base (Fossil-fueled development, baseline)

## Troubleshooting

### Common Issues

**Issue**: `Could not open [config.yaml] for configuration`
- **Solution**: Check that YAML file exists and path is correct in `run.sh`

**Issue**: `No module named 'brightway2'`
- **Solution**: Activate the conda environment: `conda activate liaison`

**Issue**: `KeyError: 'ecoinvent3.8'`
- **Solution**: Run with `read_base_lci_database: true` to import ecoinvent first

**Issue**: `Process not found in ecoinvent`
- **Solution**: 
  1. Check spelling in bridge files
  2. Verify process exists in ecoinvent 3.8
  3. Try providing `Ecoinvent_code` in bridge file
  4. Check alternative locations (GLO, RoW)

**Issue**: Premise fails with authentication error
- **Solution**: Request valid `model_key` from developers (email address below)

**Issue**: Unit mismatch errors
- **Solution**: Check ecoinvent documentation for correct units. Common mismatches:
  - `kWh` vs `kilowatt hour`
  - `kg` vs `kilogram`
  - `m3` vs `cubic meter`

### Performance Optimization

**Speed up repeated runs**:
1. Import ecoinvent once (`read_base_lci_database: true`), then set to `false`
2. For prospective LCA, create updated databases once, then reuse
3. Use `use_base_database_for_lca: true` when prospective update not needed

**Reduce memory usage**:
- Process results in batches if running many scenarios
- Clear output directory between large runs
- Close other applications during premise updates

### Getting Help

**Check LiAISON messages**: The console output provides detailed information about:
- Which activities were found/not found
- Location substitutions made
- Unit mismatches
- Database search progress

**Enable detailed logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Project Structure

```
LiAISON/
├── __main__.py                    # Main entry point
├── liaison_model.py               # LCA workflow orchestration
├── lci_calculator.py              # LCI calculations and LCIA methods
├── search_activity_ecoinvent.py   # Activity search functions
├── edit_activity_ecoinvent.py     # Activity editing functions
├── ecoinvent_explorer.py          # Database exploration utilities
├── main_database_reader.py        # Ecoinvent import
├── main_database_editor.py        # Premise integration
├── environment.yml                # Conda environment specification
├── run.sh                         # Execution script
├── data/
│   ├── inputs/
│   │   ├── ecoinvent/             # Ecoinvent database (user-provided)
│   │   ├── example1.csv           # Simple foreground inventory
│   │   ├── example2.csv           # Complex foreground inventory (PEWE)
│   │   ├── example1.yaml          # Basic LCA configuration
│   │   ├── example2.yaml          # Foreground creation configuration
│   │   ├── example3.yaml          # Prospective LCA configuration
│   │   ├── process_name_bridge.csv
│   │   ├── emission_name_bridge.csv
│   │   └── location_bridge.csv
│   └── output/                    # Results directory
└── README.md
```

## Integration with Other Models

LiAISON is designed to integrate with:

- **Systems models**: ReEDS, GCAM, etc.
- **Optimization frameworks**: Pyomo, CPLEX, etc.
- **Decision support tools**: Multi-criteria analysis, techno-economic assessment

### Example Integration Pattern

```python
import yaml
import subprocess

# Run LCA for optimization iteration
def run_lca_iteration(technology_mix, output_dir):
    # Update foreground inventory with optimization results
    create_inventory_csv(technology_mix, "temp_inventory.csv")
    
    # Update YAML configuration
    config = load_config("base_config.yaml")
    config['input_filenames']['foreground_inventory'] = "temp_inventory.csv"
    config['data_directories']['output'] = output_dir
    
    with open("temp_config.yaml", "w") as f:
        yaml.dump(config, f)
    
    # Execute LiAISON
    subprocess.run(["python", "__main__.py", 
                   "--datapath=data",
                   "--lca_config_file=temp_config.yaml"])
    
    # Parse results
    return parse_lcia_results(output_dir)
```

## Citation

If you use LiAISON in your research, please cite:

```bibtex
@article{liaison2023,
  title={LiAISON: Life Cycle Analysis Integration into Scalable Open-source Numerical Models},
  author={Ghosh, Tapajyoti and Lamers, Patrick and Chun, Soomin and others},
  journal={Environmental Science & Technology},
  year={2023},
  doi={10.1021/acs.est.2c04246}
}
```

## Contributors

- **Tapajyoti Ghosh** - Lead Developer (tghosh@nrel.gov)
- **Patrick Lamers** - Principal Investigator (plamers@nrel.gov)
- **Soomin Chun** - Contributor (schun@nrel.gov)
- **Shubhankar Upasani** - Contributor
- **Alberta Carpenter** - Contributor
- **Romain Sacchi** - Premise Integration (romain.sacchi@psi.ch)

## Support and Contact

- **Email**: tghosh@nrel.gov
- **Issues**: [GitHub Issues](https://github.com/NREL/LiAISON/issues)
- **Discussions**: [GitHub Discussions](https://github.com/NREL/LiAISON/discussions)

For premise-related questions or to request a model encryption key, contact the developers via email.

## License

[Include license information]

## Acknowledgments

This work was supported by the U.S. Department of Energy's Office of Energy Efficiency and Renewable Energy (EERE).


---

**Note**: This is research software under active development. While we strive for accuracy and reliability, please validate results for your specific use case and report any issues on GitHub.