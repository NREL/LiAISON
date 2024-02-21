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
import sys




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
    
    
    
    

def find_ecoinvent_coal_efficiency(ds):
    # Nearly all coal power plant datasets have the efficiency as a parameter. 
    # If this isn't available, we back calculate it using the amount of coal used and 
    # an average energy content of coal.
    try: 
        return ds['parameters']['efficiency']
    except KeyError:
        pass
    
    #print('Efficiency parameter not found - calculating generic coal efficiency factor', ds['name'], ds['location'])
    
    fuel_sources = technosphere(ds, 
                                either(contains('name', 'hard coal'), contains('name', 'lignite')), 
                                doesnt_contain_any('name', ('ash','SOx')),
                                equals('unit', 'kilogram'))
    energy_in = 0 
    for exc in fuel_sources:
        if 'hard coal' in exc['name']: 
            energy_density = 20.1 / 3.6 #kWh/kg
        elif 'lignite' in exc['name']: 
            energy_density = 9.9 / 3.6 # kWh/kg
        else:
            raise ValueError("Shouldn't happen because of filters!!!")
        energy_in += (exc['amount'] * energy_density)
    ds['parameters']['efficiency'] = reference_product(ds)['amount'] / energy_in
    #print(ds['parameters']['efficiency'])
    return reference_product(ds)['amount'] / energy_in

def find_ecoinvent_gas_efficiency(ds):

    # Nearly all gas power plant datasets have the efficiency as a parameter. 
    # If this isn't available, we back calculate it using the amount of gas used and an average energy content of gas.
    try: 
        return ds['parameters']['efficiency']
    except KeyError:
        pass
    
    fuel_sources = technosphere(ds,
                                either(contains('name', 'natural gas, low pressure'), contains('name', 'natural gas, high pressure')), 
                                equals('unit', 'cubic meter'))
    energy_in = 0 
    for exc in fuel_sources:
        # (based on energy density of natural gas input for global dataset 
        # 'electricity production, natural gas, conventional power plant')
        #print(exc['name'] + ' ' + str(exc['amount']))
        if 'natural gas, high pressure' in exc['name']: 
            energy_density= 39 / 3.6 # kWh/m3 
        
        # (based on average energy density of high pressure gas, scaled by the mass difference listed between 
        # high pressure and low pressure gas in the dataset: 
        # natural gas pressure reduction from high to low pressure, RoW)
        elif 'natural gas, low pressure' in exc['name']: 
            energy_density= 39 * 0.84 / 3.6 #kWh/m3 
            
        else:
            raise ValueError("Shouldn't happen because of filters!!!")
        energy_in += (exc['amount'] * energy_density)

    ds['parameters']['efficiency'] = reference_product(ds)['amount'] / energy_in
    return ds['parameters']['efficiency']




def find_ecoinvent_oil_efficiency(ds):
    
    # Nearly all oil power plant datasets have the efficiency as a parameter. 
    # If this isn't available, we use global average values to calculate it.
    try: return ds['parameters']['efficiency_oil_country']
    except KeyError:
        pass
    #print('Efficiency parameter not found - calculating generic oil efficiency factor', ds['name'], ds['location'])
    fuel_sources=[x for x in technosphere(ds, *[contains('name', 'heavy fuel oil'), 
                                    equals('unit', 'kilogram')]
                                    )]
    energy_in=0 
    for exc in fuel_sources:
        # (based on energy density of heavy oil input and efficiency parameter for dataset 
        # 'electricity production, oil, RoW')
        energy_density= 38.5 / 3.6 # kWh/m3 
        energy_in += (exc['amount'] * energy_density)
    ds['parameters']['efficiency'] = reference_product(ds)['amount'] / energy_in
    return reference_product(ds)['amount'] /energy_in


def find_ecoinvent_biomass_efficiency(ds):
    # Nearly all power plant datasets have the efficiency as a parameter. If this isn't available, we excl.
    try: return ds['parameters']['efficiency_electrical']
    except: pass
    
    if ds['name'] == 'heat and power co-generation, biogas, gas engine, label-certified': 
        ds['parameters'] = {'efficiency_electrical': 0.32}
        return ds['parameters']['efficiency_electrical']#in general comments for dataset
    
    elif ds['name'] == 'wood pellets, burned in stirling heat and power co-generation unit, 3kW electrical, future': 
        ds['parameters'] = {'efficiency_electrical': 0.23}
        return ds['parameters']['efficiency_electrical'] #in comments for dataset  
    
    print(ds['name'], ds['location'],' Efficiency not found!')
    return 0


def find_coal_efficiency_scaling_factor(ds, year, image_efficiency, agg_func=np.average):
    # Input a coal electricity dataset and year. We look up the efficiency for this region and year 
    # from the Image model and return the scaling factor by which to multiply all efficiency dependent exchanges.
    # If the ecoinvent region corresponds to multiple Image regions we simply average them.
    ecoinvent_eff = find_ecoinvent_coal_efficiency(ds)
    image_locations= ecoinvent_to_image_locations(ds['location'])
    image_eff = agg_func(image_efficiency.loc[year][image_locations].values) # we take an average of all applicable image locations
    return ecoinvent_eff / image_eff


def find_gas_efficiency_scaling_factor(ds, year, image_efficiency, agg_func=np.average):
    # Input a gas electricity dataset and year. We look up the efficiency for this region and year 
    # from the Image model and return the scaling factor by which to multiply all efficiency dependent exchanges.
    # If the ecoinvent region corresponds to multiple Image regions we simply average them.
    ecoinvent_eff = find_ecoinvent_gas_efficiency(ds)
    image_locations= ecoinvent_to_image_locations(ds['location'])
    image_eff = agg_func(image_efficiency.loc[year][image_locations].values) # we take an average of all applicable image locations
    return ecoinvent_eff / image_eff



def find_oil_efficiency_scaling_factor(ds, year, image_efficiency, agg_func=np.average):
    # Input a oil electricity dataset and year. We look up the efficiency for this region and year 
    # from the Image model and return the scaling factor by which to multiply all efficiency dependent exchanges.
    # If the ecoinvent region corresponds to multiple Image regions we simply average them.
    ecoinvent_eff = find_ecoinvent_oil_efficiency(ds)
    image_locations= ecoinvent_to_image_locations(ds['location'])
    image_eff = agg_func(image_efficiency.loc[year][image_locations].values) # we take an average of all applicable image locations
    return ecoinvent_eff / image_eff


def find_biomass_efficiency_scaling_factor(ds, year, image_efficiency, agg_func=np.average):
    # Input an electricity dataset and year. We look up the efficiency for this region and year 
    # from the Image model and return the scaling factor by which to multiply all efficiency dependent exchanges.
    # If the ecoinvent region corresponds to multiple Image regions we simply average them.
    ecoinvent_eff = find_ecoinvent_biomass_efficiency(ds)
    image_locations= ecoinvent_to_image_locations(ds['location'])
    image_eff = agg_func(image_efficiency.loc[year][image_locations].values) # we take an average of all applicable image locations
    return ecoinvent_eff / image_eff



def find_nuclear_efficiency_scaling_factor(ds, year, image_efficiency, agg_func=np.average):
    # Input an electricity dataset and year. We look up the efficiency for this region and year 
    # from the Image model and return the scaling factor compared to the improvement since 2012.
    # We do not consider the ecoinvent efficiency in 2012 as it is rather difficult to calculate and 
    # the burnup is not available. 
    # This is a simplification and certainly has it's weaknesses, 
    # however we argue that it's better than not chaning the datasets at all.
    # If the ecoinvent region corresponds to multiple Image regions we simply average them.
    image_locations= ecoinvent_to_image_locations(ds['location'])
    image_uranium_efficiency = agg_func(image_efficiency.loc[year][image_locations].values) # we take an average of all applicable image locations
    image_uranium_efficiency_2012 = agg_func(image_efficiency.loc[2012][image_locations].values)
    return image_uranium_efficiency_2012 / image_uranium_efficiency

def update_ecoinvent_efficiency_parameter(ds, scaling_factor):
    parameters = ds['parameters']
    possibles = ['efficiency', 'efficiency_oil_country', 'efficiency_electrical']

    for key in possibles:
        try: 
            parameters[key] /= scaling_factor
            return
        except KeyError:   
            pass




# This function imports the efficiency of fossil fuel power plant and returns a dataframe with the efficiency values for all years and regions for a specific technology.
def get_image_efficiencies(scenario, technology):
    
    #Reading from Electricity efficiencies
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



def get_image_electricity_emission_factors(scenario, image_efficiency, fuel2, sector= 'Power generation'):
    # This function imports a set of results from image for a certain scenario and returns
    # a dictionary of dataframes each with the emission values for all years and regions for one pollutant.
    # possible fuel2 choices are listed in  image_variable_names['Fuel2']
    
    emission_dict = {'CH4': "ENEFCH4.out",
                     'CO':"ENEFCO.out",
                     'N2O':"ENEFN2O.out",
                     'NOx':"ENEFNOx.out",
                     'SO2':"ENEFSO2.out",
                     'BC':"ENEFBC.out"}
    
    elec_emission_factors={}
    for k,v in emission_dict.items():
        fp = os.path.join(dr, scenario, v)
        elec_emission_factors[k]= load_image_data_file(fp)


    # We currently don't have a good way to deal with the fact that ecoinvent has many different VOCs listed.
    # For the moment we just allow them to scale with the efficiency.
    
    # Note that we don't import CO2 results as these are calculated by scaling using efficiency. 
    # This is more accurate as it considers that ecoinvent is more accurate regarding the energy content 
    # of the specific fuel used.

    image_emissions={}

    fuel2_number = np.where(IMAGE_variables['Fuel_type']==fuel2)[0][0]
    sector_number = np.where(IMAGE_variables['Sector']==sector)[0][0]
    
    for key, value in elec_emission_factors.items():
        image_emissions[key]={}
        for year in elec_emission_factors[key].years:
            image_emissions[key][year]={}

            for region, vector in zip(REGIONS[:-1], value.data[:, sector_number, fuel2_number,list(elec_emission_factors[key].years).index(year)]):
                image_emissions[key][year][region]=vector

        image_emissions[key]=pd.DataFrame.from_dict(image_emissions[key],orient='index')
        
        # Note that Image reports emissions pre unit of fuel in, so we have to make a couple of calculations
        if key == 'BC': image_emissions[key]= (image_emissions[key].divide(image_efficiency, axis=0))*3.6e-3 #convert to kg/kWh of electricity
        else: image_emissions[key]= (image_emissions[key].divide(image_efficiency, axis=0))*3.6e-6 #convert to kg/kWh of electricity
        image_emissions[key].replace({0: np.nan}, inplace=True) # we set all zero values to NaN so that the global average is calcuated only from values that exist.
        image_emissions[key]['World'] = image_emissions[key].mean(axis=1)
        image_emissions[key].fillna(0, inplace=True) #set nan values back to zero.

    return image_emissions







#THis dictionary is being used to store all the IMAGE DATA
image_mapping = {
    'Coal_ST': {  
        'fuel2': 'Coal',
        'eff_func': find_coal_efficiency_scaling_factor,
        'technology filters': coal_electricity + generic_excludes,
        'technosphere excludes': [retained_filter],
    },
    'Coal_CHP': {
        'fuel2': 'Coal',
        'eff_func': find_coal_efficiency_scaling_factor,
        'technology filters': coal_chp_electricity + generic_excludes,
        'technosphere excludes': [retained_filter],        
    },
    'Natural_gas_OC': {
        'fuel2': 'Natural gas',
        'eff_func': find_gas_efficiency_scaling_factor,
        'technology filters': gas_open_cycle_electricity + generic_excludes + no_imports,
        'technosphere excludes': [],                
    },
    'Natural_gas_CC': {
        'fuel2': 'Natural gas',
        'eff_func': find_gas_efficiency_scaling_factor,
        'technology filters': gas_combined_cycle_electricity + generic_excludes + no_imports, 
        'technosphere excludes': [],                
    },
    'Natural_gas_CHP': {
        'fuel2': 'Natural gas',
        'eff_func': find_gas_efficiency_scaling_factor,
        'technology filters': gas_chp_electricity + generic_excludes + no_imports, 
        'technosphere excludes': [],                
    },    
    'Oil_ST': {  
        'fuel2': 'Heavy liquid fuel',
        'eff_func': find_oil_efficiency_scaling_factor,
        'technology filters': oil_open_cycle_electricity + generic_excludes+ [exclude(contains('name', 'nuclear'))],
        'technosphere excludes': [],
    },  
    'Oil_CC': {  
        'fuel2': 'Heavy liquid fuel',
        'eff_func': find_oil_efficiency_scaling_factor,
        'technology filters': oil_combined_cycle_electricity + generic_excludes + [exclude(contains('name', 'nuclear'))] ,
        'technosphere excludes': [],
    }, 
    'Oil_CHP': {  
        'fuel2': 'Heavy liquid fuel',
        'eff_func': find_oil_efficiency_scaling_factor,
        'technology filters': oil_chp_electricity + generic_excludes + [exclude(contains('name', 'nuclear'))],
        'technosphere excludes': [],
    },
    'Biomass_ST': {  
        'fuel2': 'Biomass',
        'eff_func': find_biomass_efficiency_scaling_factor,
        'technology filters': biomass_electricity + generic_excludes + no_imports,
        'technosphere excludes': [],
    }, 
    'Biomass_CHP': {  
        'fuel2': 'Biomass',
        'eff_func': find_biomass_efficiency_scaling_factor,
        'technology filters': biomass_chp_electricity + generic_excludes,
        'technosphere excludes': [],
    }, 
    'Biomass_CC': {  
        'fuel2': 'Biomass',
        'eff_func': find_biomass_efficiency_scaling_factor,
        'technology filters': biomass_combined_cycle_electricity + generic_excludes,
        'technosphere excludes': [],
    }, 
    'Nuclear': {  
        'fuel2': None, #image parameter doesn't exist for nuclear
        'eff_func': find_nuclear_efficiency_scaling_factor,
        'technology filters': nuclear_electricity + generic_excludes,
        'technosphere excludes': [],
    }, 
}



def update_electricity_datasets_with_image_data(db, year, scenario, agg_func=np.average, update_efficiency = True, update_emissions = True):
    """    
    #for the moment we assume that particulates reduce according to the efficiency as we don't have any better data.
    
    """

    changes ={}
    
    for image_technology in image_mapping:
        print('Changing ', image_technology)
        md = image_mapping[image_technology]
        image_efficiency = get_image_efficiencies(scenario, image_technology)
        if image_technology != 'Nuclear':
            image_emissions = get_image_electricity_emission_factors(scenario, image_efficiency, fuel2=md.get('fuel2'))
        
        for ds in get_many(db, *md['technology filters']):
            
            
            changes[ds['code']]={}
            changes[ds['code']].update( {('meta data', x) : ds[x] for x in ['name','location']})
            changes[ds['code']].update( {('meta data', 'Image technology') : image_technology})
            changes[ds['code']].update( {('original exchanges', k) :v for k,v in get_exchange_amounts(ds).items()})
            
            
            '''This is the part where the input flows are changed right????'''
            if update_efficiency == True:
                # Modify using IMAGE efficiency values: 
                scaling_factor = md['eff_func'](ds, year, image_efficiency, agg_func)
                update_ecoinvent_efficiency_parameter(ds, scaling_factor)
                change_exchanges_by_constant_factor(ds, scaling_factor, md['technosphere excludes'], 
                                                [doesnt_contain_any('name', image_air_pollutants)])
            
            if image_technology != 'Nuclear': #We don't update emissions for nuclear WHY?
                
                if update_emissions == True:
                    # Modify using IMAGE specific emissions data
                    for exc in biosphere(ds, either(*[contains('name', x) for x in image_air_pollutants])):
                        image_locations = ecoinvent_to_image_locations(ds['location'])
                        flow = image_air_pollutants[exc['name']]
                        amount =  agg_func(image_emissions[flow].loc[year][image_locations].values)
                        
                        #if new amount isn't a number:
                        if np.isnan(amount): 
                            print('Not a number! Setting exchange to zero' + ds['name'], exc['name'], ds['location'])
                            rescale_exchange(exc, 0) 
                        
                        #if old amound was zero:
                        elif exc['amount'] ==0:
                            exc['amount'] = 1 
                            rescale_exchange(exc, amount / exc['amount'], remove_uncertainty = True)
                        
                        else: 
                            rescale_exchange(exc, amount / exc['amount'])
 
            changes[ds['code']].update( {('updated exchanges', k) :v for k,v in get_exchange_amounts(ds).items()}) 
    return changes

