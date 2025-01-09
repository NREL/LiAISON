import sys
import pandas as pd



def search_activity_in_ecoinvent(dictionary,process_under_study,location_under_study,unit_under_study,run_filename,data_dir):
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

    run_filename = process_selected_as_foreground
    return run_filename
