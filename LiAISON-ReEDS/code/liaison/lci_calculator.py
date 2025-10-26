import sys
import pandas as pd
import uuid
import pickle
import numpy as np
import time


def search_index_creator(ei_cf_36_db):
    
        """
        This function creates a search index dictionary storing the name and location of processes as the key 
        and the process itself as the information within the key
        
        Parameters
        ----------       
        ei_cf_36_db : ecoinvent database
            database ecoinvent     
        Returns
        -------
        dic: dictionary
            ecoinvent database in the form of a dictionary
        """
    
        problems = {}
        p = []
        
        dic = {}
        dic2 = {}
        for i in ei_cf_36_db:
            
            try:
                p.append(dic[i['name']+'@'+i['location']+'@'+i['unit']])
                problems[i['name']+'@'+i['location']+'@'+i['unit']] = i
            except:
                 dic[i['name']+'@'+i['location']+'@'+i['unit']] = {}
                 #dic2[i['name']+'@'+i['location']+'@'+i['unit']] = i
            
            
            
            dic[i['name']+'@'+i['location']+'@'+i['unit']][i['code']] = i
            dic2[i['code']] = i
        
        return dic,dic2

        
def search_index_reader(p_name,p_loc,p_unit,data_dict):
    
        """
        This function returns the process based on key consisting of process name and location
        
        Parameters
        ----------
        p_name: str
            process name
            
        p_loc: str
            process location

        p_unit: str
            process unit
             
        database_dict : 
            database dictionary ecoinvent search index with process information
        Returns
        -------
        None
        """

        dic_key = p_name+'@'+p_loc +'@'+p_unit

        activity_dict = data_dict[dic_key]
        if len(activity_dict) == 1:
            for key in activity_dict.keys():
                return activity_dict[key]

        else:
            print('\nINFO: Process dictionary length when '+dic_key+' is chosen is '+str(len(activity_dict)),flush=True)
            for key in activity_dict.keys():
                print('INFO Multiple activities found ---- ',activity_dict[key],key,flush=True)
            print('\n')
            return activity_dict[key]


        
def emissions_index_creator(bw):  
    """
    This function debugs create the dictionary for emissions
    
    Parameters
    ----------          
    bw: package
        
    Returns
    -------
    df_em: dictionary
        Emissions dictionary from ecoinvent
    """
   
    biosphere = bw.Database('biosphere3')
    df_em = {}
    df_em2 = {}

    # There may be several emissions with the same name. For that case, we store all occurences within the name key as a list. 
    for i in biosphere:
       y = i.as_dict()   

       try:
            a = df_em[y['name']]
            df_em[y['name']].append(i)

       except:
            df_em[y['name']] = [i]    

       df_em2[y['code']] = i
    
    return df_em,df_em2

def find_emission(emission_name, emissions_dict):
        """
        Retrieve emissions list by name from emissions dictionary.

        Parameters
        ----------
        emission_name : str
            Name of the emission to look up.
        emissions_dict : dict
            Dictionary from `emissions_index_creator`.

        Returns
        -------
        list or None
            List of matching flows, or None if not found.
        """
        try:
            return emissions_dict[emission_name]
        except KeyError:
            return None


def search_dictionary(db,bw):

        """
        This function creates the process foreground within ecoinvent databases, every process activity, emissions and links 
        them to the background ecoinvent processes. Emissions are also linked to the processes and biosphere emissions.
        
        Parameters
        ----------
        db : str
           ecoinvent database with scenario and year 
        
        bw : module
           brightway2 module        
           
        Returns
        -------
        None
        
        """
        ei_cf_36_db = bw.Database(db)
        database_dict,database_dict_secondary = search_index_creator(ei_cf_36_db)
        return database_dict

def liaison_calc(db,run_filename,bw):

        """
        This function creates the process foreground within ecoinvent databases, every process activity, emissions and links 
        them to the background ecoinvent processes. Emissions are also linked to the processes and biosphere emissions.
        
        Parameters
        ----------
        db : str
           ecoinvent database with scenario and year 
           
        run_filename : str
           intermediate filename with process inventory
        
        bw : module
           brightway2 module        
           
        Returns
        -------
        None
        
        """ 
        ei_cf_36_db = bw.Database(db)
        print('creating inventory withing the database---',db,flush=True)
        database_dict,database_dict_secondary = search_index_creator(ei_cf_36_db)
        
        if isinstance(run_filename, str):
            inventory = pd.read_csv(run_filename)
        else:
            inventory = run_filename

        inventory = inventory.sort_values(by=['process', 'process_location'])
      
        
        inventory = run_filename.sort_values(by=['process','process_location'])   
        # Step 1 is to create new processes or datasets    
        # The new processes and their information should be in the filtered product dataset
        processes = inventory[inventory['type'] == 'production']
        process_dict = {}
        print("Creating New activity")
        for index,row in processes.iterrows():
            
            # Reading the process name from the csv file and the location. 
            process_info = row['process']
            location_info = row['process_location']
            unit_info = row['unit']

            # Here we use the process name, the location name and the unit to find the exact entry in ecoinvent. It may or may not exist
            # Assumption is that process_name@location_name@unit is unique. 
            # Deleting the activity that was found. 
            try:
                 activity = search_index_reader(process_info,location_info,unit_info,database_dict)
                 activity.exchanges().delete()
                 print('Found existing activity ', process_info,location_info,unit_info,flush = True)
                 process_dict[process_info+'@'+location_info] = activity
                 # print('Removing Activity flows',flush=True) 

                 for key in process_dict:
                    for exch in process_dict[key].exchanges():
                            print('Deleting',exch['name'])
                            exch.delete()

                 process_dict[key].save()

            except:

                print('Activity Created ' + process_info + ' at ' + location_info,flush = True)
                process_dict[process_info+'@'+location_info] = ei_cf_36_db.new_activity(code = uuid.uuid4(), name = process_info, unit = row['unit'], location = location_info)  
                process_dict[process_info+'@'+location_info].save()

        
        print('Creating Activity output flow') 
        # Now that we have created the processes form the input inventory, we need to add output flows to those inventories.
        for key in process_dict:

            # Deleting all the flows of the created activity if it exists. 
            process_dict[key].exchanges().delete()
            splited_key = key.split("@")
            process_key_name = splited_key[0]
            location_key_name = splited_key[1]
            #unit_key_name = splited_key[2]

            # For the activities which have been created in ecoinvent, we are now searching for the corressponding output flow name
            # so that they can be added to the exchange information. We need to make sure we choose the right output flow. So we are choosing
            # by filtering on the three unique components that make every process unique. 
            # inv = inventory[(inventory['process'] == process_key_name) & (inventory['process_location'] == location_key_name) & (inventory['unit'] == unit_key_name)]
            inv = inventory[(inventory['process'] == process_key_name) & (inventory['process_location'] == location_key_name)]
            inp = inv[inv['type'] == 'production']
            if len(inp) == 1:
                pass
            elif len(inp) > 1:
                print(' Warning --- Production flows for an activity more than 1!')
            else:
                print('Warning --- No production flows!!')

            for index,row in inp.iterrows():

                temp=pd.DataFrame([row])
                #Check for production flow
                if temp.empty:
                    print('Warning --- No production flow found in inventory',flush = True)
                    print(temp,flush = True)
            
                print(row['flow']+' Output flow created for ' + process_key_name + ' '+location_key_name,flush = True)
                process_dict[key].new_exchange(input = process_dict[key].key, name = row['flow'], amount = row['value'], unit = row['unit'],type = 'production', location = process_dict[key]['location']).save()
                process_dict[key]['reference product'] = row['flow']
                process_dict[key]['production amount'] = row['value']
                process_dict[key]['unit'] = row['unit']
                process_dict[key].save()

        #Recreate the database dictionary so that the new created processes are listed in the inventory
        database_dict,database_dict_secondary = search_index_creator(ei_cf_36_db)
        
        # Step 3 is to define the flows that are inputs to the datasets
        # Only technosphere can be inputs 
        print('Technosphere input flows')     
        for key in process_dict:

            time0=time.time()

            splited_key = key.split("@")
            process_key_name = splited_key[0]
            location_key_name = splited_key[1]
            # Here we first choose a certain process in the process dictionary that we are explicitly creating in LiAISON
            # Once we choose that, we select that chosen process form our user provided inventory file and start adding the technosphere flows and then the biosphere flows.
            inv = inventory[(inventory['process'] == process_key_name) & (inventory['process_location'] == location_key_name)]
            inp = inv[inv['type'] == 'technosphere']
            print('Creating technosphere exchanges for '+process_key_name+' at '+location_key_name)
            for index,row in inp.iterrows():
                
                    unit_error_flag = 0
                    not_found = False
                    print_flag = False
                    activity = None
                    # Then the UUID has been supplied and we can try to find using UUID
                    try:
                        activity = database_dict_secondary(row['code'])
                        print('UUID matched - Provided location '+ row['supplying_location']+' for '+ row['flow'] +' was found. Chosen location was '+activity['location'] + ' . Chosen process was ' + activity['name'] ,flush = True)
                        print_flag = True
                    except:
                        # This exception is to make sure that if flows are not found for the user provided location, other locations are searched for and linked automatically. 
                        try :
                            activity = search_index_reader(row['flow'],row['supplying_location'],row['unit'],database_dict)
                            print('Search Success - Provided location '+ row['supplying_location']+' for '+ row['flow'] +' was found. Chosen location was '+activity['location'] + ' . Chosen process was ' + activity['name'] ,flush = True)
                            print_flag = True
                        except:
                            try:
                                activity = search_index_reader(row['flow'],'USA',row['unit'],database_dict)
                            except:
                                try:
                                    activity = search_index_reader(row['flow'],'US',row['unit'],database_dict)
                                except:
                                    try:
                                        activity = search_index_reader(row['flow'],'RNA',row['unit'],database_dict)
                                    except:
                                        try:
                                            activity = search_index_reader(row['flow'],'RoW',row['unit'],database_dict)
                                        except: 
                                            try:
                                                activity = search_index_reader(row['flow'],'GLO',row['unit'],database_dict)
                                            except:
                                                try:
                                                    activity = search_index_reader(row['flow'],'RER',row['unit'],database_dict)
                                                except:
                                                    print('Warning --- Failed - Not found '+row['flow'] + ' ' + row['supplying_location'] + ' ',flush = True)
                                                    print_flag = True
                                                    not_found = True
                        if print_flag == False:
                            print('Minor Success - Provided location '+ row['supplying_location']+' for '+ row['flow'] +' was not found. Shifting to ' + activity['name']+' ' + activity['location'],flush = True)

                    if not_found == False:

                        if activity['unit'] != row['unit']:
                            print('Warning --- UNIT ERROR '+row['supplying_location']+' for '+ row['flow'])
                            print('Warning --- Correct unit should be '+activity['unit'])
                            sys.exit('Warning --- Unit Error occured please check')

                        else:
                            process_dict[key].new_exchange(input=activity.key,amount=row['value'], name = activity['name'], location = activity['location'],unit=activity['unit'],type='technosphere').save()
                            process_dict[key].save() 
            
            print(str(time.time()-time0),' seconds needed for technosphere flows connection for process ', key)
            print('')
            print('')

        print('Adding Biosphere Flows',flush = True)  
        emissions_dict,emissions_code_dict = emissions_index_creator(bw)        
        for key in process_dict:
            time0=time.time()
            splited_key = key.split("@")
            process_key_name = splited_key[0]
            location_key_name = splited_key[1]
            inv = inventory[(inventory['process'] == process_key_name) & (inventory['process_location'] == location_key_name)]
            print('Creating biosphere exchanges for '+process_key_name+' at '+location_key_name,flush = True)
            inp = inv[inv['type'] == 'biosphere']
            for index,row in inp.iterrows():
                unit_error_flag = 0
                temp=pd.DataFrame([row])

                # Try find the emission using supplied UUID. If not then try name. Emission should be a list
                try:
                    emission =[emissions_code_dict[str(row['code'])]]
                except:
                    emission = find_emission(row['flow'],emissions_dict)
                
                if emission == None:
                    print('Warning --- Emission not found ' + row['flow'],flush = True)                
                else:
                    # All emissions matching a certain user provided emission name is stored as a list in the emission dictionary
                    # If multiple emissions match the list is more than 1. 
                    # We need to choose one, so we choose one of them
                    chosen_emission = emission[0]
                    
                    if len(emission) > 1:
                        # if greater than 1 we display this message
                        print("Issue:in Multiple emissions matched for ",row['flow']," but chosen emission was ",chosen_emission['name']," ",chosen_emission['categories'],flush = True)

                    else:
                        pass

                    if chosen_emission['unit'] != row['unit']:
                        print('Warning --- Emission unit error'+row['supplying_location']+' for '+ emission_bridge['Ecoinvent_name'][0],flush = True)
                        unit_error_flag = 1   
                    else:                                       
                        process_dict[key].new_exchange(input=chosen_emission.key,amount=row['value'], name = chosen_emission['name'],unit=chosen_emission['unit'],type='biosphere').save()
                        process_dict[key].save() 
                        #print(emission['name']+' '+emission['unit']+' found and added to as a biosphere exchange with amount '+str(row['value']),flush=True)
                    
                if unit_error_flag == 1:
                        print('Warning --- Correct unit should be '+chosen_emission['unit'])
                        sys.exit('Warning --- Emission unit Error occured please check',flush = True)        

 
            print(key)
            print(str(time.time()-time0),' seconds needed for biosphere flows connection for process ', key)
            print('')
            print('')


        database_dict,database_dict_secondary = search_index_creator(ei_cf_36_db)
        return database_dict

        
def lcia_traci_run(db, primary_process, functional_unit, mc_foreground_flag, mc_runs, bw):
    """
    Perform LCA and LCIA calculations using the TRACI midpoint methods.

    Parameters
    ----------
    db : any
        Identifier for the study, used as a key in the results.
    primary_process : Activity or dict
        Brightway2 process or demand mapping for the primary process.
    functional_unit : float or dict
        Functional unit for the demand (amount or mapping).
    mc_foreground_flag : bool
        If True, perform Monte Carlo on the foreground; otherwise, deterministic LCA.
    mc_runs : int
        Number of Monte Carlo iterations if mc_foreground_flag is True.
    bw : module
        The Brightway2 module.

    Returns
    -------
    tuple
        - results_dict : dict
            Mapping of study → {'functional unit': {...}, 'result': [...]}
        - n_methods : int
            Number of TRACI methods applied.
    """
    method_key = [
        [m for m in bw.methods if 'TRACI' in str(m) and 'acidification' in str(m)][0],
        [m for m in bw.methods if 'TRACI' in str(m) and 'ecotoxicity' in str(m)][0],
        [m for m in bw.methods if 'TRACI' in str(m) and 'eutrophication' in str(m)][0],
        [m for m in bw.methods if 'TRACI' in str(m) and 'global warming' in str(m)][0],
        [m for m in bw.methods if 'TRACI' in str(m) and 'carcinogenics' in str(m)][1],
        [m for m in bw.methods if 'TRACI' in str(m) and 'ozone depletion' in str(m)][0],
        [m for m in bw.methods if 'TRACI' in str(m) and 'photochemical oxidation' in str(m)][0],
        [m for m in bw.methods if 'TRACI' in str(m) and 'non-carcinogenics' in str(m)][0],
        [m for m in bw.methods if 'TRACI' in str(m) and 'respiratory effects, average' in str(m)][0]
    ]

    operation = primary_process
    operation_functional_unit = {operation: functional_unit}
    operation_result = []

    from collections import defaultdict
    LCA_sol_cal_dict = defaultdict(dict)
    LCA_sol_cal_dict['hydrogen' + str(db)] = {
        'functional unit': operation_functional_unit,
        'result': operation_result
    }

    if mc_foreground_flag:
        for key in LCA_sol_cal_dict:
            for method in method_key:
                mc = bw.MonteCarloLCA(demand=operation_functional_unit, method=method)
                mc_results = [next(mc) for _ in range(mc_runs)]
                LCA_sol_cal_dict[key]['result'].append(
                    (method[2].title(), mc_results, bw.methods.get(method).get('unit'))
                )
    else:
        for key in LCA_sol_cal_dict:
            lca = bw.LCA(LCA_sol_cal_dict[key]['functional unit'])
            lca.lci()
            for method in method_key:
                lca.switch_method(method)
                lca.lcia()
                LCA_sol_cal_dict[key]['result'].append(
                    (method[2].title(), lca.score, bw.methods.get(method).get('unit'))
                )

    return LCA_sol_cal_dict, len(method_key)


def lcia_recipe_run(db, primary_process, functional_unit, mc_foreground_flag, mc_runs, bw):
    """
    Perform LCA and LCIA calculations using ReCiPe Midpoint (H) methods.

    Parameters
    ----------
    db : any
        Identifier for the study.
    primary_process : Activity or dict
        Brightway2 process or demand mapping for the primary process.
    functional_unit : float or dict
        Functional unit for the demand.
    mc_foreground_flag : bool
        If True, perform Monte Carlo on the foreground; otherwise, deterministic LCA.
    mc_runs : int
        Number of Monte Carlo iterations if mc_foreground_flag is True.
    bw : module
        The Brightway2 module.

    Returns
    -------
    tuple
        - results_dict : dict
            Mapping of study → {'functional unit': {...}, 'result': [...]}
        - n_methods : int
            Number of ReCiPe methods applied.
    """
    method_key = [
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'agricultural land occupation' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'climate change' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'fossil depletion' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'freshwater ecotoxicity' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'freshwater eutrophication' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'human toxicity' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'ionising radiation' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'marine ecotoxicity' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'marine eutrophication' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'metal depletion' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'natural land transformation' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'ozone depletion' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'particulate matter formation' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'photochemical oxidant formation' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'terrestrial acidification' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'terrestrial ecotoxicity' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'urban land occupation' in str(m)][0],
        [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'water depletion' in str(m)][0]
    ]

    operation = primary_process
    operation_functional_unit = {operation: functional_unit}
    operation_result = []

    from collections import defaultdict
    LCA_sol_cal_dict = defaultdict(dict)
    LCA_sol_cal_dict['hydrogen' + str(db)] = {
        'functional unit': operation_functional_unit,
        'result': operation_result
    }

    if mc_foreground_flag:
        for key in LCA_sol_cal_dict:
            for method in method_key:
                mc = bw.MonteCarloLCA(demand=operation_functional_unit, method=method)
                mc_results = [next(mc) for _ in range(mc_runs)]
                LCA_sol_cal_dict[key]['result'].append(
                    (method[2].title(), mc_results, bw.methods.get(method).get('unit'))
                )
    else:
        for key in LCA_sol_cal_dict:
            lca = bw.LCA(LCA_sol_cal_dict[key]['functional unit'])
            lca.lci()
            for method in method_key:
                lca.switch_method(method)
                lca.lcia()
                LCA_sol_cal_dict[key]['result'].append(
                    (method[2].title(), lca.score, bw.methods.get(method).get('unit'))
                )

    return LCA_sol_cal_dict, len(method_key)


def lcia_premise_gwp_run(db, primary_process, functional_unit, mc_foreground_flag, mc_runs, bw):
    """
    Perform LCA and LCIA using IPCC 2013 GWP/GTP methods via PREMISE.

    Parameters
    ----------
    db : any
        Identifier for the study.
    primary_process : Activity or dict
        Brightway2 process or demand mapping for the primary process.
    functional_unit : float or dict
        Functional unit for the demand.
    mc_foreground_flag : bool
        If True, perform Monte Carlo on the foreground; otherwise, deterministic LCA.
    mc_runs : int
        Number of Monte Carlo iterations if mc_foreground_flag is True.
    bw : module
        The Brightway2 module.

    Returns
    -------
    tuple
        - results_dict : dict
            Mapping of study → {'functional unit': {...}, 'result': [...]}
        - n_methods : int
            Number of IPCC methods applied.
    """
    method_key = [
        [m for m in bw.methods if 'IPCC 2013' in str(m) and 'GTP 100a, incl. bio CO2' in str(m)][0],
        [m for m in bw.methods if 'IPCC 2013' in str(m) and 'GWP 100a, incl. H' in str(m)][0],
        [m for m in bw.methods if 'IPCC 2013' in str(m) and 'GWP 100a, incl. H' in str(m)][1],
        [m for m in bw.methods if 'IPCC 2013' in str(m) and 'GWP 100a, incl. H and bio CO2' in str(m)][0]
    ]

    from collections import defaultdict
    LCA_sol_cal_dict = defaultdict(dict)
    LCA_sol_cal_dict['hydrogen' + str(db)] = {
        'functional unit': {primary_process: functional_unit},
        'result': []
    }

    if mc_foreground_flag:
        for key in LCA_sol_cal_dict:
            for method in method_key:
                mc = bw.MonteCarloLCA(demand={primary_process: functional_unit}, method=method)
                mc_results = [next(mc) for _ in range(mc_runs)]
                LCA_sol_cal_dict[key]['result'].append(
                    (method[2].title(), mc_results, bw.methods.get(method).get('unit'))
                )
    else:
        for key in LCA_sol_cal_dict:
            lca = bw.LCA({primary_process: functional_unit})
            lca.lci()
            for method in method_key:
                lca.switch_method(method)
                lca.lcia()
                LCA_sol_cal_dict[key]['result'].append(
                    (method[2].title(), lca.score, bw.methods.get(method).get('unit'))
                )

    return LCA_sol_cal_dict, len(method_key)
