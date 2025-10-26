
import pandas as pd
import numpy as np
import sys
import os 


pd.options.mode.chained_assignment = None

def edit_ecoinvent():
    #Reading the ecoinvent38 file
    ecoinvent38 = pd.read_excel('ecoinvent_updated_full.xlsx')
    ecoinvent38 = ecoinvent38.fillna('no information')
    ecoinvent38_row = ecoinvent38[ecoinvent38['process location'] == 'RoW']
    ecoinvent38_glo = ecoinvent38[ecoinvent38['process location'] == 'GLO']
    ecoinvent38_rer = ecoinvent38[ecoinvent38['process location'] == 'RER']
    
    
    
    ecoinvent38_extra = pd.concat([ecoinvent38_row,ecoinvent38_glo,ecoinvent38_rer])
    ecoinvent38_extra.to_csv('ecoinvent38_extra.csv',index=False)
    
    
    ecoinvent38_us = ecoinvent38[(ecoinvent38['process location'].str.contains('US')) | (ecoinvent38['process location'] == 'USA')]
    ecoinvent38_us.to_csv('ecoinvent_us.csv',index=False)



edit_ecoinvent()


def correct_ecoinvent(ecoinvent38):
    
    #Ecoinvent needs to be corrected to remove processes that produce the electricity as well as by products such as heat. The heat production activity needs to be removed
    ecoinvent38_production_flows =  ecoinvent38[ecoinvent38['type_of_flow'] == 'production']

    #Only choosing electricity flows from the production flow
    # Many flows in the new version of Ecoinvent do not have the name electricity, high voltage as a product.
    # Instead the name of the process is the product. So we are using the unit to extract those flows. 
    # Heat and power cogeneration was removed from the ecoinvent as because there are are duplicate activities. 
    # Currently there are still two activities with two flows - same name as process. However, one as unit of kilowatt hour and the other is MJ. The MJ one needs to be removed from the LCI. 
    ecoinvent38_production_flows_electricity = ecoinvent38_production_flows[ecoinvent38_production_flows['unit'].str.contains('kilowatt hour') ]
    #ecoinvent38_production_flows_electricity.to_excel('ecoinvent38_production_flows_electricity.xlsx', index = False)
    ecoinvent38_production_flows_electricity = ecoinvent38_production_flows_electricity['output']
    ecoinvent38_corr = ecoinvent38.merge(ecoinvent38_production_flows_electricity, on = "output")
    #Making all production flows at no information
    ecoinvent38_corr['inpu_t'].loc[ecoinvent38_corr['type_of_flow'] == 'production'] = 'No Information'
     
    #Making all production flows have no supplying activity as its not needed.
    ecoinvent38_corr['supplying activity'].loc[ecoinvent38_corr['type_of_flow'] == 'production'] = 'No Information'
    
    #making all production flows supplying activity as not needed
    ecoinvent38_corr['supplying activity location'].loc[ecoinvent38_corr['type_of_flow'] == 'production'] = 'No Information'
    
                
    #issue with lignite coal production having the input flow of lignite as lignite mine operation and not market for lignite. 
    #We need to replace the lignite mine operation with the name market for lignite
            
    ecoinvent38_corr.loc[:,'flows'] = ecoinvent38_corr.loc[:,'flows'].str.replace('lignite mine operation','market for lignite')
            
    
    #Removing all Russia locations due to location 2 letter digit error
    ecoinvent38_corr = ecoinvent38_corr[ecoinvent38_corr['process location'] != "RUS"]
    
    '''
    ecoinvent38_corr[['db','B','C','Ecoinvent_code','E']] = ecoinvent38_corr['inpu_t'].str.split("'", expand = True)
    ecoinvent38_corr1 = ecoinvent38_corr[ecoinvent38_corr['tyoe_of_flow'] == 'biosphere']
    ecoinvent38_corr2 = ecoinvent38_corr[ecoinvent38_corr['tyoe_of_flow'] != 'biosphere']
    ecoinvent38_corr1['code'] = ecoinvent38_corr1['Ecoinvent_code']
    ecoinvent38_corr2['code'] = None
    ecoinvent38_corr3 = pd.concat([ecoinvent38_corr1,ecoinvent38_corr2])
    '''
    
    
    
    return ecoinvent38_corr



def methane_gas_cc_ct_correction(df):

    #Changing methane emissoins of Gas CC and Gas CT technologies. 
    #Multiplying the Methane emissions with 0.001 to make it same as ecoinvent. 

    df_ng = df[(df['ReEDS_Tech'] == 'Gas_combined_cycle') | (df['ReEDS_Tech'] == 'Gas_combined_cycle_CCS') | (df['ReEDS_Tech'] == 'Gas_combustion_turbine')]
    df_non_ng = pd.concat([df,df_ng]).drop_duplicates(keep=False)


    df_ng_methane = df_ng[df_ng['EmissionsType'] == 'CH4']
    df_ng_non_methane = df_ng[df_ng['EmissionsType'] != 'CH4'] 
    df_ng_methane['EmissionsRate (kg/kWh)'] = df_ng_methane['EmissionsRate (kg/kWh)']/1000

    df_corrected = pd.concat([df_non_ng,df_ng_non_methane,df_ng_methane])
    df_corrected = df_corrected[['ReEDS_Tech', 'BA', 'Year', 'Generation (MWh)',
       'Emissions (metric tons)', 'Heat Rate (MMBtu/MWh)', 'EmissionsType',
       'EmissionsRate (kg/kWh)', 'Fuel Input', 'Fuel input unit']]
    df_corrected = df_corrected.sort_values(by=['ReEDS_Tech','BA', 'Year'])
    return df_corrected


def bio_co2_correction(df):

    #ReEDS probably calculates biogenic emissions and reports them after subtracing them from total emissions
    #This is why bio CCS emissions are negative. 
    #Biopower emission reported by ReEDS - 0

    #So we use ecoinvent reported emissions for these technologies. 

    df_bio_co2 = df[((df['ReEDS_Tech'] == 'Bioenergy_CCS') | (df['ReEDS_Tech'] == 'Biopower')) & (df['EmissionsType'] == "CO2")]
    df_corrected = pd.concat([df,df_bio_co2]).drop_duplicates(keep=False)
    df_corrected = df_corrected[['ReEDS_Tech', 'BA', 'Year', 'Generation (MWh)',
       'Emissions (metric tons)', 'Heat Rate (MMBtu/MWh)', 'EmissionsType',
       'EmissionsRate (kg/kWh)', 'Fuel Input', 'Fuel input unit']]
    return df_corrected



def process_inv(year1,scenario_base,reeds_output_raw):

    #Provide the ReEDS scenario being studied over here

    #Adding the region for US
    reeds_output_raw['BA'] = "US"

    scenario = scenario_base + str(year1)
    #Clean file
    f = open(scenario+"technologiesdonotexist.txt", "a")
    f.write('')
    f.close()
    #Methane emission correction for gas cc and gas ct
    reeds_output_raw = methane_gas_cc_ct_correction(reeds_output_raw)
    #Biopower co2 emissions correction
    reeds_output_raw = bio_co2_correction(reeds_output_raw)



    reeds_output = reeds_output_raw[(reeds_output_raw['Year'] == year1)]  
    # Emissions data
    reeds_biosphere = reeds_output[['ReEDS_Tech', 'BA', 'Year', 'EmissionsType',
                                    'EmissionsRate (kg/kWh)']]
    
    # Reading emissions bridge file. Matches the name of emissions in ReEDS with the emissions in Ecoinvent. 
    biosphere_bridge = pd.read_excel('BiosphereBridgeFile.xlsx')
    reeds_biosphere = reeds_biosphere.dropna(subset=['EmissionsRate (kg/kWh)'])
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
    
    #reeds_productioneration_mix_input.to_csv('ReEDS Gen mix.csv', index = False)
    reeds_production['Amount'] = 1
    
    #Matching the ReEDS technologies with the proper energy fuels. 
    reeds_technosphere = reeds_output[[
        'ReEDS_Tech', 'BA', 'Year', 'Fuel Input']].drop_duplicates()
    reeds_technosphere = reeds_technosphere.merge(reeds_tech_fuel,on = ['ReEDS_Tech'])
    
    #Matching the ReEDS fuel flows with corressponding Ecoinvent fuel flows. 
    reeds_technosphere = reeds_technosphere.merge(
        technosphere_bridge, on=['ReEDS_flow','Unit'])
    reeds_technosphere['Amount'] = reeds_technosphere['Fuel Input']
    reeds_technosphere = reeds_technosphere[[
        'ReEDS_Tech', 'BA', 'Year', 'ReEDS_flow', 'EcoInvent_flow', 'Amount', 'Type', 'Unit']]
    
    #The technosphere, production and biosphere columns are joined into one large dataframe.
    reeds_df_restructure = pd.concat(
        [reeds_production, reeds_technosphere, reeds_biosphere])


    #Bridge file matching ReEDS location to NERC regions in the United States
    region_bridge = pd.read_excel('ReEDS_State.xlsx')
    reeds_df_restructure = reeds_df_restructure.merge(
        region_bridge, left_on=['BA'], right_on=['Region'])
    del reeds_df_restructure['BA']
    
    
    #Creating names for ReEDS technologies to be stored as activities inside ecoinvent.
    reeds_df_restructure['Ecoinvent_process_to_be_created'] = 'Electricity production_' + \
        reeds_df_restructure['ReEDS_Tech']+'_ReEDS'
    reeds_df_restructure = reeds_df_restructure.sort_values(by='ReEDS_Tech')
    #reeds_df_restructure['comments'] = "From reeds"
    #Saving the restructured dataframe from ReEDS
    reeds_df_restructure.to_excel('./output/'+
        scenario+'_ReEDS_restructured_dataframe.xlsx', index=False)
    #At this point we have a ReEDS output dataframes that have been modified with some metadata. These metadata are bridge files that relate the
    #ReEDS fuel flows, emissions, technology names and locations to the proper ecoinvent names. These  bridge files have been generated manuallry. 
    
    #The next goal is to fill up missing information within the ReEDS datasets using data from Ecoinvent. 
    #This requires matching with Ecoinvent activities and some logical data manipulation. 
    
    #Reading the ecoinvent38 file
    ecoinvent38 = pd.read_csv('ecoinvent_us.csv')
    ecoinvent38 = ecoinvent38.fillna('no information')
    
    
    ecoinvent38_corr = correct_ecoinvent(ecoinvent38)
    ecoinvent38_corr.to_excel('ecoinvent38_corrected.xlsx', index = False)
    
    ecoinvent_extra = pd.read_csv('ecoinvent38_extra.csv')
    ecoinvent_extra = correct_ecoinvent(ecoinvent_extra)
    ecoinvent_extra.to_excel('ecoinvent38_extra_corrected.xlsx', index = False)
    
    
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
    #tech_fuel_df = tech_fuel_df[tech_fuel_df['ReEDS_Tech'] == 'Biopower']

    for index, row in tech_fuel_df.iterrows():
    
        
        #Extracting one particular process in a region and year
        data_from_reeds = reeds_df_restructure[(reeds_df_restructure['Ecoinvent_process_to_be_created']
                                                == row['Ecoinvent_process_to_be_created']) & (reeds_df_restructure['Region'] == row['Region']) & (reeds_df_restructure['Year'] == row['Year'])]

    
        data_from_reeds2 = data_from_reeds[['ReEDS_Tech','Region','NERC','Year','Ecoinvent_process_to_be_created']].drop_duplicates()
    
    
        tech_bridge2 = tech_bridge[['ReEDS_Tech','EcoInvent_Tech']].drop_duplicates()
        data_from_reeds3 = data_from_reeds2.merge(tech_bridge2, on = "ReEDS_Tech")

    
        #The data from reeds for one process is merged with the matching technology in Ecoinvent. 
        ecoinvent_data = ecoinvent38_corr.merge(data_from_reeds3,left_on=['process','process location'],right_on=['EcoInvent_Tech','NERC'])
       
        #If there is no match we match without the region. This is because when matching processes within ecoinvent, a certain technology may not have a corressponding process 
        #in a region within ecoinvent at all.
        #If there is a process, that completely matches within a region, we use that process to fillup our missing data. 
        #If there is a proces that does not match, we need to choose the same process in all other regions. We average them to create our missing information
     
        if ecoinvent_data.empty:
    
            '''
            data_from_reeds = reeds_df_restructure[(reeds_df_restructure['Ecoinvent_process_to_be_created']
                                                == row['Ecoinvent_process_to_be_created']) & (reeds_df_restructure['Region'] == row['Region']) & (reeds_df_restructure['Year'] == row['Year'])]            
            data_from_reeds2 = data_from_reeds[['ReEDS_Tech','Region','NERC','Year','Ecoinvent_process_to_be_created']].drop_duplicates()
            tech_bridge2 = tech_bridge[['ReEDS_Tech','EcoInvent_Tech']].drop_duplicates()
    
            #Matching only on name and doing the same as before
            data_from_reeds2 = data_from_reeds2.merge(tech_bridge2, on = "ReEDS_Tech")  
            '''
            
            ecoinvent_data = ecoinvent38_corr.merge(data_from_reeds3,left_on=['process'],right_on=['EcoInvent_Tech'])

            if ecoinvent_data.empty:
                
                ecoinvent_data = ecoinvent_extra.merge(data_from_reeds3,left_on=['process'],right_on=['EcoInvent_Tech'])
                
                if not ecoinvent_data.empty:
                    print('Using RoW RER GLO information for ',row['Ecoinvent_process_to_be_created'], row['Region'], row['NERC'], row['Year'])
    
            else:
       
                if "USA" not in list(ecoinvent_data['process location']):
                    print('Using NERC regions ',row['Ecoinvent_process_to_be_created'], row['Region'], row['NERC'], row['Year'])
    
                else:
                    print('Using USA regions ',row['Ecoinvent_process_to_be_created'], row['Region'], row['NERC'], row['Year'])
                    pass
  
        if not ecoinvent_data.empty:
            
                #Creating a debugging file for checking
                #ecoinvent_data.to_csv('ecoinvent_check_debugger.csv',index = False, mode = "a")
                new_data = data_from_reeds[['Amount','EcoInvent_flow']].drop_duplicates()
                #The calculations require some manipulation
                #Weight based averaging needs to be done
                #The weights will come from the tech bridge file again
                #Here 4 emissions and fuel flow should match with the ReEDS data and Ecoinvent file for substitition. 
                ecoinvent_data = ecoinvent_data.merge(new_data,left_on=['flows'],right_on=['EcoInvent_flow'],how = 'left')
                ecoinvent_data['Amount'] = ecoinvent_data['Amount'].fillna(0)

           
                #df_before_average = pd.concat([df_before_average,ecoinvent_data])
                ecoinvent_data['comments']="none"
                ecoinvent_data['comments'] = np.where(ecoinvent_data['Amount'] != 0, "from Reeds","none")
                ecoinvent_data['amount'] = np.where(ecoinvent_data['Amount'] != 0, ecoinvent_data['Amount'], ecoinvent_data['amount'])
    

                #Changing the output flows to a common name for electricity production
                ecoinvent_data_production = ecoinvent_data[ecoinvent_data['type_of_flow'] == 'production']
                ecoinvent_data_not_production = ecoinvent_data[ecoinvent_data['type_of_flow'] != 'production']
                ecoinvent_data_production['flows'] = 'electricity, high voltage'
                
                
                ecoinvent_data=pd.concat([ecoinvent_data_production,ecoinvent_data_not_production])
            
              
                tech_bridge3 = tech_bridge[['ReEDS_Tech','EcoInvent_Tech','Weight']].drop_duplicates()
    
                #Merging to get weight data for processes
                ecoinvent_data = ecoinvent_data.merge(tech_bridge3,left_on=['ReEDS_Tech','EcoInvent_Tech'],right_on=['ReEDS_Tech','EcoInvent_Tech'])
                
 
    
                '''
                If there are no splitting of activities the weights should be 1
                If there are splits, then weights will not be 1
                For weights not 1, we need to do a multiplication before and then change the weights to 1 as regions will be averaged equally. 
                '''
                ecoinvent_data['amount'] = ecoinvent_data['amount'] * ecoinvent_data['Weight']
                ecoinvent_data['Weight'] = 1
                #df_before_average = pd.concat([ecoinvent_data,df_before_average])

                try:
                    
                    ecoinvent_data_f = ecoinvent_data.groupby(['process','ReEDS_Tech', 'Region', 'Year', 'NERC','flows', 'type_of_flow',
                           'unit','Ecoinvent_process_to_be_created','inpu_t','supplying activity','supplying activity location','comments']).apply(w_avg, 'amount', 'Weight').reset_index()
 
                    
                    ecoinvent_data_f1 = ecoinvent_data_f.groupby(['ReEDS_Tech', 'Region', 'Year', 'NERC','flows', 'type_of_flow',
                            'unit','Ecoinvent_process_to_be_created','inpu_t','supplying activity','supplying activity location','comments']).agg('sum').reset_index()


                    
                    ecoinvent_data_f1['amount'] = ecoinvent_data_f1[0]
                    del ecoinvent_data_f1[0]
                    reeds_data_to_brightway2 = pd.concat([reeds_data_to_brightway2,ecoinvent_data_f1])
                    
    
                except:
                    print('Calculation errors')
                    
                     
        else:
            #print(row['Ecoinvent_process_to_be_created'], row['Region'], row['NERC'], row['Year'])
            #print('Technology does not exist!!!!')
            
            # opening the file in write only mode
            f = open(scenario+"technologiesdonotexist.txt", "a")
            # f is the File Handler
            text=row['Ecoinvent_process_to_be_created']+ row['Region']+ row['NERC']+ str(row['Year'])
            f.write(text)
            pass
    
    
    #df_before_average.to_excel('./output'+scenario+'Dataframe_before_average.xlsx',index=False) 
    
    reeds_data_to_brightway2.to_excel('./output/'+scenario+'_Reeds_data_2_brightway.xlsx',index = False)
    
    #Some final adjustments to the dataframe
    output = pd.read_excel('./output/'+scenario+'_Reeds_data_2_brightway.xlsx')
    output['location'] = output['NERC']+'-'+output['Region']
    output['input'] = 'FALSE'
    
     
    output['input'].loc[output['type_of_flow'] == 'technosphere'] = 'TRUE'
    output['process_location'] = output['location']
    output['supplying_location'] = output['supplying activity location']
    output['supplying_location'].loc[output['type_of_flow'] == 'production'] = output['process_location']
    
    output['code'] = output['inpu_t']
    output = output.rename(columns = {
                                      'flows' : 'flow',
                                      'Year' : 'year',
                                      'type_of_flow' : 'type',
                                      'amount' : 'value'})
    output['process'] = output['Ecoinvent_process_to_be_created']
    
    
    #output['comments'].loc[output['type'] == 'biosphere'] = 'stack'
    
    output2 = output[['process', 'flow', 'code','value', 'unit', 'input', 'year', 'type', 'process_location','supplying_location','supplying activity','comments']].copy()
    #output2.to_csv(scenario+'_datafile.csv',index=False)
    final_cols = ['process','flow','code','value','unit','input','year','comments','type','process_location','supplying_location']
    output3 = output2[['process','flow','code','value','unit','input','year','comments','type','process_location','supplying_location']]
    
    
    output3.to_csv('./output/'+scenario+'before_ccs.csv')
    
    #The carbon dioxide CCS unit part
    
    #here we need to separate out flows for CCS units and separate all those technologies that include CCS units from this dataframe. 
    #Then we need to find CO2 net values
    #Then we need to obtained CO2 gross, captured and net values
    #Then we need to update the CO2 emissions and the CO2 capture separately. 
    
    #Read the CCS Tech Flow Bridge file
    ccstechflowbridge=pd.read_csv('ccs_techflowbridge.csv')
    
    
    #Creating names for ReEDS technologies to be stored as activities inside ecoinvent.
    ccstechflowbridge['Ecoinvent_process_to_be_created'] = 'Electricity production_' + \
        ccstechflowbridge['ReEDS_Tech']+'_ReEDS'
        
    ccstechflowbridge[['process']] = ccstechflowbridge[['Ecoinvent_process_to_be_created']]
    
    ccstechflowbridge = ccstechflowbridge[['flow','process']]
    df_ccs = output3.merge(ccstechflowbridge,on = ['process','flow'], how = 'outer', indicator = True)

     
    
    df_ccs2 = df_ccs[df_ccs['_merge'] == 'both']
    df_not_ccs2 = df_ccs[df_ccs['_merge'] == 'left_only']
    df_not_ccs2 = df_not_ccs2[output3.columns]

    
    df_co2 = df_not_ccs2[(df_not_ccs2['flow'] == 'Carbon dioxide, fossil') | (df_not_ccs2['flow'] == 'Carbon dioxide, non-fossil') ]
    df_co2.loc[:,'co2_total_emitted'] = df_co2.loc[:,'value']/0.10
    df_co2.loc[:,'co2_total_captured'] = df_co2.loc[:,'co2_total_emitted']*0.90
    df_co2 = df_co2[['process','process_location','co2_total_emitted','year','co2_total_captured']]
    df_ccs3 = df_ccs2.merge(df_co2,on=['process','process_location','year'])
    df_ccs3['value'] = df_ccs3['co2_total_captured']
    df_ccs3 = df_ccs3[output3.columns]

    
    output4 = pd.concat([df_not_ccs2,df_ccs3]).sort_values(by=['process','process_location'])

   
    
    #Extracting an output file for easy debugging
    reeds_debugging1 = output4[(output4['type'] == 'technosphere') | (output4['type'] == 'production')]
    reeds_debugging2 = output4[(output4['flow'] == 'Carbon monoxide, fossil') | (output4['flow'] == 'Carbon monoxide, non-fossil')]
    reeds_debugging3 = output4[(output4['flow'] == 'Carbon dioxide, fossil') | (output4['flow'] == 'Carbon dioxide, non-fossil')]
    
    
    debugloc = ['US-MRO-p37','US-FRCC-p102','US-NPCC-p127','US-RFC-p114','US-SERC-p83','US-SPP-p55','US-WECC-p24']
    
    reeds_debugging = pd.concat([reeds_debugging1,reeds_debugging2,reeds_debugging3])
    reeds_debugging = reeds_debugging[reeds_debugging['process_location'].isin(debugloc)]
    reeds_debugging.to_csv('./output/'+scenario+'output_debugger_checker.csv',index=False)
    
    
    co2debug = output4[(output4['flow'] == 'Carbon dioxide, fossil') | (output4['flow'] == 'Carbon dioxide, non-fossil')]
    co2debug.to_csv('./output/'+scenario+'CO2_output_debugger_checker.csv',index=False)
    
    
    flows_debug = output4
    debug_cols = ['process', 'flow', 'value',
           'process_location']
    flows_debug['_duplicates'] = output4.duplicated(subset = debug_cols, keep = False)
    flows_debug = flows_debug[flows_debug['_duplicates'] == True]
    flows_debug.to_csv('./output/'+scenario+'Duplicates_output_debugger_checker.csv',index=False)
    
    output4 = output4.drop_duplicates(subset = ['process', 'flow', 'value', 'unit', 'input', 'year', 'comments', 'type',
           'process_location'])
    
    
    output4[['db','B','C','code','E']] = output4['code'].str.split("'", expand = True)
    output5 = output4[final_cols]
    return output5


def grid_mix_inv(year1,scenario_base):


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

        #reeds_productioneration_mix_input.to_csv('ReEDS Gen mix.csv', index = False)


        # Technologymappingfile - maps ReEDS technologies to Ecoinvent technologies. This is the main matching file between ReEDS and Ecoinvent activities
        # it also houses weights for technology matching
        tech_bridge = pd.read_excel('ReEDS_EcoInvent_TechMapping.xlsx')
        tech_bridge = tech_bridge[['ReEDS_Tech']]
        reeds_productioneration_mix_input = reeds_productioneration_mix_input.merge(tech_bridge,on=['ReEDS_Tech'] )


        region_bridge = pd.read_excel('ReEDS_State.xlsx')
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
        #output.to_csv(scenario+'genmix_datafile.csv',index=False)
        output2 = output[['process', 'flow','value', 'unit', 'input', 'year', 'type', 'process_location','supplying_location','comments']].copy()

        output2 = output2.drop_duplicates()
        #Create production flow
        production_df = pd.DataFrame()
        production_df['process'] = ['ReEDS_US_Grid_Mix']
        production_df['flow'] = ['electricity high voltage']
        production_df['value'] = [1]
        production_df['unit'] = ['kilowatt hour']
        production_df['input'] = ['FALSE']
        production_df['year'] = [year1]
        production_df['comments'] = ['none']
        production_df['type'] = ['production']
        production_df['process_location'] = ['US']
        production_df['supplying_location'] = ['No information']


        total_output = output2['value'].sum()
        output2['value'] = output2['value']/total_output


        output3 = output2[['process','flow','value','unit','input','year','comments','type','process_location','supplying_location']]
        output3 = pd.concat([output3,production_df])

        output3 = output3.sort_values('supplying_location')
        return output3


def regional_grid_mix_inv(year1,scenario_base):
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

    #reeds_productioneration_mix_input.to_csv('ReEDS Gen mix.csv', index = False)


    # Technologymappingfile - maps ReEDS technologies to Ecoinvent technologies. This is the main matching file between ReEDS and Ecoinvent activities
    # it also houses weights for technology matching
    tech_bridge = pd.read_excel('ReEDS_EcoInvent_TechMapping.xlsx')
    tech_bridge = tech_bridge[['ReEDS_Tech']]
    reeds_productioneration_mix_input = reeds_productioneration_mix_input.merge(tech_bridge,on=['ReEDS_Tech'] )


    region_bridge = pd.read_excel('ReEDS_State.xlsx')
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
    output['process_location'] = output['location']
    output['supplying_location'] = output['location']
    #output['supplying_location'].loc[output['type_of_flow'] != 'production'] = 'US'

    output = output.rename(columns = {'ReEDS_Tech' : 'process',
                                      'flows' : 'flow',
                                      'Year' : 'year',
                                      'type_of_flow' : 'type',
                                      'Amount' : 'value',
                                      'Unit':'unit'})

    output['process'] = 'ReEDS_regional_Grid_Mix'
    output['flow'] = output['Ecoinvent_process_to_be_created']
    output['comments'] = 'none'
    output['comments'].loc[output['type'] == 'biosphere'] = 'stack'
    #output.to_csv(scenario+'genmix_datafile.csv',index=False)
    output2 = output[['process', 'flow','value', 'unit', 'input', 'year', 'type', 'process_location','supplying_location','comments']].copy()

    output2 = output2.drop_duplicates()
    
    loc_list = list(pd.unique(output2['process_location']))
    df_grid_mix_dataset = pd.DataFrame()
    for loc in loc_list:
        df3 = output2[output2['process_location'] == loc]
        total_output = df3['value'].sum()
        df3['value'] = df3['value']/total_output


        #Create production flow
        production_df = pd.DataFrame()
        production_df['process'] = ['ReEDS_regional_Grid_Mix']
        production_df['flow'] = ['electricity high voltage']
        production_df['value'] = [1]
        production_df['unit'] = ['kilowatt hour']
        production_df['input'] = ['FALSE']
        production_df['year'] = [year1]
        production_df['comments'] = ['none']
        production_df['type'] = ['production']
        production_df['process_location'] = loc
        production_df['supplying_location'] = ['No information']


        output3 = df3[['process','flow','value','unit','input','year','comments','type','process_location','supplying_location']]
        output4 = pd.concat([output3,production_df])
        output4 = output4.sort_values('supplying_location')
        df_grid_mix_dataset = pd.concat([df_grid_mix_dataset,output4])
    return df_grid_mix_dataset
    #df_grid_mix_dataset.to_csv(scenario+'regional_grid_mix_ecoinvent_format.csv',index=False)


def joiner_db(scenario,df1,df2,df3):

        #df1 = pd.read_csv(scenario+'_ecoInvent_format.csv')
        #df2 = pd.read_csv(scenario+'_grid_mix_ecoinvent_format.csv')
        #df3 = pd.read_csv(scenario+'regional_grid_mix_ecoinvent_format.csv')
        df4 = pd.concat([df1,df2,df3])
        df4.to_csv('./reedsdata/'+scenario+'_reeds_data_national.csv',index=False)

years = [2020,2022,2024,2026,2028,2030,2032,2034,2036,2038,2040,2042,2044,2046,2048,2050]
# years = [2022,2024,2036,2050]
# set variable for ReEDS run names, in list format, for example: [Mid_Case, Mid_Case_No_Nascent]
scen_names = os.listdir('./ReEDS_postprocessing/Raw_ReEDS_Outputs')

#scen_names = ["Mid_Case","Mid_Case_95by2050","Mid_Case_100by2035"]
#scen_names = ["Mid_Case_100by2035"]
#scen_names = ['climatetarget2036']

for scenario_base in scen_names:
    reeds_output_raw = pd.read_csv('./ReEDS_postprocessing/Modified_ReEDS_Outputs/'+scenario_base+'_output_national.csv')
    #reeds_output_raw = pd.read_csv('./climatetarget.csv')
    for year1 in years:

        A=process_inv(year1,scenario_base,reeds_output_raw)
        B=grid_mix_inv(year1,scenario_base)
        C=regional_grid_mix_inv(year1,scenario_base)
        scenario = scenario_base + str(year1)
        joiner_db(scenario,A,B,C)
    
    break



