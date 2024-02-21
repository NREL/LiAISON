# HIPSTER

"""
Reeds and Ecoinvent matcher
"""


import pandas as pd
import numpy as np
import sys
import os 

scenario_base = "Mid_Case"
years = [2020,2024,2028,2032,2036,2042,2048]
reeds_output_raw = pd.read_csv('./ReEDS_Outputs/'+scenario_base+'_output_BA.csv')

#Creating an empty copy of the ecoinvent_check_debugger.csv useful for checking issues. 
ecoinvent_data=pd.DataFrame()
ecoinvent_data.to_csv('ecoinvent_check_debugger.csv')


for year1 in years:

    scenario = scenario_base + str(year1)
    #Provide the ReEDS scenario being studied over here
    
    # Reading ReEDS Output file
    reeds_output = reeds_output_raw[(reeds_output_raw['Year'] == year1)]


    # Emissions data
    reeds_biosphere = reeds_output[['ReEDS_Tech', 'BA', 'Year', 'EmissionsType',
                                    'EmissionsRate (kg/kWh)']]


    # Reading emissions bridge file. Matches the name of emissions in ReEDS with the emissions in Ecoinvent. 
    biosphere_bridge = pd.read_excel('BiosphereBridgeFile.xlsx')
    reeds_biosphere = reeds_biosphere.merge(
        biosphere_bridge, left_on='EmissionsType', right_on='ReEDS_flow')
    reeds_biosphere['Amount'] = reeds_biosphere['EmissionsRate (kg/kWh)']



    # Matches the name of production flows with the outputflows of Ecoinvent. 
    production_bridge = pd.read_excel('ProductionBridgeFile.xlsx')

    # Unit columns
    reeds_biosphere['Unit'] = "kilogram"
    reeds_biosphere = reeds_biosphere[[
        'ReEDS_Tech', 'ReEDS_flow', 'BA', 'Year', 'EcoInvent_flow', 'Type', 'Amount', 'Unit']]


    #Reading the technosphere bridge file. It matches technosphere flows ( Fuel input flows between ReEDS and Ecoinvent)
    technosphere_bridge = pd.read_excel('TechnosphereBridgeFile.xlsx')

    #This matches ReEDS technology with the Kind of ReEDS input energy flow required. Gas CC to Natural gas. 
    reeds_tech_fuel = pd.read_excel('ReEDS_Tech_Fuel.xlsx')



    #Taking ReEDs data
    reeds_production = reeds_output[[
        'ReEDS_Tech', 'BA', 'Year', 'Generation (MWh)']].drop_duplicates()


    #Rearranging ReEDS data
    reeds_production = reeds_output.melt(id_vars=['ReEDS_Tech', 'BA', 'Year'], value_vars=[
                                         'Generation (MWh)'], var_name='ReEDS_flow', value_name='Amount').drop_duplicates()

    #Mergin with production bridge based on the ReEDS flow and ReEDS Tech columns. Matches the technology name of ReEDS with the production flow. 
    reeds_production = reeds_production.merge(
        production_bridge, on=['ReEDS_flow', 'ReEDS_Tech'])

    #Creating the ReEDS production dataframe with names of production flows with the ReEDS technologies. 
    reeds_productioneration_mix_input = reeds_production

    reeds_productioneration_mix_input.to_csv('ReEDS Gen mix.csv', index = False)


    # Technologymappingfile - maps ReEDS technologies to Ecoinvent technologies. This is the main matching file between ReEDS and Ecoinvent activities
    # it also houses weights for technology matching
    tech_bridge = pd.read_excel('ReEDS_EcoInvent_TechMapping.xlsx')
    tech_bridge = tech_bridge[['ReEDS_Tech']]
    reeds_productioneration_mix_input = reeds_productioneration_mix_input.merge(tech_bridge,on=['ReEDS_Tech'] )


    region_bridge = pd.read_excel('ReEDS_NERC.xlsx')
    reeds_productioneration_mix_input = reeds_productioneration_mix_input.merge(
        region_bridge, left_on=['BA'], right_on=['Region']).dropna().drop_duplicates()

    #Creating names for ReEDS technologies to be stored as activities inside ecoinvent. 
    reeds_productioneration_mix_input['Ecoinvent_process_to_be_created'] = 'Electricity production_' + \
        reeds_productioneration_mix_input['ReEDS_Tech']+'_ReEDS'
    reeds_productioneration_mix_input = reeds_productioneration_mix_input.sort_values(by='ReEDS_Tech')


    output = reeds_productioneration_mix_input
    output['type_of_flow'] = 'technosphere'
    output['location'] = output['NERC']+'-'+output['Region']
    output['input'] = 'FALSE'
    output['input'].loc[output['type_of_flow'] == 'technosphere'] = 'TRUE'
    output['process_location'] = 'US'
    output['supplying_location'] = output['location']
    #output['supplying_location'].loc[output['type_of_flow'] != 'production'] = 'US'

    output = output.rename(columns = {'ReEDS_Tech' : 'process',
                                      'flows' : 'flow',
                                      'Year' : 'year',
                                      'type_of_flow' : 'type',
                                      'Amount' : 'value',
                                      'Unit':'unit'})

    output['process'] = 'ReEDS_US_Grid_Mix'
    output['flow'] = output['Ecoinvent_process_to_be_created']
    output['comments'] = 'none'
    output['comments'].loc[output['type'] == 'biosphere'] = 'stack'
    output.to_csv(scenario+'genmix_datafile.csv',index=False)
    output2 = output[['process', 'flow','value', 'unit', 'input', 'year', 'type', 'process_location','supplying_location','comments']].copy()

    output2 = output2.drop_duplicates()
    #Create production flow
    production_df = pd.DataFrame()
    production_df['process'] = ['ReEDS_US_Grid_Mix']
    production_df['flow'] = ['electricity high voltage']
    production_df['value'] = [1]
    production_df['unit'] = ['kilowatt hour']
    production_df['input'] = ['FALSE']
    production_df['year'] = [2020]
    production_df['comments'] = ['none']
    production_df['type'] = ['production']
    production_df['process_location'] = ['US']
    production_df['supplying_location'] = ['No information']


    total_output = output2['value'].sum()
    output2['value'] = output2['value']/total_output


    output3 = output2[['process','flow','value','unit','input','year','comments','type','process_location','supplying_location']]
    output3 = pd.concat([output3,production_df])

    output3 = output3.sort_values('supplying_location')

    output3.to_csv(scenario+'_grid_mix_ecoinvent_format.csv',index=False)
    #output3 = reeds_productioneration_mix_input[['process','flow','value','unit','input','year','comments','type','process_location','supplying_location']]
    #reeds_productioneration_mix_input = reeds_productioneration_mix_input[[]]

'''
import pandas as pd 

scenario = 'Mid_Case'

ecoInventFormat = pd.read_csv(scenario+'_grid_mix_ecoinvent_format.csv')

processBridge = ecoInventFormat[['process', 'flow', 'type']].copy()

processBridge['common_name'] = processBridge['flow']
processBridge['ecoinvent_name'] = processBridge['flow']

processBridge['ecoinvent_name'].loc[processBridge['type'] == 'production'] = processBridge['process']
processBridge['ecoinvent_code'] = 0

output = processBridge[['common_name','ecoinvent_name','ecoinvent_code','type']].copy()

output = output[(output['type'] != 'production') & (output['type'] != 'biosphere')]

output = output.drop_duplicates()

output.to_csv('process_name_bridge_genmix.csv',index = False)

sys.exit(0)



#Matching the ReEDS technologies with the proper energy fuels. 
reeds_technosphere = reeds_output[[
    'ReEDS_Tech', 'BA', 'Year', 'Fuel Input (kg or m3 / kWh)']].drop_duplicates()
reeds_technosphere = reeds_technosphere.merge(reeds_tech_fuel,on = ['ReEDS_Tech'])


#Matching the ReEDS fuel flows with corressponding Ecoinvent fuel flows. 
reeds_technosphere = reeds_technosphere.merge(
    technosphere_bridge, on=['ReEDS_flow','Unit'])
reeds_technosphere['Amount'] = reeds_technosphere['Fuel Input (kg or m3 / kWh)']
reeds_technosphere = reeds_technosphere[[
    'ReEDS_Tech', 'BA', 'Year', 'ReEDS_flow', 'EcoInvent_flow', 'Amount', 'Type', 'Unit']]


#The technosphere, production and biosphere columns are joined into one large dataframe. 
reeds_df_restructure = pd.concat(
    [reeds_production, reeds_technosphere, reeds_biosphere])

#Bridge file matching ReEDS location to NERC regions in the United States
region_bridge = pd.read_excel('ReEDS_NERC.xlsx')
reeds_df_restructure = reeds_df_restructure.merge(
    region_bridge, left_on=['BA'], right_on=['Region'])
del reeds_df_restructure['BA']


#Creating names for ReEDS technologies to be stored as activities inside ecoinvent. 
reeds_df_restructure['Ecoinvent_process_to_be_created'] = 'Electricity production_' + \
    reeds_df_restructure['ReEDS_Tech']+'_ReEDS'
reeds_df_restructure = reeds_df_restructure.sort_values(by='ReEDS_Tech')

#Saving the restructured dataframe from ReEDS 
reeds_df_restructure.to_excel(
    scenario+'_ReEDS_restructured_dataframe.xlsx', index=False)


#At this point we have a ReEDS output dataframes that have been modified with some metadata. These metadata are bridge files that relate the
#ReEDS fuel flows, emissions, technology names and locations to the proper ecoinvent names. These  bridge files have been generated manuallry. 

#The next goal is to fill up missing information within the ReEDS datasets using data from Ecoinvent. 
#This requires matching with Ecoinvent activities and some logical data manipulation. 

#Reading the ecoinvent38 file
ecoinvent38 = pd.read_excel('ecoinvent38_USA.xlsx')
ecoinvent38 = ecoinvent38.fillna('no information')


#Ecoinvent needs to be corrected to remove processes that produce the electricity as well as by products such as heat. The heat production activity needs to be removed
ecoinvent38_production_flows =  ecoinvent38[ecoinvent38['type_of_flow'] == 'production']

#Only choosing electricity flows from the production flow
ecoinvent38_production_flows_electricity = ecoinvent38_production_flows[ecoinvent38_production_flows['flows'].str.contains('electricity') ]
#ecoinvent38_production_flows_electricity.to_excel('ecoinvent38_production_flows_electricity.xlsx', index = False)
ecoinvent38_production_flows_electricity = ecoinvent38_production_flows_electricity['output']
ecoinvent38_corr = ecoinvent38.merge(ecoinvent38_production_flows_electricity, on = "output")
#Making all production flows at no information
ecoinvent38_corr['inpu_t'].loc[ecoinvent38_corr['type_of_flow'] == 'production'] = 'No Information'
 
#Making all production flows have no supplying activity as its not needed.
ecoinvent38_corr['supplying activity'].loc[ecoinvent38_corr['type_of_flow'] == 'production'] = 'No Information'


ecoinvent38_corr.to_excel('ecoinvent38_corrected.xlsx', index = False)




#Creating a smaller dataframe from reeds dataframe with technology name and region
tech_fuel_df = reeds_df_restructure[[
    'ReEDS_Tech', 'Region', 'NERC', 'Ecoinvent_process_to_be_created','Year']].drop_duplicates()

# Technologymappingfile - maps ReEDS technologies to Ecoinvent technologies. This is the main matching file between ReEDS and Ecoinvent activities
# it also houses weights for technology matching
tech_bridge = pd.read_excel('ReEDS_EcoInvent_TechMapping.xlsx')


reeds_data_to_brightway2 = pd.DataFrame()

def w_avg(df, values, weights):
        d = df[values]
        w = df[weights]
        return (d * w).sum() / w.sum()

df_before_average = pd.DataFrame()

     

for index, row in tech_fuel_df.iterrows():

    print(row['Ecoinvent_process_to_be_created'], row['Region'], row['NERC'], row['Year'])
    #Extracting one particular process in a region and year
    data_from_reeds = reeds_df_restructure[(reeds_df_restructure['Ecoinvent_process_to_be_created']
                                            == row['Ecoinvent_process_to_be_created']) & (reeds_df_restructure['Region'] == row['Region']) & (reeds_df_restructure['Year'] == row['Year'])]
    

    data_from_reeds2 = data_from_reeds[['ReEDS_Tech','Region','NERC','Year','Ecoinvent_process_to_be_created']].drop_duplicates()


    tech_bridge2 = tech_bridge[['ReEDS_Tech','EcoInvent_Tech']].drop_duplicates()
    data_from_reeds2 = data_from_reeds2.merge(tech_bridge2, on = "ReEDS_Tech")

    #The data from reeds for one process is merged with the matching technology in Ecoinvent. 
    ecoinvent_data = ecoinvent38_corr.merge(data_from_reeds2,left_on=['process','process location'],right_on=['EcoInvent_Tech','NERC'])
   
    #If there is no match we match without the region. This is because when matching processes within ecoinvent, a certain technology may not have a corressponding process 
    #in a region within ecoinvent at all.
    #If there is a process, that completely matches within a region, we use that process to fillup our missing data. 
    #If there is a proces that does not match, we need to choose the same process in all other regions. We average them to create our missing information

    if ecoinvent_data.empty:

        data_from_reeds = reeds_df_restructure[(reeds_df_restructure['Ecoinvent_process_to_be_created']
                                            == row['Ecoinvent_process_to_be_created']) & (reeds_df_restructure['Region'] == row['Region']) & (reeds_df_restructure['Year'] == row['Year'])]            
        data_from_reeds2 = data_from_reeds[['ReEDS_Tech','Region','NERC','Year','Ecoinvent_process_to_be_created']].drop_duplicates()
        tech_bridge2 = tech_bridge[['ReEDS_Tech','EcoInvent_Tech']].drop_duplicates()

        #Matching only on name and doing the same as before
        data_from_reeds2 = data_from_reeds2.merge(tech_bridge2, on = "ReEDS_Tech")  
        
        ecoinvent_data = ecoinvent38_corr.merge(data_from_reeds2,left_on=['process'],right_on=['EcoInvent_Tech'])


    if not ecoinvent_data.empty:
        
            #Creating a debugging file for checking
            ecoinvent_data.to_csv('ecoinvent_check_debugger.csv',index = False, mode = "a")
            new_data = data_from_reeds[['Amount','EcoInvent_flow']].drop_duplicates()

            #The calculations require some manipulation
            #Weight based averaging needs to be done
            #The weights will come from the tech bridge file again
            ecoinvent_data = ecoinvent_data.merge(new_data,left_on=['flows'],right_on=['EcoInvent_flow'],how = 'left')
            ecoinvent_data['Amount'] = ecoinvent_data['Amount'].fillna(0)
            ecoinvent_data['amount'] = np.where(ecoinvent_data['Amount'] != 0, ecoinvent_data['Amount'], ecoinvent_data['amount'])
            
            tech_bridge3 = tech_bridge[['EcoInvent_Tech','Weight']]

            #Merging to get weight data for processes
            ecoinvent_data = ecoinvent_data.merge(tech_bridge3,left_on=['EcoInvent_Tech'],right_on=['EcoInvent_Tech'])


            If there are no splitting of activities the weights should be 1
            If there are splits, then weights will not be 1
            For weights not 1, we need to do a multiplication before and then change the weights to 1 as regions will be averaged equally. 

            ecoinvent_data['amount'] = ecoinvent_data['amount'] * ecoinvent_data['Weight']
            ecoinvent_data['Weight'] = 1

            #df_before_average = pd.concat([ecoinvent_data,df_before_average])

            try:
                
                ecoinvent_data_f = ecoinvent_data.groupby(['process','ReEDS_Tech', 'Region', 'Year', 'NERC','flows', 'type_of_flow',
                       'unit','Ecoinvent_process_to_be_created','inpu_t','supplying activity']).apply(w_avg, 'amount', 'Weight').reset_index()
                ecoinvent_data_f1 = ecoinvent_data_f.groupby(['ReEDS_Tech', 'Region', 'Year', 'NERC','flows', 'type_of_flow',
                        'unit','Ecoinvent_process_to_be_created','inpu_t','supplying activity']).agg('sum').reset_index()
                
                ecoinvent_data_f1['amount'] = ecoinvent_data_f1[0]
                del ecoinvent_data_f1[0]
                reeds_data_to_brightway2 = pd.concat([reeds_data_to_brightway2,ecoinvent_data_f1])
            
            except:
                print('Calculation errors')
                
    else:

        print('Technology does not exist!!!!')

df_before_average.to_excel(scenario+'Dataframe_before_average.xlsx',index=False) 

reeds_data_to_brightway2.to_excel(scenario+'_Reeds_data_2_brightway.xlsx',index = False)

scenario = 'Mid_Case'

#Some final adjustments to the dataframe
output = pd.read_excel(scenario+'_Reeds_data_2_brightway.xlsx')
output['location'] = output['NERC']+'-'+output['Region']
output['input'] = 'FALSE'
output['input'].loc[output['type_of_flow'] == 'technosphere'] = 'TRUE'
output['process_location'] = output['location']
output['supplying_location'] = output['location']
output['supplying_location'].loc[output['type_of_flow'] != 'production'] = 'US'

output['code'] = output['inpu_t']
output = output.rename(columns = {'ReEDS_Tech' : 'process',
                                  'flows' : 'flow',
                                  'Year' : 'year',
                                  'type_of_flow' : 'type',
                                  'amount' : 'value'})
output['process'] = output['Ecoinvent_process_to_be_created']

output['comments'] = 'none'
output['comments'].loc[output['type'] == 'biosphere'] = 'stack'

output2 = output[['process', 'flow', 'code','value', 'unit', 'input', 'year', 'type', 'process_location','supplying_location','supplying activity','comments']].copy()
output2.to_csv(scenario+'_datafile.csv',index=False)


output3 = output2[['process','flow','value','unit','input','year','comments','type','process_location','supplying_location']]
output3.to_csv(scenario+'_ecoInvent_format.csv',index=False)


#Removing all production flows other than electriclity
output3_with_production = output3[output3['type'] == 'production']
output3_non_production = output3[output3['type'] != 'production']

output3_with_production_elec = output3_with_production[output3_with_production['flow'].str.contains('electricity')]

output4 = pd.concat([output3_non_production,output3_with_production_elec])
output4 = output4.sort_values(by = ['process','year','process_location']).drop_duplicates()

output4.to_csv(scenario+'_ecoInvent_format.csv',index=False)

'''
