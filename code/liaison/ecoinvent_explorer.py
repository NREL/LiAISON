import pandas as pd
def electricity_mix(updated_project_name,output_dir,results_filename,updated_database,bw):

        bw.projects.set_current(updated_project_name)
        print('Databases in this project are-',flush=True)
        print(bw.databases,flush=True)
        ei_cf_36_db = bw.Database(updated_database)

        print('Extracting electricity flows')
        elec_type = []
        elec_amount = []
        elec_loc = []
        elec_mix = []
        database = []
        for act in ei_cf_36_db:
           if (act['name'] == 'market group for electricity, high voltage' or act['name'] == 'market group for electricity, low voltage') and act['location'] =='USA':
               
               for exch in act.exchanges():

                    if exch['type'] == 'technosphere':
                        print(exch['name'],exch['location'],exch['amount'])
                        #if exch['name'][0:22] == 'electricity production':
                                     
                        elec_type.append(exch['name'])
                        elec_amount.append(exch['amount'])
                        elec_loc.append(exch['location'])
                        elec_mix.append(exch['amount'])
                        database.append(updated_database)

        elec_df = pd.DataFrame(
          {'elec_type': elec_type,
           'elec_amount kwh': elec_amount,
           'elec_loc': elec_loc,
           'elec_mix ratio': elec_mix, 
           'database':database
          })

        if not elec_df.empty:
           
            elec_df['total_flow'] = elec_df['elec_amount kwh']
            elec_df.to_csv(output_dir+updated_database+'_electricity_mix_raw.csv',index = False)
            elec_df_f = elec_df[['elec_type','database','total_flow']]
            elec_df_f = elec_df_f.groupby(['elec_type','database'])['total_flow'].agg('sum').reset_index()
            #print('Total electricity production',sum(elec_df_f['total_flow']),flush=True)

            elec_df_f = elec_df_f[elec_df_f['elec_type'].str.contains('electricity production')]
            total = sum(elec_df_f['total_flow'])
            elec_df_f['total_flow'] = elec_df_f['total_flow']/total
            elec_df_f.to_csv(output_dir+updated_database+'_electricity_mix.csv',index = False)


