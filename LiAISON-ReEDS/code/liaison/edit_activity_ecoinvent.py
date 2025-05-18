def user_controlled_editing_ecoinvent_activity(process_selected_as_foreground,year_of_study,location_under_study,data_dir):
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
    print('Editing activities within ecoinvent to US location and US state wise grid mix',flush=True)
    new_location = location_under_study

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
    for exch in process_selected_as_foreground.exchanges():
            process.append(process_selected_as_foreground['name'])            
            value.append(exch['amount'])
            unit.append(exch['unit'])

            #Changing name of electricity flow
            #Changing name of electricity flow
            #name_of_flow = electricity_correction(exch)
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
                supplying_location.append(new_location)
            

            elif exch['type'] =='biosphere':
                input_1.append(False)
                type_1.append('biosphere')
                supplying_location.append('None')
                common_emission_name.append(exch['name'])
                ecoinvent_emission_name.append(exch['name'])
                code_emission.append(exch['input'][1])
                flow_code.append(exch['input'][1])


            year.append(year_of_study)
            comments.append('None')
            process_location.append(new_location)
            

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
    example.to_csv(data_dir+process_selected_as_foreground['name']+str(year_of_study)+location_under_study+'.csv',index=False)
    run_filename = example


    return run_filename
