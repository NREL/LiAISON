carma_electricity_ds_name_dict = {
 'Electricity, at wood burning power plant 20 MW, truck 25km, post, pipeline 200km, storage 1000m/2025':'Biomass_CCS',
 'Electricity, at power plant/natural gas, NGCC, no CCS/2025/kWh':'Natural_gas_CC',
 'Electricity, at power plant/natural gas, pre, pipeline 400km, storage 3000m/2025':'Natural_gas_CCS',
 'Electricity, at BIGCC power plant 450MW, pre, pipeline 200km, storage 1000m/2025':'Biomass_CCS',
 'Electricity, at power plant/hard coal, PC, no CCS/2025': 'Coal_ST',
 'Electricity, at power plant/hard coal, IGCC, no CCS/2025':'IGCC',
 'Electricity, at wood burning power plant 20 MW, truck 25km, no CCS/2025':'Biomass_ST',
 'Electricity, at power plant/natural gas, pre, pipeline 200km, storage 1000m/2025':'Natural_gas_CCS',
 'Electricity, at power plant/lignite, PC, no CCS/2025':'Coal_ST',
 'Electricity, at power plant/hard coal, pre, pipeline 200km, storage 1000m/2025':'Coal_CCS',
 'Electricity, from CC plant, 100% SNG, truck 25km, post, pipeline 200km, storage 1000m/2025': 'Biomass_CCS',
 'Electricity, at wood burning power plant 20 MW, truck 25km, post, pipeline 400km, storage 3000m/2025':'Biomass_CCS',
 'Electricity, at power plant/hard coal, oxy, pipeline 400km, storage 3000m/2025':'Coal_CCS',
 'Electricity, at power plant/lignite, oxy, pipeline 200km, storage 1000m/2025':'Coal_CCS',
 'Electricity, at power plant/hard coal, post, pipeline 400km, storage 3000m/2025':'Coal_CCS',
 'Electricity, at power plant/lignite, pre, pipeline 200km, storage 1000m/2025':'Coal_CCS',
 'Electricity, at BIGCC power plant 450MW, pre, pipeline 400km, storage 3000m/2025':'Biomass_CCS',
 'Electricity, at power plant/natural gas, post, pipeline 400km, storage 1000m/2025':'Natural_gas_CCS',
 'Electricity, at power plant/lignite, post, pipeline 400km, storage 3000m/2025':'Coal_CCS',
 'Electricity, at power plant/hard coal, post, pipeline 400km, storage 1000m/2025':'Coal_CCS',
 'Electricity, from CC plant, 100% SNG, truck 25km, post, pipeline 400km, storage 3000m/2025':'Biomass_CCS',
 'Electricity, at power plant/natural gas, ATR H2-CC, no CCS/2025':'Natural_gas_CCS',
 'Electricity, at power plant/hard coal, pre, pipeline 400km, storage 3000m/2025':'Coal_CCS',
 'Electricity, at power plant/lignite, IGCC, no CCS/2025':'IGCC',
 'Electricity, at power plant/hard coal, post, pipeline 200km, storage 1000m/2025':'Coal_CCS',
 'Electricity, at power plant/lignite, oxy, pipeline 400km, storage 3000m/2025':'Coal_CCS',
 'Electricity, at power plant/lignite, post, pipeline 200km, storage 1000m/2025':'Coal_CCS',
 'Electricity, at power plant/lignite, pre, pipeline 400km, storage 3000m/2025':'Coal_CCS',
 'Electricity, at power plant/natural gas, post, pipeline 200km, storage 1000m/2025':'Natural_gas_CCS',
 'Electricity, at power plant/natural gas, post, pipeline 400km, storage 3000m/2025':'Natural_gas_CCS',
 'Electricity, at BIGCC power plant 450MW, no CCS/2025':'Biomass_ST',
 'Electricity, from CC plant, 100% SNG, truck 25km, no CCS/2025':'Biomass_ST',
 'Electricity, at power plant/hard coal, oxy, pipeline 200km, storage 1000m/2025':'Coal_CCS'
    }




available_electricity_generating_technologies = {
    'Solar_PV_cen' : ['electricity production, photovoltaic, 570kWp open ground installation, multi-Si'],  ## need to further confirm the classification of solar PV
    
    #Has this been confirmed????
    
    'Solar_PV_decen' : ['electricity production, photovoltaic, 3kWp facade installation, multi-Si, laminated, integrated',
                        'electricity production, photovoltaic, 3kWp facade installation, multi-Si, panel, mounted',
                        'electricity production, photovoltaic, 3kWp facade installation, single-Si, laminated, integrated',
                        'electricity production, photovoltaic, 3kWp facade installation, single-Si, panel, mounted',
                        'electricity production, photovoltaic, 3kWp flat-roof installation, multi-Si',
                        'electricity production, photovoltaic, 3kWp flat-roof installation, single-Si',
                        'electricity production, photovoltaic, 3kWp slanted-roof installation, a-Si, laminated, integrated',
                        'electricity production, photovoltaic, 3kWp slanted-roof installation, a-Si, panel, mounted',
                        'electricity production, photovoltaic, 3kWp slanted-roof installation, CdTe, laminated, integrated',
                        'electricity production, photovoltaic, 3kWp slanted-roof installation, CIS, panel, mounted',
                        'electricity production, photovoltaic, 3kWp slanted-roof installation, multi-Si, laminated, integrated',
                        'electricity production, photovoltaic, 3kWp slanted-roof installation, multi-Si, panel, mounted',
                        'electricity production, photovoltaic, 3kWp slanted-roof installation, ribbon-Si, laminated, integrated',
                        'electricity production, photovoltaic, 3kWp slanted-roof installation, ribbon-Si, panel, mounted',
                        'electricity production, photovoltaic, 3kWp slanted-roof installation, single-Si, laminated, integrated'], 
    
    'CSP': ['electricity production, solar thermal parabolic trough, 50 MW', 
            'electricity production, solar tower power plant, 20 MW'],    
    
    'Wind_onshore': ['electricity production, wind, <1MW turbine, onshore',
                     'electricity production, wind, 1-3MW turbine, onshore',
                     'electricity production, wind, >3MW turbine, onshore'],
    
    'Wind_offshore': ['electricity production, wind, 1-3MW turbine, offshore'],
    
    'Wave' : ['electricity production, wave, 20kw/meter'], 
   
    'Hydro': ['electricity production, hydro, reservoir, alpine region',
              'electricity production, hydro, reservoir, non-alpine region',
              'electricity production, hydro, reservoir, tropical region',
              'electricity production, hydro, run-of-river'],  
        
    'Other_renewables':['electricity production, deep geothermal'], 
        
    'Nuclear': ['electricity production, nuclear, boiling water reactor',
                'electricity production, nuclear, pressure water reactor, heavy water moderated',
                'electricity production, nuclear, pressure water reactor'],   
        
    'Coal_ST': ['electricity production, hard coal',
                'electricity production, lignite',
                'electricity production, peat',
                'electricity production, hard coal, conventional',
                'electricity production, hard coal, supercritical'],   
        
    'Coal_CHP': ['heat and power co-generation, hard coal',
                 'heat and power co-generation, lignite'],   
        
    'IGCC': ['Electricity, at power plant/hard coal, IGCC, no CCS/2025', #From Carma project
             'Electricity, at power plant/lignite, IGCC, no CCS/2025'],  #From Carma project
        
    'Oil_ST': ['electricity production, oil'],
        
    'Oil_CHP': ['heat and power co-generation, oil'],
        
    'Oil_CC': ['electricity production, oil'], #Use copy of Oil ST here as this doesn't exist in ecoinvent
    
    'Natural_gas_OC': ['electricity production, natural gas, conventional power plant'], 
    
    'Natural_gas_CC': ['electricity production, natural gas, combined cycle power plant'],
        
    'Natural_gas_CHP': ['heat and power co-generation, natural gas, combined cycle power plant, 400MW electrical',
                        'heat and power co-generation, natural gas, conventional power plant, 100MW electrical',
                       'heat and power co-generation, natural gas, 500kW electrical, lean burn'],
            
    'Biomass_CHP': ['heat and power co-generation, wood chips, 6667 kW, state-of-the-art 2014',
                    'heat and power co-generation, wood chips, 6667 kW',
                    'heat and power co-generation, biogas, gas engine'],
        
    'Biomass_CC':['electricity production, wood, future'], # Use copy of Biomass ST here as this not available in ecoinvent
        
    'Biomass_ST':['electricity production, wood, future'],

    'Coal_CCS': ['Electricity, at power plant/hard coal, pre, pipeline 200km, storage 1000m/2025',
                 'Electricity, at power plant/lignite, pre, pipeline 200km, storage 1000m/2025',
                 'Electricity, at power plant/hard coal, post, pipeline 200km, storage 1000m/2025',
                 'Electricity, at power plant/lignite, post, pipeline 200km, storage 1000m/2025',
                 'Electricity, at power plant/lignite, oxy, pipeline 200km, storage 1000m/2025',
                 'Electricity, at power plant/hard coal, oxy, pipeline 200km, storage 1000m/2025'],
        
    'Coal_CHP_CCS': ['Electricity, at power plant/hard coal, pre, pipeline 200km, storage 1000m/2025',#Carma project didn't include Coal CHP CCS
                     'Electricity, at power plant/lignite, pre, pipeline 200km, storage 1000m/2025',
                     'Electricity, at power plant/hard coal, post, pipeline 200km, storage 1000m/2025',
                     'Electricity, at power plant/lignite, post, pipeline 200km, storage 1000m/2025',
                     'Electricity, at power plant/lignite, oxy, pipeline 200km, storage 1000m/2025',
                     'Electricity, at power plant/hard coal, oxy, pipeline 200km, storage 1000m/2025'],

    'Oil_CCS': ['Electricity, at power plant/hard coal, pre, pipeline 200km, storage 1000m/2025', #Carma project didn't include oil - we just use all coal and gas datasets as a proxy
                'Electricity, at power plant/lignite, pre, pipeline 200km, storage 1000m/2025',
                'Electricity, at power plant/hard coal, post, pipeline 200km, storage 1000m/2025',
                'Electricity, at power plant/lignite, post, pipeline 200km, storage 1000m/2025',
                'Electricity, at power plant/lignite, oxy, pipeline 200km, storage 1000m/2025',
                'Electricity, at power plant/hard coal, oxy, pipeline 200km, storage 1000m/2025',
                'Electricity, at power plant/natural gas, pre, pipeline 200km, storage 1000m/2025',
                'Electricity, at power plant/natural gas, post, pipeline 200km, storage 1000m/2025'],
        
    'Oil_CHP_CCS': ['Electricity, at power plant/hard coal, pre, pipeline 200km, storage 1000m/2025', #Carma project didn't include oil - we just use all coal and gas datasets as a proxy
                    'Electricity, at power plant/lignite, pre, pipeline 200km, storage 1000m/2025',
                    'Electricity, at power plant/hard coal, post, pipeline 200km, storage 1000m/2025',
                    'Electricity, at power plant/lignite, post, pipeline 200km, storage 1000m/2025',
                    'Electricity, at power plant/lignite, oxy, pipeline 200km, storage 1000m/2025',
                    'Electricity, at power plant/hard coal, oxy, pipeline 200km, storage 1000m/2025',
                    'Electricity, at power plant/natural gas, pre, pipeline 200km, storage 1000m/2025',
                    'Electricity, at power plant/natural gas, post, pipeline 200km, storage 1000m/2025'],

    'Natural_gas_CCS': ['Electricity, at power plant/natural gas, pre, pipeline 200km, storage 1000m/2025',
                        'Electricity, at power plant/natural gas, post, pipeline 200km, storage 1000m/2025'],

    'Natural_gas_CHP_CCS':['Electricity, at power plant/natural gas, pre, pipeline 200km, storage 1000m/2025', #Copy normal natural gas CCS datasets here
                           'Electricity, at power plant/natural gas, post, pipeline 200km, storage 1000m/2025'],
        
    'Biomass_CCS': ['Electricity, from CC plant, 100% SNG, truck 25km, post, pipeline 200km, storage 1000m/2025',
                    'Electricity, at wood burning power plant 20 MW, truck 25km, post, pipeline 200km, storage 1000m/2025',
                    'Electricity, at BIGCC power plant 450MW, pre, pipeline 200km, storage 1000m/2025'],

    'Biomass_CHP_CCS': ['Electricity, from CC plant, 100% SNG, truck 25km, post, pipeline 200km, storage 1000m/2025', #Copy normal wood CCS datasets here as CHP not available
                    'Electricity, at wood burning power plant 20 MW, truck 25km, post, pipeline 200km, storage 1000m/2025',
                    'Electricity, at BIGCC power plant 450MW, pre, pipeline 200km, storage 1000m/2025']
}


carma_electricity_ds_name_dict = {
 'Electricity, at wood burning power plant 20 MW, truck 25km, post, pipeline 200km, storage 1000m/2025':'Biomass_CCS',
 'Electricity, at power plant/natural gas, NGCC, no CCS/2025/kWh':'Natural_gas_CC',
 'Electricity, at power plant/natural gas, pre, pipeline 400km, storage 3000m/2025':'Natural_gas_CCS',
 'Electricity, at BIGCC power plant 450MW, pre, pipeline 200km, storage 1000m/2025':'Biomass_CCS',
 'Electricity, at power plant/hard coal, PC, no CCS/2025': 'Coal_ST',
 'Electricity, at power plant/hard coal, IGCC, no CCS/2025':'IGCC',
 'Electricity, at wood burning power plant 20 MW, truck 25km, no CCS/2025':'Biomass_ST',
 'Electricity, at power plant/natural gas, pre, pipeline 200km, storage 1000m/2025':'Natural_gas_CCS',
 'Electricity, at power plant/lignite, PC, no CCS/2025':'Coal_ST',
 'Electricity, at power plant/hard coal, pre, pipeline 200km, storage 1000m/2025':'Coal_CCS',
 'Electricity, from CC plant, 100% SNG, truck 25km, post, pipeline 200km, storage 1000m/2025': 'Biomass_CCS',
 'Electricity, at wood burning power plant 20 MW, truck 25km, post, pipeline 400km, storage 3000m/2025':'Biomass_CCS',
 'Electricity, at power plant/hard coal, oxy, pipeline 400km, storage 3000m/2025':'Coal_CCS',
 'Electricity, at power plant/lignite, oxy, pipeline 200km, storage 1000m/2025':'Coal_CCS',
 'Electricity, at power plant/hard coal, post, pipeline 400km, storage 3000m/2025':'Coal_CCS',
 'Electricity, at power plant/lignite, pre, pipeline 200km, storage 1000m/2025':'Coal_CCS',
 'Electricity, at BIGCC power plant 450MW, pre, pipeline 400km, storage 3000m/2025':'Biomass_CCS',
 'Electricity, at power plant/natural gas, post, pipeline 400km, storage 1000m/2025':'Natural_gas_CCS',
 'Electricity, at power plant/lignite, post, pipeline 400km, storage 3000m/2025':'Coal_CCS',
 'Electricity, at power plant/hard coal, post, pipeline 400km, storage 1000m/2025':'Coal_CCS',
 'Electricity, from CC plant, 100% SNG, truck 25km, post, pipeline 400km, storage 3000m/2025':'Biomass_CCS',
 'Electricity, at power plant/natural gas, ATR H2-CC, no CCS/2025':'Natural_gas_CCS',
 'Electricity, at power plant/hard coal, pre, pipeline 400km, storage 3000m/2025':'Coal_CCS',
 'Electricity, at power plant/lignite, IGCC, no CCS/2025':'IGCC',
 'Electricity, at power plant/hard coal, post, pipeline 200km, storage 1000m/2025':'Coal_CCS',
 'Electricity, at power plant/lignite, oxy, pipeline 400km, storage 3000m/2025':'Coal_CCS',
 'Electricity, at power plant/lignite, post, pipeline 200km, storage 1000m/2025':'Coal_CCS',
 'Electricity, at power plant/lignite, pre, pipeline 400km, storage 3000m/2025':'Coal_CCS',
 'Electricity, at power plant/natural gas, post, pipeline 200km, storage 1000m/2025':'Natural_gas_CCS',
 'Electricity, at power plant/natural gas, post, pipeline 400km, storage 3000m/2025':'Natural_gas_CCS',
 'Electricity, at BIGCC power plant 450MW, no CCS/2025':'Biomass_ST',
 'Electricity, from CC plant, 100% SNG, truck 25km, no CCS/2025':'Biomass_ST',
 'Electricity, at power plant/hard coal, oxy, pipeline 200km, storage 1000m/2025':'Coal_CCS'
    }



#Fixing name of regions WHERE???Are these names in Ecoinvent because they are not in IMAGE data
fix_names= {'CSG' : 'CN-CSG',
            'SGCC': 'CN-SGCC',
            'RFC' : 'US-RFC',
            'SERC' : 'US-SERC',
            'TRE': 'US-TRE',
            'ASCC': 'US-ASCC',
            'HICC': 'US-HICC',
            'FRCC': 'US-FRCC',
            'SPP' : 'US-SPP',
            'MRO, US only' : 'US-MRO', 
            'NPCC, US only': 'US-NPCC', 
            'WECC, US only': 'US-WECC',
             
            'IAI Area, Africa':'IAI Area 1, Africa',
            'IAI Area, South America':'IAI Area 3, South America', 
            'IAI Area, Asia, without China and GCC':'IAI Area 4&5, without China', 
            'IAI Area, North America, without Quebec':'IAI Area 2, without Quebec',
            'IAI Area, Gulf Cooperation Council':'IAI Area 8, Gulf'
            }




image_air_pollutants ={
    'Methane, fossil': 'CH4',  
    'Sulfur dioxide': 'SO2', 
    'Carbon monoxide, fossil': 'CO', 
    'Nitrogen oxides': 'NOx',
    'Dinitrogen monoxide': 'N2O'
} 



# These locations aren't found correctly by the constructive geometries library - we correct them here:
fix_names= {'CSG' : 'CN-CSG',
            'SGCC': 'CN-SGCC',
             
             'RFC' : 'US-RFC',
             'SERC' : 'US-SERC',
             'TRE': 'US-TRE',
             'ASCC': 'US-ASCC',
             'HICC': 'US-HICC',
             'FRCC': 'US-FRCC',
             'SPP' : 'US-SPP',
             'MRO, US only' : 'US-MRO', 
             'NPCC, US only': 'US-NPCC', 
             'WECC, US only': 'US-WECC',
             
             'IAI Area, Africa':'IAI Area 1, Africa',
             'IAI Area, South America':'IAI Area 3, South America', 
             'IAI Area, Asia, without China and GCC':'IAI Area 4&5, without China', 
             'IAI Area, North America, without Quebec':'IAI Area 2, without Quebec',
             'IAI Area, Gulf Cooperation Council':'IAI Area 8, Gulf'
            }