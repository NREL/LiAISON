import sys
import pandas as pd


def electricity_correction(exchange_ob):
    """
    We need an additional correction. All instances of electricity flows needs to be changed with ReEDS_State_Grid_mix
    
    Parameters:
    ----------
    exchange_obj: Ecoinvent exchange object
        Ecoinvent flow datasets

    Returns:
    -------
    name_of_flow: str
        name of the flow to be changed

    """
    if 'electricity' in exchange_ob['name']:
        name_of_flow = 'market group for electricity, high voltage'
    else:
        name_of_flow = exchange_ob['name']

    return name_of_flow


def search_activity_in_ecoinvent_for_editing(dictionary,process_under_study,location_under_study,unit_under_study,run_filename,data_dir):
    """
    This function searches for activities and edits the ecoinvent activity as a foreground process in the chosen location
    It extracts every flow in the chosen foreground process, creates a dataframe from it and changes the location
    It also changes the electricity flow name

    Parameters:
    ----------
    dictionary: dictionary
        This contains the entire ecoinvent database as a dictionary with key name as processes and locations

    Returns:
    -------
    """

    default_unit = unit_under_study
    state_location = location_under_study
    print('Searching for activity to extract from Ecoinvent and changing location and processes',flush=True)
    print('Editing activities within ecoinvent to US location and US state wise grid mix',flush=True)
    print(process_under_study+'@'+location_under_study+'@'+default_unit, 'to be searched')
    try:
        process_selected_as_foreground = dictionary[process_under_study+'@'+location_under_study+'@'+default_unit]        
        print('Complete success: Process found in ecoinvent in chosen location',flush=True)
    except:
            try:
                location_under_study = 'US'
                process_selected_as_foreground = dictionary[process_under_study+'@'+location_under_study+'@'+default_unit]
                print('Minor success: Process found in ecoinvent in US',flush=True)
            
            except:
                try:
                    location_under_study = 'RoW'
                    process_selected_as_foreground = dictionary[process_under_study+'@'+location_under_study+'@'+default_unit]
                    print('Minor success: Process found in ecoinvent in RoW',flush=True)
                except:
                        try:
                            location_under_study = 'GLO'
                            process_selected_as_foreground = dictionary[process_under_study+'@'+location_under_study+'@'+default_unit]
                            print('Minor success: Process found in ecoinvent in GLO',flush=True)

                        except:
                            print('****Failed -- Did not find this process in Ecoinvent. Please check process****',flush=True)
                            return run_filename
                            #todo needs to change when we will be also having activities being read from csv files


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
            name_of_flow = electricity_correction(exch)
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
                supplying_location.append(state_location)
            

            elif exch['type'] =='biosphere':
                input_1.append(False)
                type_1.append('biosphere')
                supplying_location.append('None')
                common_emission_name.append(exch['name'])
                ecoinvent_emission_name.append(exch['name'])
                code_emission.append(exch['input'][1])
                flow_code.append(exch['input'][1])


            year.append(2020)
            comments.append('None')
            process_location.append(state_location)
            

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

    #Sanity check to write the dataframe. Can be deleted later
    example.to_csv(data_dir+'example_process.csv',index=False)
    run_filename = pd.concat([run_filename,example])

    '''
    # Creating of process and emission bridge dataframes
    process_name_bridge_dynamic = pd.DataFrame()
    emission_name_bridge_dynamic = pd.DataFrame()

    process_name_bridge_dynamic['Common_name'] = common_name
    process_name_bridge_dynamic['Ecoinvent_name'] = common_name
    process_name_bridge_dynamic['type'] = 'technosphere'

    emission_name_bridge_dynamic['Common_name'] = common_emission_name
    emission_name_bridge_dynamic['Ecoinvent_name'] = ecoinvent_emission_name
    emission_name_bridge_dynamic['Ecoinvent_code'] = code_emission
    emission_name_bridge_dynamic['type'] = 'biosphere'

    # The bridge dataframes are never overwritten. Only appended. 
    try:
        process_name_bridge_df = pd.read_csv(process_name_bridge)
    except:
        process_name_bridge_df = pd.DataFrame()


    try:
        emission_name_bridge_df = pd.read_csv(emission_name_bridge)
    except:
        emission_name_bridge_df = pd.DataFrame()

    # The bridge dataframes are never overwritten. Only appended. 
    process_name_bridge_df = pd.concat([process_name_bridge_df,process_name_bridge_dynamic]).drop_duplicates()
    emission_name_bridge_df = pd.concat([emission_name_bridge_df,emission_name_bridge_dynamic]).drop_duplicates()

    process_name_bridge_df.to_csv(process_name_bridge,index=False)
    emission_name_bridge_df.to_csv(emission_name_bridge,index=False)
    '''

    return run_filename
