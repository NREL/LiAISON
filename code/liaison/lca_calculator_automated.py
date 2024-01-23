import pandas as pd
import numpy as np
import sys
from pprint import pprint
from typing import List, Dict, Optional
import uuid

def create_search_index(ei_cf_36_db: List[Dict]) -> tuple[Dict, Dict]:
    """
    Create a search index dictionary storing the name and location of processes.

    Parameters:
    ei_cf_36_db (List[Dict]): The ecoinvent database.

    Returns:
    Tuple[Dict, Dict]: A tuple containing dictionaries representing the search index and problematic entries.
    """
    problems: Dict = {}
    dic: Dict = {}
    dic2: Dict = {}

    for entry in ei_cf_36_db:
        key = entry['name'].lower() + '@' + entry['location'].lower()
        try:
            dic[key].update({entry['code']: entry})
            problems[key] = entry
        except KeyError:
            dic[key] = {entry['code']: entry}
            dic2[key] = entry

    return dic, dic2


def read_search_index(process_name: str, process_location: str, database_dict: Dict) -> Optional[Dict]:
    """
    Return the process based on key consisting of process name and location.

    Parameters:
    process_name (str): Process name.
    process_location (str): Process location.
    database_dict (Dict): Database dictionary ecoinvent search index with process information.

    Returns:
    Optional[Dict]: Process information or None if not found.
    """
    key = process_name.lower() + '@' + process_location.lower()
    return database_dict.get(key)


def debug_search_index(database_dict: Dict, process_code: str) -> Dict:
    """
    Debug the search process for multiple process names and locations.

    Parameters:
    database_dict (Dict): Database dictionary ecoinvent search index with process information.
    process_code (str): Code for identification of the proper process when duplicate process names and locations exist.

    Returns:
    Dict: Process information.
    """
    if process_code == '0' or process_code == 0:
        if len(database_dict) == 1:
            for act in database_dict:
                return database_dict[act]

        else:
            print('\n  ******', flush=True)
            print('Multiple processes exist for - ', flush=True)
            temp_choice = []
            for act in database_dict:
                print(act, flush=True)
                pprint(database_dict[act])
                temp_choice.append(act)
            print('\n *****', flush=True)
            print("Choose the first row by default to resolve the issue temporarily", flush=True)
            chosen_act = temp_choice[0]
            return database_dict[chosen_act]
    else:
        if len(process_code) == 33:
            process_code = process_code[1:]

        return database_dict[process_code]

def dataframe_editor(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove trailing white spaces and convert dataframe to lower case to improve robustness of matching
    and skip over user errors
    Parameters:
    df (pd.DataFrame): Input dataframe
    Returns:
    df (pd.DataFrame)
    """
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)  
    return df

def merge_emissions(inp: pd.DataFrame, emission_name_bridge: str) -> pd.DataFrame:
    """
    Match common emission names with ecoinvent emission names.

    Parameters:
    inp (pd.DataFrame): Dataframe for matching with ecoinvent bridge name databases.
    emission_name_bridge (str): Filename for emissions name bridging csv.

    Returns:
    pd.DataFrame: Merged dataframe.
    """
    emission_name = dataframe_editor(pd.read_csv(emission_name_bridge))
    emission_bridge = inp.merge(emission_name, left_on='flow', right_on='Common_name').dropna()
    return emission_bridge

def merge_names(inp: pd.DataFrame, process_name_bridge: str, location_name_bridge: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Match common process and location names with ecoinvent process and location names.

    Parameters:
    inp (pd.DataFrame): Dataframe for matching with ecoinvent bridge name databases.
    process_name_bridge (str): Filename for process name bridging csv.
    location_name_bridge (str): Filename for location name bridging csv.

    Returns:
    Tuple[pd.DataFrame, pd.DataFrame]: Merged process dataframe and Merged location dataframe.
    """
    process_name = dataframe_editor(pd.read_csv(process_name_bridge))
    #location_name = dataframe_editor(pd.read_csv(location_name_bridge))


    process_bridge = inp.merge(process_name, left_on='flow', right_on='Common_name').dropna()
    #location_bridge = inp.merge(location_name, left_on='supplying_location', right_on='location_common').dropna()
    location_bridge = inp.reset_index()
    location_bridge['location_ecoinvent'] = location_bridge['supplying_location']

    return process_bridge, location_bridge

def uncertainty_adder(eco_d: str, activity: 'Activity', exchg_name: str) -> None:
    """
    Add uncertainty information to a specific exchange in the activity.

    Parameters:
        eco_d (str): The economic data.
        activity (Activity): The activity to which uncertainty information is added.
        exchg_name (str): The name of the exchange.

    Returns:
        None
    """
    yr = int(eco_d[10:14])
    for exchg in activity.exchanges():
        if exchg['name'] == exchg_name:
            exchg['uncertainty type'] = 2
            exchg['loc'] = np.log(exchg['amount'])
            exchg['scale'] = abs(np.log(exchg['amount'])) / 1000 * (yr - 2000) * 5
            pprint({'Uncertainty added': {'loc': exchg['loc'], 'scale': exchg['scale']}})
            exchg.save()

def emissions_index_creator(bw: 'brightway2') -> dict:
    """
    Create a dictionary of biosphere emissions.

    Parameters:
        bw (module): The brightway2 module.

    Returns:
        dict: Dictionary containing biosphere emissions.
    """
    biosphere = bw.Database('biosphere3')
    df_em = {}
    for i in biosphere:
        y = i.as_dict()
        df_em[y['code']] = i

    return df_em

def find_emission(emission_bridge: pd.DataFrame, emissions_dict: dict) -> 'Activity':
    """
    Find the corresponding biosphere emission for a given emission bridge.

    Parameters:
        emission_bridge (pd.DataFrame): DataFrame containing emission bridge information.
        emissions_dict (dict): Dictionary containing biosphere emissions.

    Returns:
        Activity: The corresponding biosphere emission activity.
    """
    if len(emission_bridge) == 1:
        pprint({'One emission match found': 'Check passed!!'})
        code = emission_bridge['Ecoinvent_code'][0]
        return emissions_dict[code]
    else:
        pprint({'Warning': 'More than one emission match found. Choosing the first match!!'})
        code = emission_bridge['Ecoinvent_code'][0]
        return emissions_dict[code]


def create_activity(inventory_row, database_dict, ei_cf_36_db):
    """
    Create a new activity in the database based on the inventory row.

    Parameters:
        inventory_row (pd.Series): Row from the inventory DataFrame.
        database_dict (dict): Dictionary containing the database information.
        ei_cf_36_db (bw.Database): Brightway2 Database object.

    Returns:
        tuple: (process_key, process) - Process key and the created process object.
    """
    process_info = inventory_row['process']
    location_info = inventory_row['process_location']
    activity_dic = read_search_index(process_info, location_info, database_dict)

    if activity_dic:
        if len(activity_dic) == 1:
            pprint({'One activity found': 'Check passed'})
        else:
            pprint({'Multiple activity found': None})

        p_code = list(activity_dic.keys())
        for pc in p_code:
            activity = debug_search_index(activity_dic, pc.strip())
            if activity:
                pprint({'Deleting': process_info})
                activity.delete()
            else:
                pprint({'Issue!!!': 'Existing activity not deleted'})
    else:
        pass

    pprint({'Activity Created': process_info, 'at': location_info})
    process_key = process_info + '@' + location_info
    process = ei_cf_36_db.new_activity(
        code=uuid.uuid4(), name=process_info, unit=inventory_row['unit'], location=location_info)
    process.save()

    return process_key, process

def create_activity_output_flow(process_key, process, inventory_row):
    """
    Create output flows for the given process in the database.

    Parameters:
        process_key (str): Key of the process.
        process (bw.Activity): Brightway2 Activity object.
        inventory_row (pd.Series): Row from the inventory DataFrame.
    """
    process.exchanges().delete()
    splited_key = process_key.split("@")
    process_key_name = splited_key[0]
    location_key_name = splited_key[1]
    inv = inventory_row[(inventory_row['process'] == process_key_name) & (inventory_row['process_location'] == location_key_name)]
    inp = inv[inv['type'] == 'production']

    if len(inp) == 1:
        pprint({'Production flows check passed'})
    elif len(inp) > 1:
        pprint({'Issue!!!': 'Production flows for an activity more than 1!!##############'})
    else:
        pprint({'No production flows!!'})

    for index, row in inp.iterrows():
        temp = pd.DataFrame([row])
        if temp.empty:
            pprint({'No production flow found in inventory'})
            pprint(temp)

        pprint(row['flow'] + ' Output flow created for ' + process_key_name + ' ' + location_key_name)
        process.new_exchange(input=process.key, name=row['flow'],
                              amount=row['value'], unit=row['unit'], type='production',
                              location=process['location']).save()
        process.save()

def create_technosphere_exchanges(process_key, process, inventory_row, process_name_bridge, location_name_bridge, mc_foreground_flag, database_dict, process_database_dict):
    """
    Create technosphere exchanges for the given process in the database.

    Parameters:
        process_key (str): Key of the process.
        process (bw.Activity): Brightway2 Activity object.
        inventory_row (pd.Series): Row from the inventory DataFrame.
        process_name_bridge (str): Placeholder for the process name bridge.
        location_name_bridge (str): Placeholder for the location name bridge.
        mc_foreground_flag (bool): Foreground for monte carlo foreground calculations.
        database_dict(dict): dictionary with ecoinvent process information
    """ 
    # Recreate the database dictionary so that the new created processes are listed in the inventory
    splited_key = process_key.split("@")
    process_key_name = splited_key[0]
    location_key_name = splited_key[1]
    inv = inventory_row[(inventory_row['process'] == process_key_name) & (inventory_row['process_location'] == location_key_name)]
    inp = inv[inv['type'] == 'technosphere']

    for index,row in inp.iterrows():
        temp=pd.DataFrame([row])   
        process_bridge, location_bridge = merge_names(temp, process_name_bridge, location_name_bridge)

        if process_bridge.empty or location_bridge.empty:
            pprint(row['flow'] + ' ' + row['supplying_location'])
            pprint('Did not find this process in the process bridge\n')
        else:
            pcode = str(process_bridge['Ecoinvent_code'][0]).strip()
            flag = 'activity found'
            unit_error_flag = 0
            
            try:
                activity_dic = read_search_index(process_bridge['Ecoinvent_name'][0],
                                              location_bridge['location_ecoinvent'][0], database_dict)
                activity = debug_search_index(activity_dic, str(process_bridge['Ecoinvent_code'][0]).strip())
                if activity['unit'] != row['unit']:
                    pprint({'Unit error': location_bridge['location_ecoinvent'][0] + ' for ' +
                            process_bridge['Ecoinvent_name'][0]})
                    unit_error_flag = 1

                process.new_exchange(input=activity.key, amount=row['value'], name=activity['name'],
                                     location=activity['location'], unit=row['unit'],
                                     type='technosphere').save()
                process.save()
                pprint({'Complete Success': 'Provided location ' + location_bridge['location_ecoinvent'][0].upper() +
                      ' for ' + process_bridge['Common_name'][0] + ' was found. Chosen location was ' +
                      activity['location'] + ' . Chosen process was ' + activity['name']})
            except:
                try:
                    activity_dic = read_search_index(process_bridge['Ecoinvent_name'][0], 'RNA', database_dict)
                    activity = debug_search_index(activity_dic, process_bridge['Ecoinvent_code'][0])
                    if activity['unit'] != row['unit']:
                        pprint({'Unit error': location_bridge['location_ecoinvent'][0].upper() + ' for ' +
                                process_bridge['Ecoinvent_name'][0]})
                        unit_error_flag = 1

                    process.new_exchange(input=activity.key, amount=row['value'], name=activity['name'],
                                         location=activity['location'], unit=row['unit'],
                                         type='technosphere').save()
                    process.save()
                    pprint({'Minor Success': 'Provided location ' + location_bridge['location_ecoinvent'][0].upper() +
                          ' for ' + process_bridge['Common_name'][0] + ' was not found. Shifting to ' +
                          activity['name'] + ' ' + activity['location']})
                except:
                    try:
                        activity_dic = read_search_index(process_bridge['Ecoinvent_name'][0], 'GLO', database_dict)
                        activity = debug_search_index(activity_dic, process_bridge['Ecoinvent_code'][0])
                        if activity['unit'] != row['unit']:
                            pprint({'Unit error': location_bridge['location_ecoinvent'][0].upper() + ' for ' +
                                    process_bridge['Ecoinvent_name'][0]})
                            unit_error_flag = 1

                        process.new_exchange(input=activity.key, amount=row['value'], name=activity['name'],
                                             location=activity['location'], unit=row['unit'],
                                             type='technosphere').save()
                        process.save()
                        pprint({'Minor Success': 'Provided location ' + location_bridge['location_ecoinvent'][0].upper() +
                              ' for ' + process_bridge['Common_name'][0] + ' was not found. Shifting to ' +
                              activity['name'] + ' ' + activity['location']})
                    except:
                        try:
                            activity_dic = read_search_index(process_bridge['Ecoinvent_name'][0], 'RoW',
                                                               database_dict)
                            activity = debug_search_index(activity_dic, process_bridge['Ecoinvent_code'][0])
                            if activity['unit'] != row['unit']:
                                pprint({'Unit error': location_bridge['location_ecoinvent'][0].upper() + ' for ' +
                                        process_bridge['Common_name'][0]})
                                unit_error_flag = 1

                            process.new_exchange(input=activity.key, amount=row['value'], name=activity['name'],
                                                 location=activity['location'], unit=row['unit'],
                                                 type='technosphere').save()
                            process.save()
                            pprint({'Minor Success': 'Provided location ' + location_bridge['location_ecoinvent'][0].upper() +
                                  ' for ' + activity['name'] + ' was not found. Shifting to ' +
                                  activity['name'] + ' ' + activity['location']})
                        except:
                            pprint({'Failed': 'Not found ' + process_bridge['Common_name'][0] + ' ' +
                                  location_bridge['location_ecoinvent'][0].upper() + ' ' +
                                  str(process_bridge['Ecoinvent_code'][0])})


            if flag == 'activity found':
                # Not implemented
                mc_foreground = mc_foreground_flag
                # if mc_foreground:
                # uncertainty_adder(db, process_dict[key], activity['name'])
                # continue

            if unit_error_flag == 1:
                pprint({'Correct unit should be': activity['unit']})
                sys.exit('Unit Error occurred, please check')

def create_biosphere_exchanges(process_key, process, inventory_row, emissions_dict, emission_name_bridge):
    """
    Create biosphere exchanges for the given process in the database.

    Parameters:
        process_key (str): Key of the process.
        process (bw.Activity): Brightway2 Activity object.
        inventory_row (pd.Series): Row from the inventory DataFrame.
        emissions_dict (dict): Dictionary containing emissions information.
        emission_name_bridge (str): Placeholder for the emission name bridge.
    """
    splited_key = process_key.split("@")
    process_key_name = splited_key[0]
    location_key_name = splited_key[1]
    inv = inventory_row[(inventory_row['process'] == process_key_name) & (inventory_row['process_location'] == location_key_name)]
    pprint('Creating biosphere exchanges for ' + process_key_name + ' at ' + location_key_name.upper())
    inp = inv[inv['type'] == 'biosphere']
    for index, row in inp.iterrows():
        unit_error_flag = 0
        temp = inp[inp['flow'] == row['flow']]
        emission_bridge = merge_emissions(temp, emission_name_bridge)

        if emission_bridge.empty:
            pprint(row['flow'] + ' Emission match not found from Emission Bridge!!')
        else:
            emission = find_emission(emission_bridge, emissions_dict)

            if emission is None:
                pprint('Emission not found ' + row['flow'])
            else:
                pprint('Emission found')
                if emission['unit'] != row['unit']:
                    pprint({'Emission unit error': row['supplying_location'].upper() + ' for ' +
                          emission_bridge['Ecoinvent_name'][0]})
                    unit_error_flag = 1
                else:
                    process.new_exchange(input=emission.key, amount=row['value'], name=emission['name'],
                                         unit=emission['unit'], type='biosphere').save()
                    process.save()
                    pprint({emission['name']: {'unit': emission['unit'],
                                               'amount': str(row['value'])}})

            if unit_error_flag == 1:
                pprint({'Correct unit should be': emission['unit']})
                sys.exit('Emission unit Error occurred, please check')

def brightway(db: str, run_filename: str, mc_foreground_flag: bool, mc_runs: int,
              process_name_bridge: str, emission_name_bridge: str, location_name_bridge: str,
              bw: 'brightway2') -> dict:

    """
    This function creates the process foreground within ecoinvent databases,
    every process activity, emissions and links them to the background ecoinvent processes.
    Emissions are also linked to the processes and biosphere emissions.

    Parameters:
        db (str): Ecoinvent database with scenario and year.
        run_filename (str): Intermediate filename with process inventory.
        mc_foreground_flag (bool): Flag to perform Monte Carlo simulation.
        mc_runs (int): Number of Monte Carlo runs.
        process_name_bridge (str): Filename for process name bridging csv.
        location_name_bridge (str): Filename for location name bridging csv.
        emission_name_bridge (str): Filename for emission name bridging csv.
        bw (module): Brightway2 module.

    Returns:
        dict: Dictionary containing process database information.
    """

    ei_cf_36_db = bw.Database(db)
    database_dict, process_database_dict = create_search_index(ei_cf_36_db)

    # Preprocessing
    pprint({'Reading from': run_filename})
    inventory = dataframe_editor(pd.read_csv(run_filename))
    del inventory['comments']
    process_dict = {}

    # Creating new activities
    pprint("Creating New activity")
    for index, row in inventory[inventory['type'] == 'production'].iterrows():
        process_key, process = create_activity(row, database_dict, ei_cf_36_db)
        process_dict[process_key] = process

    # Creating Activity output flow
    for key in process_dict:
        create_activity_output_flow(key, process_dict[key], inventory)

    # Recreate the database dictionary so that the new created processes are listed in the inventory
    database_dict, process_database_dict = create_search_index(ei_cf_36_db)
    # Define the flows that are inputs to the datasets (technosphere)
    pprint('Technosphere input flows')
    for key in process_dict:
        create_technosphere_exchanges(key, process_dict[key], inventory, process_name_bridge, location_name_bridge, mc_foreground_flag,database_dict, process_database_dict)

    pprint('Starting emissions')

    emissions_dict = emissions_index_creator(bw)

    for key in process_dict:
        create_biosphere_exchanges(key, process_dict[key], inventory, emissions_dict, emission_name_bridge)

    database_dict, process_database_dict = create_search_index(ei_cf_36_db)
    return process_database_dict

from collections import defaultdict
from typing import Tuple, Dict, List

def run_lcia_traci(
    db: pd.DataFrame,
    primary_process: 'ecoinvent process',
    functional_unit: str,
    mc_foreground_flag: bool,
    mc_runs: int,
    bw
) -> Tuple[Dict[str, Dict], int]:
    """
    Perform the LCA and LCIA calculations with the TRACI method.
    
    Parameters
    ----------
    db : pd.DataFrame
        Dataframe for matching with ecoinvent bridge name databases
        
    primary_process : ecoinvent process
        Ecoinvent process with the primary process under LCA study
    
    functional_unit : str
        Filename for location name bridging csv
            
    Returns
    -------
    Tuple[Dict[str, Dict], int]
        A tuple containing a dictionary with LCA results and the number of methods used.
    """

    method_key = [[m for m in bw.methods if 'TRACI' in str(m) and 'acidification' in str(m)][0],
          [m for m in bw.methods if 'TRACI' in str(m) and 'ecotoxicity' in str(m)][0],
          [m for m in bw.methods if 'TRACI' in str(m) and 'eutrophication' in str(m)][0],
          [m for m in bw.methods if 'TRACI' in str(m) and 'global warming' in str(m)][0],
          [m for m in bw.methods if 'TRACI' in str(m) and 'carcinogenics' in str(m)][1],
          [m for m in bw.methods if 'TRACI' in str(m) and 'ozone depletion' in str(m)][0],
          [m for m in bw.methods if 'TRACI' in str(m) and 'photochemical oxidation' in str(m)][0],
          [m for m in bw.methods if 'TRACI' in str(m) and 'non-carcinogenics' in str(m)][0],
          [m for m in bw.methods if 'TRACI' in str(m) and 'respiratory effects, average' in str(m)][0]]


    operation_functional_unit = {primary_process: functional_unit}
    operation_result = []

    lca_sol_cal_dict = defaultdict(dict)
    lca_sol_cal_dict[f'hydrogen{db}'] = {'functional unit': operation_functional_unit, 'result': operation_result}

    mc = mc_foreground_flag
    if mc:
        for key in lca_sol_cal_dict.keys():
            for method in method_key:
                mc_lca = bw.MonteCarloLCA(demand=operation_functional_unit, method=method)
                mc_results = [next(mc_lca) for _ in range(mc_runs)]
                lca_sol_cal_dict[key]['result'].append((method[2].title(), mc_results, bw.methods.get(method).get('unit')))
    else:
        for key in lca_sol_cal_dict.keys():
            lca = bw.LCA(lca_sol_cal_dict[key]['functional unit'])
            lca.lci()
            for method in method_key:
                lca.switch_method(method)
                lca.lcia()
                lca_sol_cal_dict[key]['result'].append((method[2].title(), lca.score, bw.methods.get(method).get('unit')))

    return lca_sol_cal_dict, len(method_key)


def run_lcia_recipe(
    db: pd.DataFrame,
    primary_process: 'ecoinvent process',
    functional_unit: str,
    mc_foreground_flag: bool,
    mc_runs: int,
    bw
) -> Tuple[Dict[str, Dict], int]:
    """
    Perform the LCA and LCIA calculations with the ReCiPe method.
    
    Parameters
    ----------
    db : pd.DataFrame
        Dataframe for matching with ecoinvent bridge name databases
        
    primary_process : ecoinvent process
        Ecoinvent process with the primary process under LCA study
    
    functional_unit : str
        Filename for location name bridging csv
            
    Returns
    -------
    Tuple[Dict[str, Dict], int]
        A tuple containing a dictionary with LCA results and the number of methods used.
    """
    method_key = [[m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'agricultural land occupation' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'climate change' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'fossil depletion' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'freshwater ecotoxicity' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'freshwater eutrophication' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'human toxicity' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'ionising radiation' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'marine ecotoxicity' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'marine eutrophication' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'metal depletion' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'natural land transformation' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'particulate matter formation' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'photochemical oxidant formation' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'terrestrial acidification' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'terrestrial ecotoxicity' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'urban land occupation' in str(m)][0],
                  [m for m in bw.methods if 'ReCiPe Midpoint (H) V1.13' == str(m[0]) and 'water depletion' in str(m)][0]]


    operation_functional_unit = {primary_process: functional_unit}
    operation_result = []

    lca_sol_cal_dict = defaultdict(dict)
    lca_sol_cal_dict[f'hydrogen{db}'] = {'functional unit': operation_functional_unit, 'result': operation_result}

    mc = mc_foreground_flag
    if mc:
        for key in lca_sol_cal_dict.keys():
            for method in method_key:
                mc_lca = bw.MonteCarloLCA(demand=operation_functional_unit, method=method)
                mc_results = [next(mc_lca) for _ in range(mc_runs)]
                lca_sol_cal_dict[key]['result'].append((method[2].title(), mc_results, bw.methods.get(method).get('unit')))
    else:
        for key in lca_sol_cal_dict.keys():
            lca = bw.LCA(lca_sol_cal_dict[key]['functional unit'])
            lca.lci()
            for method in method_key:
                lca.switch_method(method)
                lca.lcia()
                lca_sol_cal_dict[key]['result'].append((method[2].title(), lca.score, bw.methods.get(method).get('unit')))

    return lca_sol_cal_dict, len(method_key)


def run_lcia_premise_gwp(
    db: pd.DataFrame,
    primary_process: 'ecoinvent process',
    functional_unit: str,
    mc_foreground_flag: bool,
    mc_runs: int,
    bw
) -> Tuple[Dict[str, Dict], int]:
    """
    Perform the LCA and LCIA calculations with the Premise GWP method.
    
    Parameters
    ----------
    db : pd.DataFrame
        Dataframe for matching with ecoinvent bridge name databases
        
    primary_process : ecoinvent process
        Ecoinvent process with the primary process under LCA study
    
    functional_unit : str
        Filename for location name bridging csv
            
    Returns
    -------
    Tuple[Dict[str, Dict], int]
        A tuple containing a dictionary with LCA results and the number of methods used.
    """

    method_key = [[m for m in bw.methods if 'IPCC 2013' == str(m[0]) and 'GWP 100a, incl. H' == str(m[2])][0],
                  [m for m in bw.methods if 'IPCC 2013' == str(m[0]) and 'GWP 100a, incl. H and bio CO2' == str(m[2])][0]]
    operation_functional_unit = {primary_process: functional_unit}
    operation_result = []

    lca_sol_cal_dict = defaultdict(dict)
    lca_sol_cal_dict[f'hydrogen{db}'] = {'functional unit': operation_functional_unit, 'result': operation_result}

    mc = mc_foreground_flag
    if mc:
        for key in lca_sol_cal_dict.keys():
            for method in method_key:
                mc_lca = bw.MonteCarloLCA(demand=operation_functional_unit, method=method)
                mc_results = [next(mc_lca) for _ in range(mc_runs)]
                lca_sol_cal_dict[key]['result'].append((method[2].title(), mc_results, bw.methods.get(method).get('unit')))
    else:
        for key in lca_sol_cal_dict.keys():
            lca = bw.LCA(lca_sol_cal_dict[key]['functional unit'])
            lca.lci()
            for method in method_key:
                lca.switch_method(method)
                lca.lcia()
                lca_sol_cal_dict[key]['result'].append((method[2].title(), lca.score, bw.methods.get(method).get('unit')))
    
    save_db = False
    if save_db:
        ei_cf_36_db = bw.Database(db)
        ei_cf_36_db.backup()
        print('Backed up database')

    return lca_sol_cal_dict, len(method_key)

