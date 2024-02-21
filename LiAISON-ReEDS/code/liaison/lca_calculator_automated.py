import sys
import pandas as pd
import uuid
import pickle
import numpy as np


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
        None
        """
    
        problems = {}
        p = []
        
        dic = {}
        dic2 = {}
        for i in ei_cf_36_db:
            
            try:
                p.append(dic[i['name']+'@'+i['location']])
                problems[i['name']+'@'+i['location']] = i
            except:
                 dic[i['name']+'@'+i['location']] = {}
                 dic2[i['name']+'@'+i['location']] = i
            
            
            dic[i['name']+'@'+i['location']][i['code']] = i


        '''    
        filehandler = open(db+".obj","wb")
        pickle.dump(dic,filehandler)
        filehandler.close()
        
        filehandler = open("problems.obj","wb")
        pickle.dump(problems,filehandler)
        filehandler.close()
        '''
        
        return dic,dic2

        
def search_index_reader(p_name,p_loc,database_dict):
    
        """
        This function returns the process based on key consisting of process name and location
        
        Parameters
        ----------
        p_name: str
            process name
            
        p_loc: str
            process location
             
        database_dict : 
            database dictionary ecoinvent search index with process information
        Returns
        -------
        None
        """

        key = p_name+'@'+p_loc
        return database_dict[key]
            
def search_index_debugger(database_dict,p_code):
    
        """
        This function debugs the search process for multiple process names and locations
        
        Parameters
        ----------          
        p_code: str
            code for identification of proper process when duplicate process names and location exists. 
             
        database_dict : 
            database dictionary ecoinvent search index with process information
            
        Returns
        -------
        None
        """

        if p_code == 0 or p_code == "0":
              if len(database_dict) == 1:
                for act in database_dict:
                    return database_dict[act]
                    break 
              else:
                print('\n  ******',flush = True)            
                print('Multiple processes exist for - ',flush = True)
                temp_choice = []
                for act in database_dict:
                    print(act,flush = True)
                    print(database_dict[act],flush = True)
                    
                    temp_choice.append(act)
                print('\n *****',flush = True)    
                print("Choose the first row by default to resolve the issue temporarily",flush = True)
                chosen_act = temp_choice[0]
                return database_dict[act]
   
        else:

            if len(p_code) == 33:
                p_code = p_code[1:]
            return database_dict[p_code]

def emission_merge(inp, emission_name_bridge):
    
            """
            This function matches common emission names with ecoinvent emission names.
            
            Parameters
            ----------
            inp : pd.DataFrame
               Dataframe for matching with ecoinvent bridge name databases
            
            emission_name_bridge : str
               filename for emissions name bridging csv             
                      
               
            Returns
            -------
            None
            """
            
            emission_name = pd.read_csv(emission_name_bridge)
            emission_bridge = inp.merge(emission_name, left_on = ['flow'], right_on = ['Common_name']).dropna()
            return emission_bridge

 
def merge(inp,process_name_bridge,location_name_bridge):
    
            """
            This function matches common process and location names with ecoinvent process and location names.
            
            Parameters
            ----------
            inp : pd.DataFrame
               Dataframe for matching with ecoinvent bridge name databases
            
            process_name_bridge : str
               filename for process name bridging csv             
            
            location_name_bridge : str
               filename for location name bridging csv            
               
            Returns
            -------
            None
            """
        
            process_name = pd.read_csv(process_name_bridge)
        
            location_name = pd.read_csv(location_name_bridge)

            process_bridge = inp.merge(process_name, left_on = ['flow'], right_on = ['Common_name']).dropna()
            
            location_bridge = inp.merge(location_name, left_on = ['supplying_location'], right_on = ['location_common']).dropna()

            return process_bridge,location_bridge      


#Not incorporated
def uncertainty_adder(eco_d,activity,exchg_name):
    yr = int(eco_d[10:14])
    for exchg in activity.exchanges():
        if exchg['name'] == exchg_name:
                exchg['uncertainty type'] = 2
                exchg['loc'] = np.log(exchg['amount'])
                exchg['scale'] = abs(np.log(exchg['amount']))/1000*(yr-2000)*5
                print('uncertainty added:'+str(exchg['loc'])+" - "+str(exchg['scale']))
                exchg.save()

        
def emissions_index_creator(bw):        
    biosphere = bw.Database('biosphere3')
    df_em = {}
    for i in biosphere:
       y = i.as_dict()
       df_em[y['code']] = i


    return df_em

def find_emission(emission_bridge,emissions_dict):

        if len(emission_bridge) == 1:
            print('One emission match found. Check passed!!')  
            code = emission_bridge['Ecoinvent_code'][0]
            return emissions_dict[code]

        else:
            print('Warning More than One emission match found. Choosing first match!!')  
            code = emission_bridge['Ecoinvent_code'][0]
            return emissions_dict[code]



def brightway(db,run_filename,mc_foreground_flag,mc_runs,process_name_bridge,emission_name_bridge,location_name_bridge,bw):

        """
        This function creates the process foreground within ecoinvent databases, every process activity, emissions and links 
        them to the background ecoinvent processes. Emissions are also linked to the processes and biosphere emissions.
        
        Parameters
        ----------
        db : str
           ecoinvent database with scenario and year 
           
        run_filename : str
           intermediate filename with process inventory
           
        mc_foreground_flag : boolean
           flag to perform monte carlo simulation
        
        process_name_bridge : str
           filename for process name bridging csv             
        
        location_name_bridge : str
           filename for location name bridging csv   
    
        eemission_name_bridge : str
           filename for emission name bridging csv
        
        bw : module
           brightway2 module        
           
        Returns
        -------
        None
        
        """
        
        
        ei_cf_36_db = bw.Database(db)
        database_dict,process_database_dict = search_index_creator(ei_cf_36_db)
      
        #CELL
        #Preprocessing
        print('Reading from ' + run_filename,flush = True)
        inventory = pd.read_csv(run_filename)
        
        
        #CELL
        #Step 1 is to create new processes or datasets    
        #The new processes and their information should be in the filtered product dataset
        processes = inventory[inventory['type'] == 'production']
        process_dict = {}
        print("Creating New activity")
        for index,row in processes.iterrows():
            
            
            #Getting proper_ecoinvent names

            process_info = row['process']
            location_info = row['process_location']


            try:
                    activity_dic = search_index_reader(db,process_info,location_info,database_dict)
                    activity = search_index_debugger(activity_dic,process_info)
                    if activity != None:
                        print('Deleting ' + process_info,flush = True)
                        activity.delete()
            except:
                pass
            print('Activity Created ' + process_info + ' at ' + location_info,flush = True)
            process_dict[process_info+'@'+location_info] = ei_cf_36_db.new_activity(code = uuid.uuid4(), name = process_info, unit = row['unit'], location = location_info)  
            process_dict[process_info+'@'+location_info].save()

        
        print('Creating Activity output flow') 

        for key in process_dict:

            process_dict[key].exchanges().delete()
            splited_key = key.split("@")
            process_key_name = splited_key[0]
            location_key_name = splited_key[1]
            inv = inventory[(inventory['process'] == process_key_name) & (inventory['process_location'] == location_key_name)]
            inp = inv[inv['type'] == 'production']
            if len(inp) == 1:
                print('Production flows check passed!!')
            elif len(inp) > 1:
                print('############Production flows for an activity more than 1!!##############')
            else:
                print('No production flows!!')


            for index,row in inp.iterrows():

                temp=pd.DataFrame([row])
                #Check for no matches 
                if temp.empty:
                    print('No production flow found in inventory',flush = True)
                    print(temp,flush = True)
            
                print(row['flow']+' Output flow created for ' + process_key_name + ' '+location_key_name,flush = True)
                process_dict[key].new_exchange(input = process_dict[key].key, name = row['flow'], amount = row['value'], unit = row['unit'],type = 'production', location = process_dict[key]['location']).save()
                process_dict[key].save()


        #Recreate the database dictionary so that the new created processes are listed in the inventory
        database_dict,process_database_dict = search_index_creator(ei_cf_36_db)
        
        #Step 3 is to define the flows that are inputs to the datasets
        #Only technosphere can be inputs 
        print('Technosphere input flows')     
        for key in process_dict:

            splited_key = key.split("@")
            process_key_name = splited_key[0]
            location_key_name = splited_key[1]
            inv = inventory[(inventory['process'] == process_key_name) & (inventory['process_location'] == location_key_name)]
            inp = inv[inv['type'] == 'technosphere']
            print('Creating technosphere exchanges for '+process_key_name+' at '+location_key_name)
            for index,row in inp.iterrows():

                temp=pd.DataFrame([row])
                process_bridge,location_bridge = merge(temp,process_name_bridge,location_name_bridge)
                
                if process_bridge.empty or location_bridge.empty:
                    print(row['flow'] + ' ' + row['supplying_location'],flush = True)
                    print('Did not find this process/location in the process bridge or location bridge file\n',flush = True)
                    #Some matches may not happen
                    #These will become cutoff flows
                else:

                    pcode = str(process_bridge['Ecoinvent_code'][0]).strip()
                    flag = 'activity found'
                    unit_error_flag = 0

                    
                    try :
                        activity_dic = search_index_reader(process_bridge['Ecoinvent_name'][0],location_bridge['location_ecoinvent'][0],database_dict)
                        activity = search_index_debugger(activity_dic,str(process_bridge['Ecoinvent_code'][0]).strip())    

                        if activity['unit'] != row['unit']:
                            print('UNIT ERROR '+location_bridge['location_ecoinvent'][0]+' for '+ process_bridge['Ecoinvent_name'][0])
                            unit_error_flag = 1                     
                        
                        process_dict[key].new_exchange(input=activity.key,amount=row['value'], name = activity['name'], location = activity['location'],unit=row['unit'],type='technosphere').save()
                        process_dict[key].save() 
                        print('Complete Success - Provided location '+ location_bridge['location_ecoinvent'][0]+' for '+ process_bridge['Ecoinvent_name'][0] +' was found. Chosen location was '+activity['location'] + ' . Chosen process was ' + activity['name'] ,flush = True)
                    
                    
                    except:
                        try:
                            #This exception is to make sure that if flows are not found the defaults of ROW or GLO or US-WECC are chosen for building the database
                            #The reason why three locations are used are because processes(like electricity) do not have RoW location but US-WECC is present.
                            activity_dic = search_index_reader(process_bridge['Ecoinvent_name'][0],'RNA',database_dict)
                            activity = search_index_debugger(activity_dic,process_bridge['Ecoinvent_code'][0])    
                            if activity['unit'] != row['unit']:
                                print('UNIT ERROR '+location_bridge['location_ecoinvent'][0]+' for '+ process_bridge['Ecoinvent_name'][0])
                                unit_error_flag = 1                          
                            
                            process_dict[key].new_exchange(input=activity.key,amount=row['value'], name = activity['name'], location = activity['location'],unit=row['unit'],type='technosphere').save()
                            process_dict[key].save() 
                            print('Minor Success - Provided location '+ location_bridge['location_ecoinvent'][0]+' for '+ process_bridge['Ecoinvent_name'][0] +' was not found. Shifting to ' + activity['name']+' ' + activity['location'],flush = True)

                            
                        except:
                            try:
                                #This exception is to make sure that if flows are not found the defaults of ROW or GLO or US-WECC are chosen for building the database
                                #The reason why three locations are used are because processes(like electricity) do not have RoW location but US-WECC is present.
                                activity_dic = search_index_reader(process_bridge['Ecoinvent_name'][0],'GLO',database_dict)
                                activity = search_index_debugger(activity_dic,process_bridge['Ecoinvent_code'][0])    
                                if activity['unit'] != row['unit']:
                                    print('UNIT ERROR '+location_bridge['location_ecoinvent'][0]+' for '+ process_bridge['Ecoinvent_name'][0])
                                    unit_error_flag = 1  
                                
                                process_dict[key].new_exchange(input=activity.key,amount=row['value'], name = activity['name'], location = activity['location'],unit=row['unit'],type='technosphere').save()
                                process_dict[key].save() 
                                print('Minor Success - Provided location '+ location_bridge['location_ecoinvent'][0]+' for '+ process_bridge['Ecoinvent_name'][0] +' was not found. Shifting to ' + activity['name']+' ' + activity['location'],flush = True)

                            except:
                                try:
                                    #This exception is to make sure that if flows are not found the defaults of ROW or GLO or US-WECC are chosen for building the database
                                    #The reason why three locations are used are because processes(like electricity) do not have RoW location but US-WECC is present.
                                    activity_dic = search_index_reader(process_bridge['Ecoinvent_name'][0],'RoW',database_dict)
                                    activity = search_index_debugger(activity_dic,process_bridge['Ecoinvent_code'][0])    
                                    if activity['unit'] != row['unit']:
                                        print('Unit error '+location_bridge['location_ecoinvent'][0]+' for '+ process_bridge['Ecoinvent_name'][0])
                                        unit_error_flag = 1  
                                    
                                    process_dict[key].new_exchange(input=activity.key,amount=row['value'], name = activity['name'], location = activity['location'],unit=row['unit'],type='technosphere').save()
                                    process_dict[key].save() 
                                    print('Minor Success - Provided location '+ location_bridge['location_ecoinvent'][0]+' for '+ activity['name'] +' was not found. Shifting to ' + activity['name']+' ' + activity['location'],flush = True)

                                except:                                   
                                         print('Failed - Not found '+process_bridge['Ecoinvent_name'][0] + ' ' + location_bridge['location_ecoinvent'][0] + ' '+str(process_bridge['Ecoinvent_code'][0]),flush = True)


                    if flag == 'activity found':
                        #Not implemented
                        mc_foreground = mc_foreground_flag
                        if mc_foreground:
                             uncertainty_adder(db,process_dict[key],activity['name'])
                             continue
            
                    if unit_error_flag == 1:
                        print('Correct unit should be '+activity['unit'])
                        sys.exit('Unit Error occured please check')
        

        
        print('Starting emissions')  

        emissions_dict = emissions_index_creator(bw)        
        
        for key in process_dict:
            
            splited_key = key.split("@")
            process_key_name = splited_key[0]
            location_key_name = splited_key[1]
            inv = inventory[(inventory['process'] == process_key_name) & (inventory['process_location'] == location_key_name)]
            print('Creating biosphere exchanges for '+process_key_name+' at '+location_key_name)
            inp = inv[inv['type'] == 'biosphere']
            for index,row in inp.iterrows():
                unit_error_flag = 0
                temp = inp[inp['flow'] == row['flow']]
                emission_bridge = emission_merge(temp, emission_name_bridge) 
                
                if emission_bridge.empty:
                    print(row['flow'] + ' Emission match not found from Emission Bridge!!')
                else:
                    emission = find_emission(emission_bridge,emissions_dict)
                    
                    if emission == None:
                        print('Emission not found ' + row['flow'],flush = True)                
                    else:
                        if emission['unit'] != row['unit']:
                            print('Emission unit error'+row['supplying_location']+' for '+ emission_bridge['Ecoinvent_name'][0])
                            unit_error_flag = 1   
                        else:                                       
                            process_dict[key].new_exchange(input=emission.key,amount=row['value'], name = emission['name'],unit=emission['unit'],type='biosphere').save()
                            process_dict[key].save() 
                            print(emission['name']+' '+emission['unit']+' found and added to as a biosphere exchange with amount '+str(row['value']),flush=True)
                    
                    if unit_error_flag == 1:
                            print('Correct unit should be '+emission['unit'])
                            sys.exit('Emission unit Error occured please check')        


        database_dict,process_database_dict = search_index_creator(ei_cf_36_db)
        return process_database_dict
        

def lcia_traci_run(db,primary_process,functional_unit,mc_foreground_flag,mc_runs,bw):
    
        """
        This function performs the LCA and LCIA calculations with the TRACI method.
        
        Parameters
        ----------
        db : pd.DataFrame
           Dataframe for matching with ecoinvent bridge name databases
        
        primary_process : ecoinvent process
           Ecoinvent process with the primary process under LCA study         
                        
        
        functional unit : str
           filename for location name bridging csv            
           
        Returns
        -------
        None
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


    
        operation = primary_process
      
        
        operation_functional_unit = {operation:functional_unit}
        
        operation_result = []
        
        from collections import defaultdict
        LCA_sol_cal_dict = defaultdict(dict)
        
        LCA_sol_cal_dict['hydrogen'+str(db)] = {'functional unit' : operation_functional_unit, 'result': operation_result}
        

        mc = mc_foreground_flag
        if mc:
         for key in LCA_sol_cal_dict.keys():
            for method in method_key:
                    mc = bw.MonteCarloLCA(demand=operation_functional_unit, method=method)
                    mc_results = [next(mc) for _ in range(mc_runs)]#Obsolete Code. Needs to updated
                    LCA_sol_cal_dict[key]['result'].append((method[2].title(), mc_results , bw.methods.get(method).get('unit')))
        
        else:
         for key in LCA_sol_cal_dict.keys():
            lca = bw.LCA(LCA_sol_cal_dict[key]['functional unit'])
            lca.lci()
            
            for method in method_key:
                lca.switch_method(method)
                lca.lcia()
                LCA_sol_cal_dict[key]['result'].append((method[2].title(), lca.score, bw.methods.get(method).get('unit')))
                #print('TOP ACTIVITIES\n\n')
                #print(lca.top_activities())
                #print('TOP EMISSIONS\n\n')
                #print(lca.top_emissions())                 

                
        return LCA_sol_cal_dict,len(method_key)

def lcia_recipe_run(db,primary_process,functional_unit,mc_foreground_flag,mc_runs,bw):

        method_key = [[m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'agricultural land occupation' in str(m)][0],
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
                      [m for m in bw.methods if 'ReCiPe Midpoint (H)' in str(m) and 'water depletion' in str(m)][0]]


    
        operation = primary_process
        
        operation_functional_unit = {operation:functional_unit}
        
        operation_result = []
        
        from collections import defaultdict
        LCA_sol_cal_dict = defaultdict(dict)
        
        LCA_sol_cal_dict['hydrogen'+str(db)] = {'functional unit' : operation_functional_unit, 'result': operation_result}
        

        mc = mc_foreground_flag
        if mc:
         for key in LCA_sol_cal_dict.keys():
            for method in method_key:

                    mc = bw.MonteCarloLCA(demand=operation_functional_unit, method=method)
                    mc_results = [next(mc) for _ in range(mc_runs)]#Obsolete Code. Needs to updated
                    LCA_sol_cal_dict[key]['result'].append((method[2].title(), mc_results , bw.methods.get(method).get('unit')))
        
        
        else:
         for key in LCA_sol_cal_dict.keys():
            lca = bw.LCA(LCA_sol_cal_dict[key]['functional unit'])
            lca.lci()

            
            for method in method_key:
                lca.switch_method(method)
                lca.lcia()


                LCA_sol_cal_dict[key]['result'].append((method[2].title(), lca.score, bw.methods.get(method).get('unit')))
                #print('TOP ACTIVITIES\n\n')
                #print(lca.top_activities())
                #print('TOP EMISSIONS\n\n')
                #print(lca.top_emissions())                  


                
        return LCA_sol_cal_dict,len(method_key)


def lcia_premise_gwp_run(db,primary_process,functional_unit,mc_foreground_flag,mc_runs,bw):

        method_key = [[m for m in bw.methods if 'IPCC 2013' in str(m) and 'GTP 100a, incl. bio CO2' in str(m)][0],
                      [m for m in bw.methods if 'IPCC 2013' in str(m) and 'GWP 100a, incl. H' in str(m)][0],
                      [m for m in bw.methods if 'IPCC 2013' in str(m) and 'GWP 100a, incl. H' in str(m)][1],
                      [m for m in bw.methods if 'IPCC 2013' in str(m) and 'GWP 100a, incl. H and bio CO2' in str(m)][0]]
    
        operation = primary_process
        
        operation_functional_unit = {operation:functional_unit}
        
        operation_result = []
        
        from collections import defaultdict
        LCA_sol_cal_dict = defaultdict(dict)
        
        LCA_sol_cal_dict['hydrogen'+str(db)] = {'functional unit' : operation_functional_unit, 'result': operation_result}
        

        mc = mc_foreground_flag
        if mc:
         for key in LCA_sol_cal_dict.keys():
            for method in method_key:
                    print(method)
                    mc = bw.MonteCarloLCA(demand=operation_functional_unit, method=method)
                    mc_results = [next(mc) for _ in range(mc_runs)]#Obsolete Code. Needs to updated
                    LCA_sol_cal_dict[key]['result'].append((method[2].title(), mc_results , bw.methods.get(method).get('unit')))
        
        
        else:
         for key in LCA_sol_cal_dict.keys():
            lca = bw.LCA(LCA_sol_cal_dict[key]['functional unit'])
            lca.lci()
            
            for method in method_key:
                lca.switch_method(method)
                lca.lcia()
                LCA_sol_cal_dict[key]['result'].append((method[2].title(), lca.score, bw.methods.get(method).get('unit')))
                #print('TOP ACTIVITIES\n\n')
                #print(lca.top_activities())
                #print('TOP EMISSIONS\n\n')
                #print(lca.top_emissions())                

        save_db = False
        if save_db == True:
            ei_cf_36_db = bw.Database(db)    
            ei_cf_36_db.backup()
            print('backed up database')

                
        return LCA_sol_cal_dict,len(method_key)
