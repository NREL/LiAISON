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
        for i in ei_cf_36_db:
            
            try:
                p.append(dic[i['name']+'@'+i['location']])
                problems[i['name']+'@'+i['location']] = i
            except:
                 dic[i['name']+'@'+i['location']] = {}
            
            
            dic[i['name']+'@'+i['location']][i['code']] = i



        '''    
        filehandler = open(db+".obj","wb")
        pickle.dump(dic,filehandler)
        filehandler.close()
        
        filehandler = open("problems.obj","wb")
        pickle.dump(problems,filehandler)
        filehandler.close()
        '''
        
        return dic

        
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
            emission_bridge = inp.merge(emission_name, left_on = ['flow','comments'], right_on = ['Common_name','Common_source']).dropna()
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

def reeds_lci_modifier(db,run_filename,process_name_bridge,emission_name_bridge,location_name_bridge,bw):

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
        database_dict = search_index_creator(ei_cf_36_db)
      
        #CELL
        #Preprocessing
        print('Reading from ' + run_filename,flush = True)
        inventory = pd.read_csv(run_filename)


  
        #CELL
        #Step 1 is to create new processes or datasets    
        #The new processes and their information should be in the filtered product dataset
        processes = inventory[inventory['type'] == 'production']
        process_dict = {}
        print("Modifying activity")
        for index,row in processes.iterrows():
            
            
            #Getting proper_ecoinvent names
            process_info = row['process']
            location_info = row['process_location']
            print(process_info,location_info)


            activity_dic = search_index_reader(process_info,location_info,database_dict)
            if len(activity_dic) == 1:
                print('One activity found. Check passed')
            else:
                print('Warning: Multiple activity found')
            p_code = list(activity_dic.keys())
            activity = search_index_debugger(activity_dic,p_code[0].strip())
            
            if activity != None:
                print('Activity Found!!',flush=True)

            process_dict[process_info+'@'+location_info] = activity

            #print('Activity Created ' + process_info + ' at ' + location_info,flush = True)
            #process_dict[process_info+'@'+location_info] = ei_cf_36_db.new_activity(code = uuid.uuid4(), name = process_info, unit = row['unit'], location = location_info)  
            #process_dict[process_info+'@'+location_info].save()

        
        print('Removing Activity technosphere flow') 

        for key in process_dict:
            for exch in process_dict[key].exchanges():
                if exch['type'] == 'technosphere':
                    exch.delete()

            process_dict[key].save()

        for key in process_dict:
            for exch in process_dict[key].exchanges():
                print(exch)

        #Recreate the database dictionary so that the new created processes are listed in the inventory
        database_dict = search_index_creator(ei_cf_36_db)
        
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
                    print('Warning Failed: Did not find this activity in the bridge file\n',flush = True)
                    #Some matches may not happen
                    #These will become cutoff flows
                else:

                    unit_error_flag = 0

                    
                    try :
                        activity_dic = search_index_reader(process_bridge['Ecoinvent_name'][0],location_bridge['location_ecoinvent'][0],database_dict)
                        activity = search_index_debugger(activity_dic,str(process_bridge['Ecoinvent_code'][0]).strip())    

                        if activity['unit'] != row['unit']:
                            print('Warning Failed UNIT ERROR '+location_bridge['location_ecoinvent'][0]+' for '+ process_bridge['Common_name'][0])
                            unit_error_flag = 1                     
                        
                        process_dict[key].new_exchange(input=activity.key,amount=row['value'], name = activity['name'], location = activity['location'],unit=row['unit'],type='technosphere').save()
                        process_dict[key].save() 
                        print('Complete Success - Provided location '+ location_bridge['location_ecoinvent'][0]+' for '+ process_bridge['Common_name'][0] +' was found. Chosen location was '+activity['location'] + ' . Chosen process was ' + activity['name'] ,flush = True)
                    
                    
                    except:
                        try:
                            #This exception is to make sure that if flows are not found the defaults of ROW or GLO or US-WECC are chosen for building the database
                            #The reason why three locations are used are because processes(like electricity) do not have RoW location but US-WECC is present.
                            activity_dic = search_index_reader(process_bridge['Ecoinvent_name'][0],'RNA',database_dict)
                            activity = search_index_debugger(activity_dic,process_bridge['Ecoinvent_code'][0])    
                            if activity['unit'] != row['unit']:
                                print('Warning Failed UNIT ERROR '+location_bridge['location_ecoinvent'][0]+' for '+ process_bridge['Common_name'][0])
                                unit_error_flag = 1                          
                            
                            process_dict[key].new_exchange(input=activity.key,amount=row['value'], name = activity['name'], location = activity['location'],unit=row['unit'],type='technosphere').save()
                            process_dict[key].save() 
                            print('Minor Success - Provided location '+ location_bridge['location_ecoinvent'][0]+' for '+ process_bridge['Common_name'][0] +' was not found. Shifting to ' + activity['name']+' ' + activity['location'],flush = True)

                            
                        except:
                            try:
                                #This exception is to make sure that if flows are not found the defaults of ROW or GLO or US-WECC are chosen for building the database
                                #The reason why three locations are used are because processes(like electricity) do not have RoW location but US-WECC is present.
                                activity_dic = search_index_reader(process_bridge['Ecoinvent_name'][0],'GLO',database_dict)
                                activity = search_index_debugger(activity_dic,process_bridge['Ecoinvent_code'][0])    
                                if activity['unit'] != row['unit']:
                                    print('Warning Failed UNIT ERROR '+location_bridge['location_ecoinvent'][0]+' for '+ process_bridge['Common_name'][0])
                                    unit_error_flag = 1  
                                
                                process_dict[key].new_exchange(input=activity.key,amount=row['value'], name = activity['name'], location = activity['location'],unit=row['unit'],type='technosphere').save()
                                process_dict[key].save() 
                                print('Minor Success - Provided location '+ location_bridge['location_ecoinvent'][0]+' for '+ process_bridge['Common_name'][0] +' was not found. Shifting to ' + activity['name']+' ' + activity['location'],flush = True)

                            except:
                                try:
                                    #This exception is to make sure that if flows are not found the defaults of ROW or GLO or US-WECC are chosen for building the database
                                    #The reason why three locations are used are because processes(like electricity) do not have RoW location but US-WECC is present.
                                    activity_dic = search_index_reader(process_bridge['Ecoinvent_name'][0],'RoW',database_dict)
                                    activity = search_index_debugger(activity_dic,process_bridge['Ecoinvent_code'][0])    
                                    if activity['unit'] != row['unit']:
                                        print('Warning Failed Unit error '+location_bridge['location_ecoinvent'][0]+' for '+ process_bridge['Common_name'][0])
                                        unit_error_flag = 1  
                                    
                                    process_dict[key].new_exchange(input=activity.key,amount=row['value'], name = activity['name'], location = activity['location'],unit=row['unit'],type='technosphere').save()
                                    process_dict[key].save() 
                                    print('Minor Success - Provided location '+ location_bridge['location_ecoinvent'][0]+' for '+ activity['name'] +' was not found. Shifting to ' + activity['name']+' ' + activity['location'],flush = True)

                                except:                                   
                                         print('Warning Failed - Not found '+process_bridge['Common_name'][0] + ' ' + location_bridge['location_ecoinvent'][0] + ' '+str(process_bridge['Ecoinvent_code'][0]),flush = True)

            
                    if unit_error_flag == 1:
                        print('Correct unit should be '+activity['unit'])
                        sys.exit('Warning Failed Unit Error occured please check')
        

        
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
                    print(row['flow'] + ' Warning Failed Emission match not found from Emission Bridge!!')
                
                else:
                    emission = find_emission(emission_bridge,emissions_dict)
                    if emission == None:
                        print('Warning Failed Emission not found ' + row['flow'],flush = True)                
                    else:
                        if emission['unit'] != row['unit']:
                            print('Warning Failed Emission unit error'+row['supplying_location']+' for '+ emission_bridge['Ecoinvent_name'][0])
                            unit_error_flag = 1   
                        else:                                       
                            process_dict[key].new_exchange(input=emission.key,amount=row['value'], name = emission['name'],unit=emission['unit'],type='biosphere').save()
                            process_dict[key].save() 
                            print(emission['name']+' '+emission['unit']+' found and added to as a biosphere exchange with amount '+str(row['value']),flush=True)
                    
                    if unit_error_flag == 1:
                            print('Correct unit should be '+emission['unit'])
                            sys.exit('Warning Failed Emission unit Error occured please check')  
        
