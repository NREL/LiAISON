# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 10:23:35 2023

@author: tgoforth
"""

import pandas as pd
import os

# read in tech mapping file for simplified technology names and ecoinvent names
techMap = pd.read_excel('inputs/ReEDSTechNames.xlsx')

# read in regions file
regions = pd.read_csv('inputs/regions.csv')

# set variable for ReEDS run names, in list format, for example: [Mid_Case, Mid_Case_No_Nascent]
scen_names = os.listdir('Raw_ReEDS_Outputs')

#%% 
# create dictionary to save scenario specific generation data in for both regional aggregation types
genDict_BA = {}
genDict_national = {}

# loop through each ReEDS scenario
for scenario in scen_names:
    # gen_ivrt.csv contains generation across each region and model year for more detailed techs ('hydUD' rather than 'hydro' etc.), which is better for tech mapping
    gen = pd.read_csv('Raw_ReEDS_Outputs/'+scenario+'/gen_ivrt.csv').rename(columns={'Dim1':'Tech', 'Dim2':'Vintage', 'Dim3':'BA', 'Dim4':'Year', 'Val':'Generation (MWh)'})
    
    # merge generation with tech mapping and regional files in order to aggregate to correct tech groups and region groups (NERC etc)
    gen = pd.merge(gen, techMap, on = 'Tech', how = 'left')
    gen = pd.merge(gen, regions, on = 'BA', how = 'left')

    # aggregrate by chosen spatial resolution (national or BA)
    # national aggregation here 
    genAgg = {'Generation (MWh)':sum}

    # aggregate generation by technology and year 
    genTech_BA = gen.groupby(['ReEDS_Tech', 'Year', 'BA'], as_index = False).agg(genAgg)
    genTech_national = gen.groupby(['ReEDS_Tech', 'Year'], as_index = False).agg(genAgg)

    # place scenario specific generation data in dictionary
    genDict_BA[scenario] = genTech_BA
    genDict_national[scenario] = genTech_national
    
#%%
emitDict_BA = {}
emitDict_national = {}

for scenario in scen_names:
    # emit_irt.csv details emissions for each model year, technology, and emission type ( SOx, NOx, CH4) in metric tons across BA regions
    emitTech = pd.read_csv('Raw_ReEDS_Outputs/'+scenario+'/emit_irt.csv').rename(columns={'Dim1':'EmissionsType', 'Dim2':'Tech', 'Dim3':'BA', 'Dim4':'Year', 'Val':'Emissions (metric tons)'})
    emitTech = pd.merge(emitTech, techMap, on = 'Tech', how = 'left')
    emitTech = pd.merge(emitTech, regions, on = 'BA', how = 'left')

    # aggregate by EcoInvent technology
    # only CO2 is in kilo metric tons. Others are in metric tonnes. but we adjust this later using the emission scales file.
    emitAgg = {'Emissions (metric tons)':sum}
    emitTech_agg_BA = emitTech.groupby(['ReEDS_Tech', 'Year', 'BA', 'EmissionsType'], as_index = False).agg(emitAgg)
    emitTech_agg_national = emitTech.groupby(['ReEDS_Tech', 'Year', 'EmissionsType'], as_index = False).agg(emitAgg)

    # place scenario specific emissions data into dictionary
    emitDict_BA[scenario] = emitTech_agg_BA
    emitDict_national[scenario] = emitTech_agg_national
    
#%% 
# read in conversion rates for heat rates 
fuelConversion = pd.read_excel('inputs/ConversionRates.xlsx')

# read in ATB file that contains heat rate for each tech and each year 2010 - 2050
heatRate = pd.read_csv('inputs/conv_ATB_2022.csv')
heatRate = heatRate[['i', 't', 'heatrate']].copy().rename(columns = {'i':'Tech', 't':'Year', 'heatrate': 'Heat Rate (MMBtu/MWh)'})
heatRate = pd.merge(heatRate, techMap, on = 'Tech', how = 'left')
heatRate = pd.merge(heatRate, fuelConversion, on = 'Tech')

heatRateAgg = {'Heat Rate (MMBtu/MWh)':'mean'}
heatRate_avg = heatRate.groupby(['ReEDS_Tech', 'Year', 'Energy density', 'ED Units', 'Fuel input unit'], as_index = False).agg(heatRateAgg)

#%%
# conversion for MMBtu to MJ 
btu_per_mj = 947.817
btu_per_mmtbu = 1000000
kwh_per_MWh = 1000
emissionScales = pd.read_csv('inputs/EmissionScales.csv')

for scenario in scen_names:
    # calculate emissions rate (kg/kWh)
    generation_BA = genDict_BA[scenario] 
    emissions_BA = emitDict_BA[scenario] 

    generation_national = genDict_national[scenario] 
    emissions_national = emitDict_national[scenario]

    # BA
    emitRate_BA = pd.merge(generation_BA, emissions_BA, on = ['ReEDS_Tech', 'BA', 'Year'], how = 'left')
    emitRate_BA = pd.merge(emitRate_BA, emissionScales, on = ['EmissionsType'])
    emitRate_BA['EmissionsRate (kg/kWh)'] = emitRate_BA['Emissions (metric tons)']/(emitRate_BA['Generation (MWh)'])*emitRate_BA['Scale']
    # national
    emitRate_national = pd.merge(generation_national, emissions_national, on = ['ReEDS_Tech', 'Year'], how = 'left')
    emitRate_national = pd.merge(emitRate_national, emissionScales, on = ['EmissionsType'])
    emitRate_national['EmissionsRate (kg/kWh)'] = emitRate_national['Emissions (metric tons)']/(emitRate_national['Generation (MWh)'])*emitRate_national['Scale']

    # calculate fuel input (per kwh)
    # merge generation data with heat rate data and only include technologies 
    # BA
    fuelInput_BA = pd.merge(generation_BA, heatRate_avg, on = ['ReEDS_Tech', 'Year'], how = 'left')
    fuelInput_BA['Fuel Input'] = (fuelInput_BA['Heat Rate (MMBtu/MWh)'] * (1/fuelInput_BA['Energy density']) * 1/btu_per_mj * btu_per_mmtbu)/kwh_per_MWh
    # national
    fuelInput_national = pd.merge(generation_national, heatRate_avg, on = ['ReEDS_Tech', 'Year'], how = 'left')
    fuelInput_national['Fuel Input'] = (fuelInput_national['Heat Rate (MMBtu/MWh)'] * (1/fuelInput_national['Energy density']) * 1/btu_per_mj * btu_per_mmtbu)/kwh_per_MWh

    output_BA = pd.merge(emitRate_BA, fuelInput_BA, on = ['ReEDS_Tech', 'BA', 'Year', 'Generation (MWh)'], how = 'outer')
    output_national = pd.merge(emitRate_national, fuelInput_national, on = ['ReEDS_Tech', 'Year', 'Generation (MWh)'], how = 'outer')
    
    output2_BA = output_BA[['ReEDS_Tech', 'BA', 'Year', 'Generation (MWh)', 'Emissions (metric tons)', 'Heat Rate (MMBtu/MWh)', 'EmissionsType', 'EmissionsRate (kg/kWh)', 'Fuel Input', 'Fuel input unit']].copy()
    output2_national = output_national[['ReEDS_Tech', 'Year', 'Generation (MWh)', 'Emissions (metric tons)', 'Heat Rate (MMBtu/MWh)', 'EmissionsType', 'EmissionsRate (kg/kWh)', 'Fuel Input', 'Fuel input unit']].copy()
    
    # output to CSV
    output2_BA.to_csv('Modified_ReEDS_Outputs/'+scenario+'_output_BA.csv')
    output2_national.to_csv('Modified_ReEDS_Outputs/'+scenario+'_output_national.csv')