import numpy as np
import pyprind
import pandas as pd
import os
import pprint
import copy
import wurst as w
from matplotlib import pyplot as plt
from wurst import *
from wurst.searching import *
from wurst.transformations.activity import change_exchanges_by_constant_factor
from wurst.transformations.uncertainty import rescale_exchange
from wurst.IMAGE.io import *
from wurst.IMAGE import *
from wurst.ecoinvent.electricity_markets import *
from wurst.ecoinvent.filters import *
from wurst.transformations.geo import *
from image_ecoinvent_updater.basic_functions_base_data import *




def get_image_markets(scenario):
    # This returns a pandas dataframe containing the electricity mix for a certain year for all image locations.
    # This function is totally inefficient and should be rewritten to consider the year in question. Currently it calculates for all years and then filters out the year in question!
    fp = os.path.join(dr, scenario, "ElecProdSpec.out")
    elec_production = load_image_data_file(fp)
    # The loaded image electricity production data has three level: Region(28)-Tech(30)-Year(131)
    
    elec_prod_dfs = {}
    for i, region in enumerate(REGIONS):
        elec_prod_dfs[region] = pd.DataFrame(elec_production.data[i,:,:],columns = elec_production.years,index = IMAGE_variables['Technology'].dropna().values).T.drop('EMPTY CATEGORY!!',axis = 1)
        ## Need to think about whether to combine the centralized and decentralized Solar PV.
        # elec_prod_dfs[region]['Solar_PV'] = elec_prod_dfs[region]['Solar_PV_cen'] + elec_prod_dfs[region]['Solar_PV_decen']
        # elec_prod_dfs[region] = elec_prod_dfs[region].drop(['Solar_PV_cen', 'Solar_PV_decen'], axis=1)    
    
    year = [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]
    elec_mix_year={}
    
    for y in year:
        elec_mix_year[y] = pd.concat([pd.Series(elec_prod_dfs[region].loc[y], name = region) for region  in REGIONS[:-1]], axis = 1)
        elec_mix_year[y]['World'] = elec_mix_year[y].sum(axis = 1)
        empty_columns = find_empty_columns(elec_mix_year[y])
        elec_mix_year[y] = elec_mix_year[y].divide(elec_mix_year[y].sum(axis = 0)).sort_values(by = 'World', ascending = False).T.drop(empty_columns,axis = 1)

    return elec_mix_year

def find_average_mix(df):
    #This function considers that there might be several image regions that match the ecoinvent region. This function returns the average mix across all regions.
    #This function is useful for the Market for electricity, high voltage (RoW), because this location returns the all the image regions.
    return df.divide(df.sum().sum()).sum()

## These series of functions are trying to find the electricity production (tech) data for the electricity market data
## Function 1 -- Find the electricity production (tech) data for the specific (same) ecoinvent region
def find_ecoinvent_electricity_datasets_in_same_ecoinvent_location(tech, location, db):
    #first try ecoinvent location code:
    try: return [x for x in get_many(db, *[either(*[equals('name', name) for name in available_electricity_generating_technologies[tech]]), 
                                           equals('location', location), equals('unit', 'kilowatt hour')])]
    #otherwise try image location code (for new datasets)
    except: return [x for x in get_many(db, *[either(*[equals('name', name) for name in available_electricity_generating_technologies[tech]]), 
                                              equals('location', ecoinvent_to_image_locations(location)), equals('unit', 'kilowatt hour')])]
    

## Function 2 -- Find the electricity production (tech) data for the same IMAGE region.
def find_ecoinvent_electricity_datasets_in_image_location(tech, location, db):
       return [x for x in get_many(db, *[either(*[equals('name', name) for name in available_electricity_generating_technologies[tech]]), 
                                         either(*[equals('location', loc) for loc in find_other_ecoinvent_regions_in_image_region(location)]),
                                         equals('unit', 'kilowatt hour')])]
   
    
## Function 3 -- Find the electricity production (tech) data as long as they are available (no location restricted)
def find_ecoinvent_electricity_datasets_in_all_locations(tech, db):
       return [x for x in get_many(db, *[either(*[equals('name', name) for name in available_electricity_generating_technologies[tech]]),
                                         equals('unit', 'kilowatt hour')])]    
    


def update_electricity_markets(db, year, scenario):
    
    #import the image electricity production, and calculate the electricity mix by %:
    image_electricity_market_df = get_image_markets(scenario)[year]
    #Remove all electricity producers from markets:
    db = empty_low_voltage_markets(db)
    db = empty_medium_voltage_markets(db)
    db = empty_high_voltage_markets(db) # This function isn't working as expected - it needs to delete imports as well.
    changes={}
    #update high voltage markets:
    for ds in get_many(db, *electricity_market_filter_high_voltage):
        changes[ds['code']]={}
        changes[ds['code']].update( {('meta data', x) : ds[x] for x in ['name','location']})
        changes[ds['code']].update( {('original exchanges', k) :v for k,v in get_exchange_amounts(ds).items()})
        delete_electricity_inputs_from_market(ds) # This function will delete the markets. Once Wurst is updated this can be deleted.
        add_new_datasets_to_electricity_market(ds, db, image_electricity_market_df)

        changes[ds['code']].update( {('updated exchanges', k) :v for k,v in get_exchange_amounts(ds).items()})
    print('Updated electricity market')
    return changes




def add_new_datasets_to_electricity_market(ds, db, df):
    #This function adds new electricity datasets to a market based on image results. We pass not only a dataset to modify, but also a pandas dataframe containing the new electricity mix information, and the db from which we should find the datasets
    # find out which image regions correspond to our dataset:

    image_locations= ecoinvent_to_image_locations(ds['location'])

    # here we find the mix of technologies in the new market and how much they contribute:
    mix =  find_average_mix(df.loc[image_locations]) #could be several image locations - we just take the average

    # here we find the datasets that will make up the mix for each technology
    datasets={}
    for i in mix.index:
        if mix[i] !=0:
            #print('Next Technology: ',i) 
            # First try to find a dataset that is from same location (or image region for new datasets):   
            datasets[i] = find_ecoinvent_electricity_datasets_in_same_ecoinvent_location(i, ds['location'], db)
            #print('First round: ',i, [(ds['name'], ds['location']) for ds in datasets[i]])
            
            #If this doesn't work, we try to take a dataset from another ecoinvent region within the same image region                                    
            if len(datasets[i]) == 0: 
                datasets[i] = find_ecoinvent_electricity_datasets_in_image_location(i, ds['location'], db)
                #print('Second round: ',i, [(ds['name'], ds['location']) for ds in datasets[i]])
            
            # If even this doesn't work, try taking a global datasets 
            if len(datasets[i]) == 0:  
                datasets[i] = find_ecoinvent_electricity_datasets_in_same_ecoinvent_location(i, 'GLO', db)
                #print('Third round: ',i, [(ds['name'], ds['location']) for ds in datasets[i]])
                    
            #if no global dataset available, we just take the average of all datasets we have:
            if len(datasets[i]) ==0:  
                datasets[i] = find_ecoinvent_electricity_datasets_in_all_locations(i, db)
                #print('Fourth round: ',i, [(ds['name'], ds['location']) for ds in datasets[i]])
                
            #If we still can't find a dataset, we just take the global market group
            if len(datasets[i]) ==0:
                print('No match found for location: ', ds['location'], ' Technology: ', i,'. Taking global market group for electricity')
                datasets[i] = [x for x in get_many(db, *[equals('name', 'market group for electricity, high voltage'), equals('location', 'GLO')])]
                                            
                            
    # Now we add the new exchanges:
    for i in mix.index:
        if mix[i] !=0:
            total_amount = mix[i]
            amount= total_amount / len(datasets[i])
            for dataset in datasets[i]:
                ds['exchanges'].append({
                'amount': amount,
                'unit': dataset['unit'],    
                'input': (dataset['database'], dataset['code']),
                'type': 'technosphere',
                'name': dataset['name'],
                'location': dataset['location']                           
                    })
    
    #confirm that exchanges sum to 1!
    sum = np.sum([exc['amount'] for exc in technosphere(ds, *[equals('unit', 'kilowatt hour'), doesnt_contain_any('name', ['market for electricity, high voltage'])])])
    if round(sum,4) != 1.00:  print(ds['location'], " New exchanges don't add to one! something is wrong!", sum )
    return