import sys
import pandas as pd


def extract_process(process_selected_as_foreground):
    """
    Extract process from the dictionary

    Parameters
    ----------

    Returns
    -------

    """
    # These variables are used to create inventory dataframe
    process = []
    flow = []
    value = []
    unit = []
    input_1 = []
    year = []
    comments = []
    type_1 = []
    process_location = []
    supplying_location = []
    flow_code = []

    # These variables are used to create the emissions and process bridge dataframes
    common_name = []
    ecoinvent_name = []
    common_emission_name = []
    ecoinvent_emission_name = []
    code = []
    code_emission = []


    #Extracting ecoinvent database for activity and flows and creating a LiAISON friendly dataframe
    for key in process_selected_as_foreground.keys():
        for exch in process_selected_as_foreground[key].exchanges():
            process.append(process_selected_as_foreground[key]['name'])            
            value.append(exch['amount'])
            unit.append(exch['unit'])

            #Changing name of electricity flow
            name_of_flow = exch['name']
            flow.append(name_of_flow)

            if exch['type'] == 'production':
                input_1.append(False)
                type_1.append('production')
                supplying_location.append(exch['location'])
                flow_code.append(exch['input'][1])
            

            elif exch['type'] =='technosphere':
                input_1.append(True)
                type_1.append('technosphere')
                common_name.append(name_of_flow)
                ecoinvent_name.append(name_of_flow)
                code.append(exch['input'][1])

                #Appending 0 to flow code for technosphere since we want to change the location of these flows. 
                #They need to be searched in the proper location
                flow_code.append(0)
                supplying_location.append(exch['location'])
            

            elif exch['type'] =='biosphere':
                input_1.append(False)
                type_1.append('biosphere')
                supplying_location.append('None')
                common_emission_name.append(exch['name'])
                ecoinvent_emission_name.append(exch['name'])
                code_emission.append(exch['input'][1])
                flow_code.append(exch['input'][1])

            year_of_study = 2020
            year.append(year_of_study)
            comments.append('None')
            process_location.append(process_selected_as_foreground[key]['location'])
            

    # Creating of the inventory dataframe
    example = pd.DataFrame(columns=['process', 'flow', 'value', 'unit', 'input', 'year', 'comments', 'type',
           'process_location', 'supplying_location'])
    
    example['process'] = process
    example['flow'] = flow
    example['value'] = value
    example['unit'] = unit
    example['input'] = input_1
    example['year'] = year
    example['comments'] = comments
    example['type'] = type_1
    example['process_location'] = process_location
    example['supplying_location'] = supplying_location
    example['code'] = flow_code

    return example




def scope1(process_selected_as_foreground,data_dir):
    """
    Scope 1 calculations
    Parameters:
    ----------
    dictionary: dictionary
        This contains the entire ecoinvent database as a dictionary with key name as processes and locations

    Returns:
    -------
    """
    example = extract_process(process_selected_as_foreground)

    example = example[example['type'] != "technosphere"]
    #Sanity check to write the dataframe. Can be deleted later
    example.to_csv(data_dir+'Scope1_edited_process.csv',index=False)
    run_filename = example

    return run_filename



def scope2(db,process_selected_as_foreground,location_under_study,data_dir,bw):
    """
    Scope 2 calculations
    """
    print('Scope 2 emissions are being calculated by deleting all flows in the primary activity other than electricity use and removing all technosphere flows of electricity production activities',flush = True)
    example = extract_process(process_selected_as_foreground)
    product_edited_df = example[example['type'] == 'production']
    electricity_edited_df = example[example['flow'].str.contains('electricity')]
    edited_df = pd.concat([product_edited_df,electricity_edited_df])

    #In Scope 2 all flows except electricity needs to be removed
    #Sanity check to write the dataframe. Can be deleted later
    edited_df.to_csv(data_dir+'Scope2_edited_process.csv',index=False)

    # Editing the database to remove all electricity production technosphere flows so that only upstream included in the calculations
    ei_38_db = bw.Database(db)
    for process in ei_38_db:
        if ('electricity production' in process['name']):
            if 'market' not in process['name']:
                if (process['location'] == location_under_study) or ('CN' in process['location']):
                    print(process['name'],process['location'],' deleting technosphere flows',flush=True)
                    for exch in process.exchanges():
                        if exch['type'] == "technosphere":
                            # Deleting exchanges
                            exch.delete()
            process.save()
    
    return edited_df



