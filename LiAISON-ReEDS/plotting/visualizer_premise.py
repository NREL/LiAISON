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


def comp_process_line():
        #GRAPH FOR COMPARING PROCESSES
        location = ['US']

        Scenarios = ["High_Demand_Growth2036",
                    "High_Demand_Growth_100by20352036",
                    "High_RE_Cost_NoNascent2036",
                    "DAC_95by20502036",
                    "High_NG_Price_NoNascent2036",
                    "No_TC_Expiration_100by20352036",
                    "Low_RE_Cost_95by2050_NoNascent2036",
                    "High_Demand_Growth_95by20502036",
                    "Low_NG_Price_NoNascent2036",
                    "No_TC_Expiration2036",
                    "High_RE_Cost2036",
                    "Low_RE_Cost_NoNascent2036",
                    "Low_Nuclear_CCS_Cost_100by20352036",
                    "High_Trans_100by20352036",
                    "Low_Nuclear_CCS_Cost2036",
                    "Low_RE_Cost_95by20502036",
                    "High_RE_Cost_95by2050_NoNascent2036",
                    "No_IRA_NoNascent2036",
                    "Low_NG_Price_95by20502036",
                    "No_IRA2036",
                    "High_RE_Cost_100by20352036",
                    "Low_RE_Cost2036",
                    "Reduced_RE_Resource_95by2050_NoNascent2036",
                    "Mid_Case_95by20502036",
                    "High_NG_Price2036",
                    "Low_Demand_Growth2036",
                    "High_NG_Price_95by20502036",
                    "High_RE_Cost_95by20502036",
                    "Mid_Case_NoNascent2036",
                    "Low_Demand_Growth_95by2050_NoNascent2036",
                    "No_TC_Expiration_NoNascent2036",
                    "High_NG_Price_100by20352036",
                    "DAC_95by2050_NoNascent2036",
                    "High_NG_Price_95by2050_NoNascent2036",
                    "No_IRA_95by2050_NoNascent2036",
                    "No_TC_Expiration_95by20502036",
                    "Reduced_RE_Resource_95by20502036",
                    "PVB2036",
                    "High_Trans2036",
                    "No_TC_Expiration_95by2050_NoNascent2036",
                    "Low_Nuclear_CCS_Cost_95by2050_NoNascent2036",
                    "High_Trans_95by2050_NoNascent2036",
                    "Mid_Case_95by2050_NoNascent2036",
                    "Low_NG_Price2036",
                    "Low_Nuclear_CCS_Cost_95by20502036",
                    "Mid_Case2036",
                    "Reduced_RE_Resource2036",
                    "Low_Nuclear_CCS_Cost_NoNascent2036",
                    "Mid_Case_100by20352036",
                    "PVB_100by20352036",
                    "DAC_NoNascent2036",
                    "No_IRA_95by20502036",
                    "Low_NG_Price_100by20352036",
                    "High_Trans_95by20502036",
                    "Reduced_RE_Resource_NoNascent2036",
                    "PVB_NoNascent2036",
                    "High_Trans_NoNascent2036",
                    "High_Demand_Growth_95by2050_NoNascent2036",
                    "DAC2036",
                    "DAC_100by20352036",
                    "Low_Demand_Growth_95by20502036",
                    "PVB_95by20502036",
                    "Low_RE_Cost_100by20352036",
                    "Reduced_RE_Resource_100by20352036",
                    "Low_NG_Price_95by2050_NoNascent2036",
                    "PVB_95by2050_NoNascent2036",
                    "Low_Demand_Growth_100by20352036",
                    "Low_Demand_Growth_NoNascent2036",
                    "High_Demand_Growth_NoNascent2036",
                    "No_IRA_100by20352036",
                    "High_Demand_Growth2050",
                    "High_Demand_Growth_100by20352050",
                    "High_RE_Cost_NoNascent2050",
                    "DAC_95by20502050",
                    "High_NG_Price_NoNascent2050",
                    "No_TC_Expiration_100by20352050",
                    "Low_RE_Cost_95by2050_NoNascent2050",
                    "High_Demand_Growth_95by20502050",
                    "Low_NG_Price_NoNascent2050",
                    "No_TC_Expiration2050",
                    "High_RE_Cost2050",
                    "Low_RE_Cost_NoNascent2050",
                    "Low_Nuclear_CCS_Cost_100by20352050",
                    "High_Trans_100by20352050",
                    "Low_Nuclear_CCS_Cost2050",
                    "Low_RE_Cost_95by20502050",
                    "High_RE_Cost_95by2050_NoNascent2050",
                    "No_IRA_NoNascent2050",
                    "Low_NG_Price_95by20502050",
                    "No_IRA2050",
                    "High_RE_Cost_100by20352050",
                    "Low_RE_Cost2050",
                    "Reduced_RE_Resource_95by2050_NoNascent2050",
                    "Mid_Case_95by20502050",
                    "High_NG_Price2050",
                    "Low_Demand_Growth2050",
                    "High_NG_Price_95by20502050",
                    "High_RE_Cost_95by20502050",
                    "Mid_Case_NoNascent2050",
                    "Low_Demand_Growth_95by2050_NoNascent2050",
                    "No_TC_Expiration_NoNascent2050",
                    "High_NG_Price_100by20352050",
                    "DAC_95by2050_NoNascent2050",
                    "High_NG_Price_95by2050_NoNascent2050",
                    "No_IRA_95by2050_NoNascent2050",
                    "No_TC_Expiration_95by20502050",
                    "Reduced_RE_Resource_95by20502050",
                    "PVB2050",
                    "High_Trans2050",
                    "No_TC_Expiration_95by2050_NoNascent2050",
                    "Low_Nuclear_CCS_Cost_95by2050_NoNascent2050",
                    "High_Trans_95by2050_NoNascent2050",
                    "Mid_Case_95by2050_NoNascent2050",
                    "Low_NG_Price2050",
                    "Low_Nuclear_CCS_Cost_95by20502050",
                    "Mid_Case2050",
                    "Reduced_RE_Resource2050",
                    "Low_Nuclear_CCS_Cost_NoNascent2050",
                    "Mid_Case_100by20352050",
                    "PVB_100by20352050",
                    "DAC_NoNascent2050",
                    "No_IRA_95by20502050",
                    "Low_NG_Price_100by20352050",
                    "High_Trans_95by20502050",
                    "Reduced_RE_Resource_NoNascent2050",
                    "PVB_NoNascent2050",
                    "High_Trans_NoNascent2050",
                    "High_Demand_Growth_95by2050_NoNascent2050",
                    "DAC2050",
                    "DAC_100by20352050",
                    "Low_Demand_Growth_95by20502050",
                    "PVB_95by20502050",
                    "Low_RE_Cost_100by20352050",
                    "Reduced_RE_Resource_100by20352050",
                    "Low_NG_Price_95by2050_NoNascent2050",
                    "PVB_95by2050_NoNascent2050",
                    "Low_Demand_Growth_100by20352050",
                    "Low_Demand_Growth_NoNascent2050",
                    "High_Demand_Growth_NoNascent2050",
                    "No_IRA_100by20352050",
                    "High_Demand_Growth2022",
                    "High_Demand_Growth_100by20352022",
                    "High_RE_Cost_NoNascent2022",
                    "DAC_95by20502022",
                    "High_NG_Price_NoNascent2022",
                    "No_TC_Expiration_100by20352022",
                    "Low_RE_Cost_95by2050_NoNascent2022",
                    "High_Demand_Growth_95by20502022",
                    "Low_NG_Price_NoNascent2022",
                    "No_TC_Expiration2022",
                    "High_RE_Cost2022",
                    "Low_RE_Cost_NoNascent2022",
                    "Low_Nuclear_CCS_Cost_100by20352022",
                    "High_Trans_100by20352022",
                    "Low_Nuclear_CCS_Cost2022",
                    "Low_RE_Cost_95by20502022",
                    "High_RE_Cost_95by2050_NoNascent2022",
                    "No_IRA_NoNascent2022",
                    "Low_NG_Price_95by20502022",
                    "No_IRA2022",
                    "High_RE_Cost_100by20352022",
                    "Low_RE_Cost2022",
                    "Reduced_RE_Resource_95by2050_NoNascent2022",
                    "Mid_Case_95by20502022",
                    "High_NG_Price2022",
                    "Low_Demand_Growth2022",
                    "High_NG_Price_95by20502022",
                    "High_RE_Cost_95by20502022",
                    "Mid_Case_NoNascent2022",
                    "Low_Demand_Growth_95by2050_NoNascent2022",
                    "No_TC_Expiration_NoNascent2022",
                    "High_NG_Price_100by20352022",
                    "DAC_95by2050_NoNascent2022",
                    "High_NG_Price_95by2050_NoNascent2022",
                    "No_IRA_95by2050_NoNascent2022",
                    "No_TC_Expiration_95by20502022",
                    "Reduced_RE_Resource_95by20502022",
                    "PVB2022",
                    "High_Trans2022",
                    "No_TC_Expiration_95by2050_NoNascent2022",
                    "Low_Nuclear_CCS_Cost_95by2050_NoNascent2022",
                    "High_Trans_95by2050_NoNascent2022",
                    "Mid_Case_95by2050_NoNascent2022",
                    "Low_NG_Price2022",
                    "Low_Nuclear_CCS_Cost_95by20502022",
                    "Mid_Case2022",
                    "Reduced_RE_Resource2022",
                    "Low_Nuclear_CCS_Cost_NoNascent2022",
                    "Mid_Case_100by20352022",
                    "PVB_100by20352022",
                    "DAC_NoNascent2022",
                    "No_IRA_95by20502022",
                    "Low_NG_Price_100by20352022",
                    "High_Trans_95by20502022",
                    "Reduced_RE_Resource_NoNascent2022",
                    "PVB_NoNascent2022",
                    "High_Trans_NoNascent2022",
                    "High_Demand_Growth_95by2050_NoNascent2022",
                    "DAC2022",
                    "DAC_100by20352022",
                    "Low_Demand_Growth_95by20502022",
                    "PVB_95by20502022",
                    "Low_RE_Cost_100by20352022",
                    "Reduced_RE_Resource_100by20352022",
                    "Low_NG_Price_95by2050_NoNascent2022",
                    "PVB_95by2050_NoNascent2022",
                    "Low_Demand_Growth_100by20352022",
                    "Low_Demand_Growth_NoNascent2022",
                    "High_Demand_Growth_NoNascent2022",
                    "No_IRA_100by20352022"]

        df_loc = pd.DataFrame()
        for sc in Scenarios:

                        folder = '../results/result'+sc+'short_hipster_lca_'+sc+sc
                        file = folder+'/lcia_resultspremise_baseelectricity.csv'
                        try:
                            df = pd.read_csv(file)
                            df['Location'] = "US"
                            df['Process'] = 'US Electricity Grid Mix'
                            df['year'] = sc[len(sc)-4:len(sc)]
                            df['Scenario'] = sc[0:len(sc)-4]
                            df['model'] = 'ReEDS'
                            df_loc = pd.concat([df_loc,df])
                        except:
                            print('Missing '+sc)

        df_loc.to_csv('compiled_lca_results.csv', index = False)                    
        #Editing labesl and units
        #df_loc['Scenario'] = df_loc['year'].str.slice(0,17)
        #df_loc['year'] = df_loc['year'].str.slice(17,)
        df_loc.loc[df_loc['Scenario'] == 'midcase','Scenario'] = 'ReEDS MidCase'   

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

        us_recipe.to_csv('compiled_results_lcia.csv')     
        sns.set_context("poster",font_scale=1.4)



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
                                            hue=conventional['Scenario'], palette='bright')
                    ax1[b, c].legend(bbox_to_anchor=(1.2,-0.2), ncol=2)
                else:
                    ax1[b, c] = sns.lineplot(ax=ax1[b, c], x=conventional['year'], y=conventional['value'],
                                            hue=conventional['Scenario'], palette='bright')
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
        combine_graph_t2(us_traci,'processtraciline','model',3)   



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
                                            hue=conventional['Scenario'], palette='bright')
                    ax1[b, c].legend(bbox_to_anchor=(1.2,-0.2), ncol=2)
                else:
                    ax1[b, c] = sns.lineplot(ax=ax1[b, c], x=conventional['year'], y=conventional['value'],
                                            hue=conventional['Scenario'], palette='bright')
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
            #plt.legend(handles=h, labels=l,frameon=True,loc='lower center')
            #fig1.legend(['United States','China','Global','United States(rcp)','China(rcp)','Global(rcp)'],loc="lower center", ncol=2, nrow = 3)

            fig1.savefig(name+'.png',dpi=300)
        combine_graph_s2(us_recipe, 'processrecipeline', 'model',3) 

comp_process_line()
