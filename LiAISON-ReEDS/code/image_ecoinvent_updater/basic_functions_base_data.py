import pandas as pd
from wurst import *
from wurst.searching import *
from wurst.transformations.activity import change_exchanges_by_constant_factor
from wurst.transformations.uncertainty import rescale_exchange
from wurst.IMAGE.io import *
from wurst.IMAGE import *
from wurst.ecoinvent.electricity_markets import *
from wurst.ecoinvent.filters import *
from wurst.transformations.geo import *
from image_ecoinvent_updater.supplementary_data import *
import sys
import yaml
import os
import time
#import the config file
import argparse
parser = argparse.ArgumentParser(description='Execute CELAVI model')
parser.add_argument('--database', help='Name of database to be created.')
parser.add_argument('--datapath', help='Path to the input and output data folder.')
parser.add_argument('--envpath', help='Path to the environments folder.')
parser.add_argument('--lca_config_file', help='Name of config file in data folder.')
args = parser.parse_args()
tim0 = time.time()
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
    sys.exit(1)


image_variable_file = os.path.join(args.datapath,
                                  data_dirs.get('liaisondata'),
                                  data_dirs.get('image'),
                                  inputs.get('image_variable_names'))
image_data = os.path.join(args.datapath,
                                  data_dirs.get('liaisondata'),
                                  data_dirs.get('image'))

IMAGE_variables = pd.read_excel(image_variable_file)
dr = image_data


REGIONS = IMAGE_variables['Regions'].dropna().values

#Prepare for filters and name matchings

## This filter is to select out all the "Market for electricity, high voltage" activities (172) in Ecoinvent 3.6. 
electricity_market_filter_high_voltage= [contains('name', 'market for electricity, high voltage'),
                                         doesnt_contain_any('name', ['aluminium industry',
                                                                     'internal use in coal mining',
                                                                     'Swiss Federal Railways',
                                                                     'label-certified'])]

## This filter is to select out all the "Market for electricity, medium voltage" activities (172) in Ecoinvent 3.6. 
electricity_market_filter_medium_voltage= [contains('name', 'market for electricity, medium voltage'),
                                           doesnt_contain_any('name', ['aluminium industry',
                                                                       'electricity, from municipal waste incineration',
                                                                       'label-certified'])]

## This filter is to select out all the "Market for electricity, low voltage" activities (172) in Ecoinvent 3.6. 
electricity_market_filter_low_voltage= [contains('name', 'market for electricity, low voltage'),
                                        doesnt_contain_any('name', ['label-certified'])]


retained_filter = doesnt_contain_any('name', (
    'market for NOx retained',
    'market for SOx retained'
))

no_al = [exclude(contains('name', 'aluminium industry'))]
no_ccs = [exclude(contains('name', 'carbon capture and storage'))]
no_markets = [exclude(contains('name', 'market'))]
no_imports = [exclude(contains('name', 'import'))]
generic_excludes = no_al + no_ccs + no_markets


fix_names_back = {k:v for k,v in fix_names.items()}

def rename_locations(db, name_dict):
    for ds in db:
        if ds['location'] in name_dict:
            ds['location'] = name_dict[ds['location']]
        for exc in ds['exchanges']:
            print(exc)
            if exc['location'] in name_dict:
                temp = exc['location']
                exc['location'] = name_dict[exc['location']]
                print(exc['location'] + ' Location changed ' + temp)




## Extract the exchanges from the dataset
def get_exchange_amounts(ds, technosphere_filters=None, biosphere_filters=None):
    result={}
    for exc in technosphere(ds, *(technosphere_filters or [])):
        result[(exc['name'], exc['location'])]=exc['amount']
    for exc in biosphere(ds, *(biosphere_filters or [])):
        result[(exc['name'], exc['categories'])]=exc['amount']
    return result

def delete_electricity_inputs_from_market(ds):
    #This function reads through an electricity market dataset and deletes all electricity inputs that are not own consumption. 
    ds['exchanges'] = [exc for exc in get_many(ds['exchanges'], *[either(*[exclude(contains('unit', 'kilowatt hour')),
                                                                           contains('name', 'market for electricity, high voltage'),
                                                                           contains('name', 'market for electricity, medium voltage'),
                                                                           contains('name', 'market for electricity, low voltage'),
                                                                           contains('name', 'electricity voltage transformation')])])]


##  Find the all ecoinvent regions that are in the same IMAGE region of the input region. 
##  (input: one ecoinvent region, output: multiple ecoinvent regions that are in the same IMAGE region as the input region)
def find_other_ecoinvent_regions_in_image_region(loc):
    if loc== 'RoW':
        loc='GLO'
    
    if loc in fix_names:
        new_loc_name = fix_names[loc]
        image_regions = [r for r in geomatcher.intersects(new_loc_name) if r[0]=='IMAGE']
    
    else: image_regions = [r for r in geomatcher.intersects(loc) if r[0]=='IMAGE']

    temp = []
    for image_region in image_regions:
        temp.extend([r for r in geomatcher.contained(image_region)])

    result = []
    for temp in temp:
        if type(temp) ==tuple:
            result.append(temp[1])
        else: result.append(temp)
    return set(result)


##  Find the exact IMAGE region for the ecoinvent region (input: ecoinvent region, output: IMAGE region)
def ecoinvent_to_image_locations(loc):
    if loc == 'RoW':
        loc = 'GLO'
    
    if loc in fix_names.keys():
        new_loc_name = fix_names[loc]
        return [r[1] for r in geomatcher.intersects(new_loc_name) if r[0]=='IMAGE']
    
    else: return [r[1] for r in geomatcher.intersects(loc) if r[0]=='IMAGE'] 

def find_empty_columns(df):
    # This function searches through a dataframe and returns the names of all columns that are empty as a list.
    drop_list=[]
    for col in df.columns:
         if df[col].sum()==0: drop_list.append(col)
    return drop_list



def add_new_locations_to_added_datasets(db):
    # We create a new version of all added electricity generation datasets for each IMAGE region. 
    # We allow the upstream production to remain global, as we are mostly interested in regionalizing 
    # to take advantage of the regionalized IMAGE data.
    
    # step 1: make copies of all datasets for new locations
    # best would be to regionalize datasets for every location with an electricity market like this:
    # locations = {x['location'] for x in get_many(db, *electricity_market_filter_high_voltage)}  
    
    # but this takes quite a long time. For now, we just use 1 location that is uniquely in each IMAGE region.
    possibles = {}
    for reg in REGIONS[:-1]:
        temp= [x for x in geomatcher.intersects(('IMAGE', reg))if type(x) !=tuple]
        possibles[reg] = [x for x in temp if len(ecoinvent_to_image_locations(x)) ==1 ]
        if not len(possibles[reg]): print(reg, ' has no good candidate')
    locations = [v[0] for v in possibles.values()]
    
    # This code would modify every new dataset, but this would be quite large:
    # for ds in  pyprind.prog_bar([ds for ds in db if ds['database'] in ['CSP','Carma CCS']]):
    # so we consider only the final electricity production dataset and not the upstream impacts:
    for ds in pyprind.prog_bar([ds for ds in db if ds['name'] in carma_electricity_ds_name_dict.keys()]):
        for location in locations:
            new_ds = copy_to_new_location(ds, location)
            db.append(new_ds)

# This function imports the efficiency of fossil fuel power plant and returns a dataframe with the efficiency values for all years and regions for a specific technology.
def get_image_efficiencies(scenario, technology):
    
    fp = os.path.join(dr, scenario, "ElecEffAvg.out" )
    elec_eff_avg= load_image_data_file(fp)

    image_efficiency={}
    lookup_number = np.where(IMAGE_variables['Technology']==technology)[0][0]
    for year in elec_eff_avg.years:
        image_efficiency[year]={}
        for region, vector in zip(REGIONS[:], elec_eff_avg.data[:, lookup_number, list(elec_eff_avg.years).index(year)]):
            image_efficiency[year][region]=vector
    image_efficiency=pd.DataFrame.from_dict(image_efficiency,orient='index')
    image_efficiency['World']= image_efficiency.mean(axis=1)
    return image_efficiency
        
def get_image_electricity_emissions_per_input_energy(scenario, Fuel_type, sector= 'Power generation'):
    # This function imports a set of results from image for a certain scenario and returns
    # a dictionary of dataframes each with the emission values for all years and regions for one pollutant.
    # possible fuel2 choices are listed in  image_variable_names['Fuel2']
    elec_emission_factors={}

    fp = os.path.join(dr, scenario, "ENEFCH4.out")
    elec_emission_factors['CH4']= load_image_data_file(fp)

    fp = os.path.join(dr, scenario, "ENEFCO.out")
    elec_emission_factors['CO']= load_image_data_file(fp)

    fp = os.path.join(dr, scenario, "ENEFN2O.out")
    elec_emission_factors['N2O']= load_image_data_file(fp)
    
    fp = os.path.join(dr, scenario, "ENEFNOx.out")
    elec_emission_factors['NOx']= load_image_data_file(fp)

    fp = os.path.join(dr, scenario, "ENEFSO2.out")
    elec_emission_factors['SO2']= load_image_data_file(fp)
    
    fp = os.path.join(dr, scenario, "ENEFBC.out")
    elec_emission_factors['BC']= load_image_data_file(fp)

    # We currently don't have a good way to deal with the fact that ecoinvent has many different VOCs listed.
    # For the moment we just allow them to scale with the efficiency.
    
    # Note that we don't import CO2 results as these are calculated by scaling using efficiency. 
    # This is more accurate as it considers that ecoinvent is more accurate regarding the energy content of coal.

    image_emissions={}

    Fuel_type_number = np.where(IMAGE_variables['Fuel_type']==Fuel_type)[0][0]
    sector_number = np.where(IMAGE_variables['Sector']==sector)[0][0]
    
    for key, value in elec_emission_factors.items():
        image_emissions[key]={}
        for year in elec_emission_factors[key].years:
            image_emissions[key][year]={}

            for region, vector in zip(REGIONS[:-1], value.data[:, sector_number, Fuel_type_number,list(elec_emission_factors[key].years).index(year)]):
                image_emissions[key][year][region]=vector

        image_emissions[key]=pd.DataFrame.from_dict(image_emissions[key],orient='index')
        
        # Note that Image reports emissions pre unit of fuel in, so we have to make a couple of calculations
        if key == 'BC': image_emissions[key]= image_emissions[key]*1e-3 #convert to kg/MJ of input energy
        else: image_emissions[key]= image_emissions[key]*1e-6 #convert to kg/MJ of input energy
        image_emissions[key].replace({0: np.nan}, inplace=True) # we set all zero values to NaN so that the global average is calcuated only from values that exist.
        image_emissions[key]['World'] = image_emissions[key].mean(axis=1)
        image_emissions[key].fillna(0, inplace=True) #set nan values back to zero.

    return image_emissions     

    

def modify_carma_dataset_emissions(db,ds,year,scenario, emission_df):
    # The dataset passed to this function doesn't have the biosphere flows directly. 
    # Rather, it has an exchange (with unit MJ) that contains the biosphere flows per unit fuel input. 
    
    biosphere_mapping={'CH4':'Methane, fossil', 
                       'SO2':'Sulfur dioxide', 
                       'CO': 'Carbon monoxide, fossil', 
                       'NOx': 'Nitrogen oxides',
                       'N2O':'Dinitrogen monoxide'} 
    
    image_locations= ecoinvent_to_image_locations(ds['location'])
        
    exc_dataset_names = [x['name'] for x in technosphere(ds, equals('unit', 'megajoule'))]
    
    for exc_dataset in get_many(db, *[either(*[equals('name', exc_dataset_name) for exc_dataset_name in exc_dataset_names])]):
        
        if len(list(biosphere(exc_dataset)))==0: 
            modify_carma_dataset_emissions(db,exc_dataset,year,scenario, emission_df)
            continue
            
        # Modify using IMAGE emissions data
        for key, value in biosphere_mapping.items():
            for exc in biosphere(exc_dataset, contains('name', value)):          
                exc['amount'] = np.average(emission_df[key].loc[year][image_locations].values)
                if np.isnan(exc['amount']): 
                    print('Not a number! Setting exchange to zero' + ds['name'], exc['name'], ds['location'])
                    exc['amount']=0
    return

def modify_standard_carma_dataset_efficiency(ds,year,scenario, image_efficiency):
    if 'Electricity, at BIGCC power plant 450MW' in ds['name']:
        print("This function can't modify dataset: ",ds['name'], "It's got a different format.")
        return
    
    image_locations= ecoinvent_to_image_locations(ds['location'])
    image_efficiency = np.average(image_efficiency.loc[year][image_locations].values)
    
    # All other carma electricity datasets have a single exchange that is the combustion of a fuel in MJ. 
    # We can just scale this exchange and efficiency related changes will be done
    
    for exc in technosphere(ds):
        exc['amount'] = 3.6/image_efficiency
   
    return 



def modify_carma_BIGCC_efficiency(ds,year,scenario, image_efficiency):
    image_locations= ecoinvent_to_image_locations(ds['location'])
    image_efficiency = np.average(image_efficiency.loc[year][image_locations].values)
    
    old_efficiency = 3.6/get_one(technosphere(ds), *[contains('name', 'Hydrogen, from steam reforming')])['amount'] 

    for exc in technosphere(ds):
        exc['amount'] = exc['amount']*old_efficiency/image_efficiency
        return
    
    
    
def modify_all_carma_electricity_datasets(db, year, scenario, update_efficiency = True, update_emissions = True):
    # First determine which image efficiency dataset needs to be used:

    image_emissions={}
    for fuel2 in ['Coal','Natural gas','Biomass']:
        image_emissions[fuel2] = get_image_electricity_emissions_per_input_energy(scenario, fuel2, sector= 'Power generation')

    fuel_dict = {'Biomass_CCS':'Biomass',
                 'Biomass_ST':'Biomass',
                 'Coal_CCS':'Coal',
                 'Coal_ST':'Coal',
                 'IGCC':'Coal',
                 'Natural_gas_CC':'Natural gas',
                 'Natural_gas_CCS':'Natural gas'}
    
    
    for name, tech in carma_electricity_ds_name_dict.items():
        image_efficiency = get_image_efficiencies(scenario, tech)
        for ds in get_many(db, equals('name', name)):
            if update_efficiency:
                if 'Electricity, at BIGCC power plant 450MW' in ds['name']: 
                    modify_carma_BIGCC_efficiency(ds,year,scenario, image_efficiency)
                else:
                    modify_standard_carma_dataset_efficiency(ds,year,scenario, image_efficiency)
            if update_emissions:
                modify_carma_dataset_emissions(db, ds,year,scenario, image_emissions[fuel_dict[tech]])
    
    
    
    # The efficiency defined by image also includes the electricity consumed in the carbon capture process, 
    # so we have to set this exchange amount to zero:
    if update_efficiency:
        for ds in get_many(db, contains('name', 'CO2 capture')):
            for exc in technosphere(ds, *[contains('name', 'Electricity'), equals('unit', 'kilowatt hour')]):
                exc['amount'] = 0
                
                
