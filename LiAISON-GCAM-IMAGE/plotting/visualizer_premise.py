import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import sys
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from matplotlib.ticker import FormatStrFormatter
import matplotlib.font_manager as font_manager
sns.set_style("ticks")
sns.set_context("poster",font_scale=2.0)
sns.color_palette('bright')




df_name1 = pd.read_csv('lcia_name_bridge.csv')
df_loc = pd.DataFrame()
unit_df = pd.read_csv('unit_bridge.csv')





def combine_graph_t2(hydrogen, name, style,no):

            fig1, ax1 = plt.subplots(no, 3, figsize=(40, 28))
            fig1.tight_layout(pad=3.0)
            lcias = pd.unique(hydrogen['lcia'])
            c = 0
            b = 0
            for i in lcias:

                if c > 2:
                    b = b + 1
                    c = 0



                conventional = hydrogen[hydrogen['lcia'] == i]
                if b == 2 and c == 1:
                    
                    ax1[b, c] = sns.lineplot(ax=ax1[b, c], x=conventional['year'], y=conventional['value'],
                                            style=conventional[style[0]],hue=conventional[style[1]], palette='bright')
                    ax1[b, c].legend(bbox_to_anchor=(1.2,-0.2), ncol=2)
                else:
                    ax1[b, c] = sns.lineplot(ax=ax1[b, c], x=conventional['year'], y=conventional['value'],
                                            style=conventional[style[0]],hue=conventional[style[1]], palette='bright')
                    ax1[b, c].legend_.remove()
                ax1[b, c].set_ylabel(ylabel=conventional.iloc[0, 2])
                ax1[b, c].set_title(conventional.iloc[0, 0],
                                    fontdict=None, loc='center', pad=None, fontsize=33)
                ax1[b, c].set_xlabel(xlabel='year')
                ax1[b, c].tick_params(axis='x', labelsize=28)
                #ax1[b, c].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
                #ax1[b, c].ticklabel_format(axis="y")
                ax1[b, c].ticklabel_format(axis="y")
                c = c + 1
            #fig1.suptitle('TRACI2.1 Results for Hydrogen Production Process with Process Variability', fontsize=34)

            fig1.subplots_adjust(bottom=0.2)
            #plt.legend(handles=h, labels=l,frameon=True,loc='lower center')
            #fig1.legend(['United States','China','Global','United States(rcp)','China(rcp)','Global(rcp)'],loc="lower center", ncol=2, nrow = 3)

            fig1.savefig(name+'.png',dpi=300)
            plt.close()
           



def combine_graph_s2(hydrogen, name, style,no):

            fig1, ax1 = plt.subplots(no, 3, figsize=(40, 30))
            fig1.tight_layout(pad=3.0)
            lcias = pd.unique(hydrogen['lcia'])
            c = 0 
            b = 0
            for i in lcias:

                if c > 2:
                    b = b + 1
                    c = 0

                conventional = hydrogen[hydrogen['lcia'] == i]
                if b == 2 and c == 1:
                    
                    ax1[b, c] = sns.lineplot(ax=ax1[b, c], x=conventional['year'], y=conventional['value'],
                                            style=conventional[style[0]],hue=conventional[style[1]], palette='bright')
                    ax1[b, c].legend(bbox_to_anchor=(1.2,-0.2), ncol=2)
                else:
                    ax1[b, c] = sns.lineplot(ax=ax1[b, c], x=conventional['year'], y=conventional['value'],
                                            style=conventional[style[0]],hue=conventional[style[1]], palette='bright')
                    ax1[b, c].legend_.remove()
                ax1[b, c].set_ylabel(ylabel=conventional.iloc[0, 2])
                ax1[b, c].set_title(conventional.iloc[0, 0],fontdict=None, loc='center', pad=None, fontsize=33)
                ax1[b, c].set_xlabel(xlabel='year')
                ax1[b, c].tick_params(axis='x', labelsize=30)
                #ax1[b, c].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
                #ax1[b, c].ticklabel_format(axis="y")
                ax1[b, c].ticklabel_format(axis="y")
                c = c + 1
            #fig1.suptitle('Recipe Results for Hydrogen Production Process with process Variability', fontsize=34)

            #fig1.tight_layout() 
            fig1.subplots_adjust(bottom=0.2)
            #fig1.savefig(folder+"/"+name+'recipe.png',dpi=300)
            #plt.legend(handles=h, labels=l,frameon=True,loc='lower center')
            #fig1.legend(['United States','China','Global','United States(rcp)','China(rcp)','Global(rcp)'],loc="lower center", ncol=2, nrow = 3)

            fig1.savefig(name+'.png',dpi=300)
            plt.close()


def comp_process_line(model,process):
        #GRAPH FOR COMPARING PROCESSES
        location = ['US']

        allsc = [
             'ecoinvent_2020_SSP2-Base',
             'ecoinvent_2030_SSP2-Base',
             'ecoinvent_2040_SSP2-Base',
             'ecoinvent_2050_SSP2-Base',
             'ecoinvent_2060_SSP2-Base',
             'ecoinvent_2070_SSP2-Base',
             'ecoinvent_2080_SSP2-Base',
             'ecoinvent_2090_SSP2-Base',
             'ecoinvent_2100_SSP2-Base',             
             'ecoinvent_2020_SSP2-RCP26',
             'ecoinvent_2030_SSP2-RCP26',
             'ecoinvent_2040_SSP2-RCP26',
             'ecoinvent_2050_SSP2-RCP26',
             'ecoinvent_2060_SSP2-RCP26',
             'ecoinvent_2070_SSP2-RCP26',
             'ecoinvent_2080_SSP2-RCP26',
             'ecoinvent_2090_SSP2-RCP26',
             'ecoinvent_2100_SSP2-RCP26'            
             ]


        rcp26 = [
             'ecoinvent_2020_SSP2-RCP26',
             'ecoinvent_2030_SSP2-RCP26',
             'ecoinvent_2040_SSP2-RCP26',
             'ecoinvent_2050_SSP2-RCP26',
             'ecoinvent_2060_SSP2-RCP26',
             'ecoinvent_2070_SSP2-RCP26',
             'ecoinvent_2080_SSP2-RCP26',
             'ecoinvent_2090_SSP2-RCP26',
             'ecoinvent_2100_SSP2-RCP26'            
             ]

        rcpbase = [
             'ecoinvent_2020_SSP2-Base',
             'ecoinvent_2030_SSP2-Base',
             'ecoinvent_2040_SSP2-Base',
             'ecoinvent_2050_SSP2-Base',
             'ecoinvent_2060_SSP2-Base',
             'ecoinvent_2070_SSP2-Base',
             'ecoinvent_2080_SSP2-Base',
             'ecoinvent_2090_SSP2-Base',
             'ecoinvent_2100_SSP2-Base']


        '''
        Scenarios = [
             'ecoinvent_2020_SSP2-Base',
             'ecoinvent_2050_SSP2-Base',
             'ecoinvent_2100_SSP2-Base',             
             'ecoinvent_2020_SSP2-RCP26',
             'ecoinvent_2050_SSP2-RCP26',
             'ecoinvent_2100_SSP2-RCP26'            
             ]


        Scenarios = [
             'ecoinvent_2020_SSP2-RCP26',
             'ecoinvent_2050_SSP2-RCP26',
             'ecoinvent_2100_SSP2-RCP26'           
             ]


        Scenarios = [
             'ecoinvent_2020_SSP2-Base',
             'ecoinvent_2050_SSP2-Base',
             'ecoinvent_2100_SSP2-Base']
        '''
        
        #models = ['image']
        #models = ['gcam']
        #models = ['gcam','image']
        #models = ['image']
        models = [model]

        
        #hue = 'Process'
        #hue = ['Process','model']
        hue = ['Process','Scenario']

        

        #process = ['peme','smr']
        #process = ['truck']
        #process = ['peme']        
        #process = ['electricity']
        #process = ['ng_supply']

        #add_name = '_imagegcamelectricityssp2rcp26'
        #add_name = '_imagegcampemesmrssp2rcpbase'
        #add_name = '_gcampemessp2rcp26gcam_nobm'
        #add_name="gcam_peme_ssp2basercp26"
        add_name=model+'_'+process[0]+"_ssp2basercp26"
        Scenarios = allsc



        df_loc = pd.DataFrame()

        for m in models:
            for sc in Scenarios:
                for p in process:
                        print(p)
                        folder = '../results/result'+sc+"_"+m+'_'+p+'_liaison_lca_shared'

                        if p == 'electricity':
                            file = folder+'/lcia_results'+sc+'electricity'+'.csv'
                        elif p == 'truck':
                            file = folder+'/lcia_results'+sc+'truck transportation'+'.csv'
                        elif p == 'ng_supply':
                            file = folder+'/lcia_results'+sc+'ng_supply'+'.csv'
                        elif p == 'ng':
                            file = folder+'/lcia_results'+sc+'ng_electricity'+'.csv'
                        elif p == 'dacs':
                            file = folder+'/lcia_results'+sc+'dacs'+'.csv'
                        elif p == 'electricity_gas_cc_ccs':
                            file = folder+'/lcia_results'+sc+'electricity_gas_cc_ccs'+'.csv'
                        elif p == 'gasolinesustainablecoalgas':
                            file = folder+'/lcia_results'+sc+'gasolinesustainablecoalgas'+'.csv'
                        elif p ==  'peme':
                            file = folder+'/lcia_results'+sc+'hydrogen'+'.csv'
                        else:
                            file = folder+'/lcia_results'+sc+p+'.csv'
                        try:
                            df = pd.read_csv(file)
                            df['Location'] = "US"
                            df['Process'] = p
                            df['year'] = sc
                            df['model'] = m.upper()
                            df_loc = pd.concat([df_loc,df])
                        except:
                            print('Missing '+file)

        df_loc.to_csv(add_name+'compiled_lca_results.csv', index = False)                    
        #Editing labesl and units
        df_loc['Scenario'] = df_loc['year'].str.slice(15,)
        df_loc['year'] = df_loc['year'].str.slice(10,14)
        df_loc.loc[df_loc['Scenario'] == 'SSP2-Base','Scenario'] = 'SSP2 Baseline'  
        df_loc.loc[df_loc['Scenario'] == 'SSP2-RCP26','Scenario'] = 'SSP2 RCP2.6' 
        df_loc.loc[df_loc['Scenario'] == 'SSP2-RCP19','Scenario'] = 'SSP2 RCP1.9'


        df_traci = df_loc[df_loc['method'] == 'TRACI2.1']
        df_recipe = df_loc[df_loc['method'] != 'TRACI2.1']

        #df_traci = df_traci[df_traci['lcia'] != 'Photochemical Oxidation']

        #df_recipe = df_recipe[(df_recipe['lcia'] == 'Gwp100') | (df_recipe['lcia'] == 'Fep') | (df_recipe['lcia'] == 'Fetpinf') | (df_recipe['lcia'] == 'Tap100') | (df_recipe['lcia'] == 'Pmfp') | (df_recipe['lcia'] == 'Wdp') | (df_recipe['lcia'] == 'Mdp') | (df_recipe['lcia'] == 'Nltp') | (df_recipe['lcia'] == 'Htpinf')]
        temp_recipe = df_recipe
    
        df_recipe = df_recipe.merge(df_name1,left_on = 'lcia',right_on = 'abbv')
        df_recipe['lcia'] = df_recipe['full']
        df_traci = df_traci.merge(df_name1,left_on = 'lcia',right_on = 'abbv')
        df_traci['lcia'] = df_traci['full']
        #df_recipe_wt = df_recipe[df_recipe['Location'] == 'US']
        #df_traci_wt = df_traci[df_traci['Location'] == 'US']
        #df_recipe_wt['Technology'] = 'Without Tech. Evolution'
        #df_traci_wt['Technology'] = 'Without Tech. Evolution'
        us_traci = df_traci[df_traci['Location'] == 'US']
        us_recipe = df_recipe[df_recipe['Location'] == 'US']


        df_mapping = pd.DataFrame({'order': ['Global Warming', 'Freshwater Ecotoxicity', 'Carcinogenics', 'Marine Eutrophication', 'Terrestrial Acidification','Respiratory Effects, Average','Ozone Depletion','Photochemical Oxidation','Non-Carcinogenics']})
        sort_mapping = df_mapping.reset_index().set_index('order')
        us_traci['order_num'] = us_traci['lcia'].map(sort_mapping['index'])
        us_traci = us_traci.sort_values(['order_num','year'])



        df_mapping = pd.DataFrame({'order': ['Global Warming', 'Freshwater Ecotoxicity', 'Human Toxicity', 'Marine Eutrophication', 'Terrestrial Acidification','Particulate Matter Exposure','Metal depletion','Water depletion']})
        sort_mapping = df_mapping.reset_index().set_index('order')
        us_recipe['order_num'] = us_recipe['lcia'].map(sort_mapping['index'])
        us_recipe = us_recipe.sort_values(['order_num','year'])
 
        chosen_metrics = ['Global Warming', 'Freshwater Ecotoxicity', 'Human Toxicity', 'Marine Eutrophication', 'Terrestrial Acidification','Particulate Matter Exposure','Metal depletion','Water depletion','Natural land transformation']
        us_recipe = us_recipe[us_recipe['lcia'].isin(chosen_metrics) ]
        compiled_df = pd.concat([us_recipe,us_traci])

        us_recipe.to_csv(add_name+'compiled_results_lcia.csv')   
        us_recipe.to_csv('compiled_results_lcia.csv',mode = 'a',header=False)     
        sns.set_context("poster",font_scale=1.4)

        combine_graph_t2(us_traci,'processtraciline'+add_name,hue,3)
        combine_graph_t2(us_recipe,'processrecipeline'+add_name,hue,3)


'''
comp_process_line('gcam',['dacs'])
comp_process_line('image',['dacs'])

comp_process_line('gcam',['ng'])
comp_process_line('image',['ng'])
'''
#comp_process_line('gcam',['peme','smr','sox'])
#comp_process_line('image',['peme','smr','sox'])

'''
comp_process_line('gcam',['electricity'])
comp_process_line('image',['electricity'])
'''

#comp_process_line('gcam',['peme'])
#comp_process_line('image',['peme'])

comp_process_line('image',['electricity_gas_cc_ccs'])
comp_process_line('image',['electricity_coal_ccs'])
comp_process_line('image',['electricity_geothermal'])
comp_process_line('image',['electricity_gas_cc'])
comp_process_line('image',['electricity_solar_pv'])
comp_process_line('image',['electricity_wind'])
comp_process_line('image',['electricity_gas_ct'])
comp_process_line('image',['electricity_hydro'])
comp_process_line('image',['electricity_solar_csp'])
comp_process_line('image',['electricity_coal'])
comp_process_line('image',['gasoline5byethanolvolume'])
comp_process_line('image',['gasoline'])
comp_process_line('image',['gasolinesustainablecoalgas'])
comp_process_line('image',['gasolinesustainabledacs'])
