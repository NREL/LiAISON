import sys
import pandas as pd
import uuid
import numpy as np
import time


def search_index_creator(ei_cf_36_db):
    """
    Create dictionaries to index ecoinvent activities by process name, location, and unit.

    Parameters
    ----------
    ei_cf_36_db : brightway2.Database
        The ecoinvent database object from Brightway2.

    Returns
    -------
    tuple of dict
        - Primary dictionary with keys of the form "name@location@unit" and values as dicts of code:activity.
        - Secondary dictionary with keys as process codes and values as activity objects.
    """
    dic = {}
    dic2 = {}
    for i in ei_cf_36_db:
        try:
            _ = dic[i['name'] + '@' + i['location'] + '@' + i['unit']]
        except:
            dic[i['name'] + '@' + i['location'] + '@' + i['unit']] = {}
        dic[i['name'] + '@' + i['location'] + '@' + i['unit']][i['code']] = i
        dic2[str(i['code'])] = i
    return dic, dic2


def search_index_reader(p_name, p_loc, p_unit, data_dict):
    """
    Retrieve a specific ecoinvent activity from a pre-indexed dictionary using process metadata.

    Parameters
    ----------
    p_name : str
        Name of the process.
    p_loc : str
        Location of the process.
    p_unit : str
        Unit of the process.
    data_dict : dict
        Dictionary from `search_index_creator`.

    Returns
    -------
    brightway2.Activity
        Matching activity from ecoinvent, or last matching item if multiple found.
    """
    dic_key = p_name + '@' + p_loc + '@' + p_unit
    activity_dict = data_dict[dic_key]
    if len(activity_dict) == 1:
        for key in activity_dict:
            return activity_dict[key]
    else:
        print(f'\nLength Issue: {len(activity_dict)} matches for {dic_key}')
        for key in activity_dict:
            print('Multiple activities found ---- ', activity_dict[key], key)
        return activity_dict[key]


def uncertainty_adder(eco_d, activity, exchg_name):
    """
    Add lognormal uncertainty to a specific exchange within an activity.

    Parameters
    ----------
    eco_d : str
        Name of the ecoinvent database (used to extract year).
    activity : brightway2.Activity
        Brightway2 activity object.
    exchg_name : str
        Name of the exchange to modify.

    Returns
    -------
    None
    """
    yr = int(eco_d[10:14])
    for exchg in activity.exchanges():
        if exchg['name'] == exchg_name:
            exchg['uncertainty type'] = 2
            exchg['loc'] = np.log(exchg['amount'])
            exchg['scale'] = abs(np.log(exchg['amount'])) / 1000 * (yr - 2000) * 5
            print(f'Uncertainty added: loc={exchg["loc"]}, scale={exchg["scale"]}')
            exchg.save()


def emissions_index_creator(bw):
    """
    Create indexed dictionaries of emissions from the biosphere database.

    Parameters
    ----------
    bw : module
        Brightway2 module.

    Returns
    -------
    tuple of dict
        - Dictionary mapping emission names to lists of matching biosphere flows.
        - Dictionary mapping emission codes to biosphere flow objects.
    """
    biosphere = bw.Database('biosphere3')
    df_em = {}
    df_em2 = {}

    for i in biosphere:
        y = i.as_dict()
        df_em.setdefault(y['name'], []).append(i)
        df_em2[y['code']] = i

    return df_em, df_em2


def find_emission(emission_name, emissions_dict):
    """
    Look up an emission by name in the indexed dictionary.

    Parameters
    ----------
    emission_name : str
        Name of the emission to search.
    emissions_dict : dict
        Emissions dictionary created by `emissions_index_creator`.

    Returns
    -------
    list or None
        List of matching emissions, or None if not found.
    """
    return emissions_dict.get(emission_name)


def reeds_db_editor(db, run_filename, bw):
    """
    Integrate ReEDS-generated inventory into a Brightway2 ecoinvent database.

    This function:
    - Creates or overwrites activities in the target database using a ReEDS inventory CSV.
    - Adds production, technosphere, and biosphere exchanges.
    - Links processes and emissions using string matching and UUID lookups.

    Parameters
    ----------
    db : str
        Name of the ecoinvent database (e.g., modified for a scenario).
    run_filename : str or df
        Path to CSV file containing ReEDS process and emissions inventory.
    bw : module
        Brightway2 module instance.

    Returns
    -------
    None
    """
    ei_cf_36_db = bw.Database(db)
    print('Creating inventory within the database:', db, flush=True)
    database_dict, database_dict_secondary = search_index_creator(ei_cf_36_db)

    if isinstance(run_filename, str):
        inventory = pd.read_csv(run_filename)
    else:
        inventory = run_filename

    inventory = inventory.sort_values(by=['process', 'process_location'])

    # Create new or update existing processes
    processes = inventory[inventory['type'] == 'production']
    process_dict = {}

    for _, row in processes.iterrows():
        key = row['process'] + '@' + row['process_location']
        try:
            activity = search_index_reader(row['process'], row['process_location'], row['unit'], database_dict)
            activity.exchanges().delete()
            process_dict[key] = activity
        except:
            activity = ei_cf_36_db.new_activity(code=uuid.uuid4(), name=row['process'],
                                                unit=row['unit'], location=row['process_location'])
            activity.save()
            process_dict[key] = activity

    # Add production flows
    for key, activity in process_dict.items():
        activity.exchanges().delete()
        p_name, p_loc = key.split('@')
        flow_data = inventory[(inventory['process'] == p_name) & 
                              (inventory['process_location'] == p_loc) & 
                              (inventory['type'] == 'production')]
        for _, row in flow_data.iterrows():
            activity.new_exchange(
                input=activity.key, name=row['flow'], amount=row['value'],
                unit=row['unit'], type='production', location=activity['location']
            ).save()
            activity['reference product'] = row['flow']
            activity['production amount'] = row['value']
            activity['unit'] = row['unit']
            activity.save()

    # Update dictionary with new activities
    database_dict, database_dict_secondary = search_index_creator(ei_cf_36_db)

    # Add technosphere flows
    for key in process_dict:
        t0 = time.time()
        p_name, p_loc = key.split('@')
        tech_inputs = inventory[(inventory['process'] == p_name) &
                                (inventory['process_location'] == p_loc) &
                                (inventory['type'] == 'technosphere')]
        for _, row in tech_inputs.iterrows():
            activity = None
            try:
                activity = database_dict_secondary[str(row['code'])]
            except:
                for loc in [row['supplying_location'], 'USA', 'US', 'RNA', 'RoW', 'GLO', 'RER']:
                    try:
                        activity = search_index_reader(row['flow'], loc, row['unit'], database_dict)
                        break
                    except:
                        continue
            if activity is None:
                print(f'Warning --- Not found: {row["flow"]} @ {row["supplying_location"]}')
                continue

            if activity['unit'] != row['unit']:
                print(f'Warning --- Unit mismatch for {row["flow"]}: expected {activity["unit"]}, got {row["unit"]}')
                sys.exit('Unit mismatch error')

            process_dict[key].new_exchange(
                input=activity.key, amount=row['value'], name=activity['name'],
                location=activity['location'], unit=activity['unit'], type='technosphere'
            ).save()
            process_dict[key].save()

        print(f'{time.time() - t0:.2f}s for technosphere connections to {key}')

    # Add biosphere flows
    print('Adding Biosphere Flows', flush=True)
    emissions_dict, emissions_code_dict = emissions_index_creator(bw)
    for key in process_dict:
        t0 = time.time()
        p_name, p_loc = key.split('@')
        bio_inputs = inventory[(inventory['process'] == p_name) &
                               (inventory['process_location'] == p_loc) &
                               (inventory['type'] == 'biosphere')]
        for _, row in bio_inputs.iterrows():
            emission = emissions_code_dict.get(str(row['code'])) or \
                       (find_emission(row['flow'], emissions_dict) or [None])[0]

            if not emission:
                print(f'Warning --- Emission not found: {row["flow"]}')
                continue

            if emission['unit'] != row['unit']:
                print(f'Warning --- Emission unit mismatch: expected {emission["unit"]}, got {row["unit"]}')
                sys.exit('Emission unit mismatch error')

            process_dict[key].new_exchange(
                input=emission.key, amount=row['value'], name=emission['name'],
                unit=emission['unit'], type='biosphere'
            ).save()
            process_dict[key].save()

        print(f'{time.time() - t0:.2f}s for biosphere connections to {key}')
