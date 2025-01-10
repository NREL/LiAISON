import os
import pandas as pd
os.environ['BRIGHTWAY2_DIR'] = "/projects/liaison/env/batteries_liaison/"
import brightway2 as bw
bw.projects.set_current('ecoinvent_2020_SSP2-Base')
ei_cf_36_db = bw.Database('ecoinvent_2020_SSP2-Base')
db = 'ecoinvent_updated'
def premise():

        process = []
        flows = []
        amount = []
        type_of_flow = []
        unit = []
        inpu_t = []
        output = []
        activity = []
        activity_lc = []
        supplying_activity = []
        supplying_activity_lc = []


        code_df = {}
        for act in ei_cf_36_db:
            code_df[str(act.as_dict()['code'])] = act

        for act in ei_cf_36_db:
           #if (act['name'] == 'market group for electricity, high voltage' or act['name'] == 'market group for electricity, low voltage' or act['name'] == 'market group for electricity, medium voltage') and act['location'] =='USA':
           #if ("US" in act['location'] and "RUS" != act['location']) :   
               print(act['name'],act['location'])
               for exch in act.exchanges():         
                        process.append(act['name'])
                        activity_lc.append(act['location'])
                        flows.append(exch['name'])
                        amount.append(exch['amount'])
                        type_of_flow.append(exch['type'])
                        unit.append(exch['unit'])
                        inpu_t.append(exch['input'])
                        output.append(exch['output'])
                        try:
                           activity.append(exch['activity'])
                        except:
                           activity.append('')
                        s =  exch['input'][1]  
                        try:
                             s_act = code_df[s]
                             supplying_activity.append(s_act['name'])
                             supplying_activity_lc.append(s_act['location'])
                        except:
                             supplying_activity.append('')
                             supplying_activity_lc.append('')   

        ecoinvent38 = pd.DataFrame()
        ecoinvent38['process'] = process
        ecoinvent38['process location'] = activity_lc
        ecoinvent38['flows'] = flows
        ecoinvent38['amount'] = amount
        ecoinvent38['type_of_flow'] = type_of_flow
        ecoinvent38['unit'] = unit
        ecoinvent38['inpu_t'] = inpu_t
        ecoinvent38['output'] = output
        ecoinvent38['activity'] = activity
        ecoinvent38['supplying activity'] = supplying_activity
        ecoinvent38['supplying activity location'] = supplying_activity_lc

        ecoinvent38.to_excel('ecoinvent_38.xlsx',index = False)

#act = [i for i in bw.Database(db).search('electricity photovoltaic', limit=1000) if (i.as_dict()['location'] == 'US-WECC')]
#act = [i for i in bw.Database(db).search('solar', limit=1000)][0]
#act = [i for i in bw.Database(db).search('market for electricity', limit=1000) if (i.as_dict()['location'] == 'US')]
premise()


def wurst():

    elec_type = []
    elec_amount = []
    elec_loc = []
    elec_mix = []
    database = []

    code_df = {}
    for act in ei_cf_36_db:
        code_df[str(act.as_dict()['code'])] = act

    for act in ei_cf_36_db:
       if (act['name'] == 'market group for electricity, high voltage' or act['name'] == 'market group for electricity, low voltage') and act['location'] =='US':
           print(act['name'])
           for exch in act.exchanges():
              if (code_df[str(exch.as_dict()['input'][1])]['name'] == 'market for electricity, high voltage') or (code_df[str(exch.as_dict()['input'][1])]['name'] == 'market for electricity, low voltage'):
                 act2 = code_df[str(exch.as_dict()['input'][1])]
                 print(act2['name']) 
                 for exch2 in act2.exchanges():
                    if str(exch2.as_dict()['input'][0]) == "ecoinvent3.8":
                        if code_df[str(exch2.as_dict()['input'][1])]['name'][0:22] == 'electricity production':
                         elec_type.append(code_df[str(exch2.as_dict()['input'][1])]['name'])
                         elec_amount.append(exch2['amount'])
                         elec_loc.append(act2['location'])
                         elec_mix.append(exch['amount'])
                         database.append(db)
                        elif code_df[str(exch2.as_dict()['input'][1])]['name'][0:15] == 'Electricity, at':
                         elec_type.append(code_df[str(exch2.as_dict()['input'][1])]['name'])
                         elec_amount.append(exch2['amount'])
                         elec_loc.append(act2['location'])
                         elec_mix.append(exch['amount'])
                         database.append(db)

                   
    elec_df = pd.DataFrame(
      {'elec_type': elec_type,
       'elec_amount kwh': elec_amount,
       'elec_loc': elec_loc,
       'elec_mix ratio': elec_mix, 
       'database':database
      })  
           
    elec_df.to_csv(db+'_electricity_mix_raw.csv',index = False)
    regions = list(pd.unique(elec_df['elec_loc']))
    elec_df_corr = pd.DataFrame()
    for reg in regions:
        df = elec_df[elec_df['elec_loc'] == reg]
        t_sum = sum(df['elec_amount kwh'])
        loss_inverse = 1/t_sum
        df['elec_amount kwh'] = df['elec_amount kwh'] * loss_inverse
        elec_df_corr = pd.concat([elec_df_corr,df])

    elec_df_corr['total_flow'] = elec_df_corr['elec_amount kwh']* elec_df_corr['elec_mix ratio']
    elec_df_corr = elec_df_corr[['elec_type','database','total_flow']]
    elec_df_corr= elec_df_corr.groupby(['elec_type','database'])['total_flow'].agg('sum').reset_index()
    print(sum(elec_df_corr['total_flow']),flush=True)
    elec_df_corr.to_csv(db+'_electricity_mix.csv',index = False)

#wurst()

def wurst3():

    process = []
    flows = []
    amount = []
    type_of_flow = []
    unit = []
    inpu_t = []
    output = []
    activity = []
    activity_lc = []
    supplying_activity = []
    supplying_activity_lc = []

    code_df = {}
    for act in ei_cf_36_db:
        code_df[str(act.as_dict()['code'])] = act


    for act in ei_cf_36_db:
        act_d = act.as_dict()
        
        for ex in act.exchanges():


            


                    ex_d = ex.as_dict()
                    if 'US' in act_d['location']:
                        process.append(act_d['name'])
                        activity_lc.append(act_d['location'])
                        flows.append(ex_d['name'])
                        amount.append(ex_d['amount'])
                        type_of_flow.append(ex_d['type'])
                        unit.append(ex_d['unit'])
                        inpu_t.append(ex_d['input'])
                        output.append(ex_d['output'])
                        try:
                           activity.append(ex_d['activity'])
                        except:
                           activity.append('')
                        s =  ex_d['input'][1]  
                        try:
                             s_act = code_df[s]
                             supplying_activity.append(s_act['name'])
                             supplying_activity_lc.append(s_act['location'])
                        except:
                             supplying_activity.append('')
                             supplying_activity_lc.append('')               




    ecoinvent38 = pd.DataFrame()
    ecoinvent38['process'] = process
    ecoinvent38['process location'] = activity_lc
    ecoinvent38['flows'] = flows
    ecoinvent38['amount'] = amount
    ecoinvent38['type_of_flow'] = type_of_flow
    ecoinvent38['unit'] = unit
    ecoinvent38['inpu_t'] = inpu_t
    ecoinvent38['output'] = output
    ecoinvent38['activity'] = activity
    ecoinvent38['supplying activity'] = supplying_activity
    ecoinvent38['supplying activity location'] = supplying_activity_lc

    ecoinvent38.to_csv('ecoinvent38_USA.csv',index = False)

#wurst3()


'''
def wurst_2():

    elec_type = []
    elec_amount = []
    elec_loc = []
    elec_mix = []
    database = []

    code_df = {}
    for act in ei_cf_36_db:
        code_df[str(act.as_dict()['code'])] = act

    for act in ei_cf_36_db:
       if act['name'][0:22] == 'electricity production' and act['location'][0:2] =='US':
           print(act['name'])
           for exch in act.exchanges():
                if str(exch.as_dict()['input'][0]) == "ecoinvent3.8":
                         elec_type.append(code_df[str(exch.as_dict()['input'][1])]['name'])
                         elec_amount.append(exch['amount'])
                         elec_loc.append(act['location'])
                         elec_mix.append(exch['amount'])
                         database.append(db)

                   
    elec_df = pd.DataFrame(
      {'elec_type': elec_type,
       'elec_amount kwh': elec_amount,
       'elec_loc': elec_loc,
       'elec_mix ratio': elec_mix, 
       'database':database
      })  
           
    elec_df.to_csv(db+'_electricity_activities_raw.csv',index = False)



wurst_2()
'''