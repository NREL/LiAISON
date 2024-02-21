#The debugger is used for finding issues with the dataframe generated by HIPSTER matcher code. 


#We find issues using the debugger and then solve them in the HIPSTER matcher code itself.

#These issues are also listed in the Github issues of our repository. HIPSTER

#Issue 1 
#Heat and power co generation is an issue. There are duplicate processess with electricity output and heat output inside ecoinvent. 

#First thing is to search for duplication production flows in an activity

import pandas as pd
import os
import sys
print(os.getcwd())
filename=sys.argv[1]
df = pd.read_csv(filename)


df2 = df[df['type'] == 'production']

df2 = df2[['process', 'flow', 'year', 'comments', 'type',
       'process_location', 'supplying_location']]

df2['indicator'] = df2.duplicated(keep=False)

df2.to_excel('debugging_file.xlsx', index = False)

#Issue 2 
#Lignite and Coal are causing an issue. Because they need to be added by the output code is causing an issue.. 
#Resolved by removing supplying activitiy for production flows

#df = pd.read_csv('Mid_Case_ecoinvent_format.csv')
#df = pd.read_csv('Mid_Case_grid_mix_ecoinvent_format.csv')
#df = pd.read_csv('example.csv')


loc_flag = True
loc_list = ['US-NPCC-p134', 'US-WECC-p33', 'US-RFC-p80', 'US-MRO-p46', 'US-TRE-p63', 'US-RFC-p122', 'US-NPCC-p133', 'US-RFC-p79', 'US-RFC-p123', 'US-NPCC-p127', 'US-WECC-p8', 'US-NPCC-p130', 'US-NPCC-p132', 'US-RFC-p112', 'US-SPP-p66', 'US-FRCC-p101', 'US-SERC-p97', 'US-MRO-p77', 'US-SERC-p96', 'US-MRO-p78', 'US-SERC-p94', 'US-WECC-p9', 'US-WECC-p10', 'US-MRO-p70', 'US-MRO-p75', 'US-MRO-p76', 'US-SERC-p99', 'US-TRE-p67', 'US-RFC-p115', 'US-RFC-p116', 'US-SERC-p88', 'US-RFC-p117', 'US-SERC-p87', 'US-RFC-p114', 'US-SERC-p109', 'US-RFC-p111', 'US-RFC-p118', 'US-SERC-p85', 'US-WECC-p2', 'US-WECC-p21', 'US-WECC-p23', 'US-WECC-p24', 'US-WECC-p12', 'US-RFC-p121', 'US-SERC-p108', 'US-SERC-p92', 'US-SERC-p91', 'US-SERC-p93', 'US-SERC-p98', 'US-RFC-p105', 'US-SERC-p89', 'US-RFC-p107', 'US-RFC-p103', 'US-SERC-p90', 'US-WECC-p25', 'US-SERC-p81', 'US-SPP-p53', 'US-SPP-p54', 'US-SERC-p72', 'US-SPP-p55', 'US-SPP-p52', 'US-MRO-p45', 'US-SPP-p50', 'US-SPP-p51', 'US-SPP-p56', 'US-TRE-p64', 'US-TRE-p65', 'US-MRO-p69', 'US-SPP-p58', 'US-SPP-p57', 'US-SERC-p82', 'US-WECC-p29', 'US-WECC-p31', 'US-SERC-p84', 'US-WECC-p34', 'US-WECC-p26', 'US-MRO-p36', 'US-WECC-p28', 'US-MRO-p40', 'US-MRO-p41', 'US-MRO-p43', 'US-MRO-p38', 'US-MRO-p37', 'US-SERC-p83', 'US-WECC-p19', 'US-NPCC-p131', 'US-NPCC-p129', 'US-WECC-p6', 'US-WECC-p5', 'US-WECC-p13', 'US-WECC-p18', 'US-WECC-p3', 'US-WECC-p4', 'US-WECC-p17', 'US-WECC-p16', 'US-WECC-p15', 'US-WECC-p7', 'US-MRO-p74', 'US-WECC-p27', 'US-SERC-p95', 'US-WECC-p14', 'US-WECC-p1', 'US-SERC-p100', 'US-FRCC-p102', 'US-RFC-p104', 'US-SPP-p48', 'US-SPP-p47', 'US-WECC-p59', 'US-MRO-p35', 'US-SERC-p86', 'US-MRO-p68', 'US-TRE-p60', 'US-TRE-p62', 'US-WECC-p11', 'US-NPCC-p128', 'US-RFC-p126', 'US-RFC-p125', 'US-RFC-p106', 'US-SERC-p73', 'US-MRO-p44', 'US-MRO-p39', 'US-WECC-p30', 'US-RFC-p113', 'US-MRO-p42', 'US-SERC-p110', 'US-SERC-p71', 'US-TRE-p61', 'US-WECC-p32', 'US-RFC-p124', 'US-SPP-p49', 'US-WECC-p20', 'US-RFC-p119', 'US-RFC-p120', 'US-WECC-p22']
loc_list1 = ['US-NPCC-p134', 'US-WECC-p33', 'US-RFC-p80', 'US-MRO-p46', 'US-TRE-p63', 'US-RFC-p122', 'US-NPCC-p133', 'US-RFC-p79', 'US-RFC-p123', 'US-NPCC-p127', 'US-WECC-p8', 'US-NPCC-p130', 'US-NPCC-p132', 'US-RFC-p112', 'US-SPP-p66', 'US-FRCC-p101', 'US-SERC-p97', 'US-MRO-p77', 'US-SERC-p96', 'US-MRO-p78', 'US-SERC-p94', 'US-WECC-p9', 'US-WECC-p10', 'US-MRO-p70', 'US-MRO-p75', 'US-MRO-p76', 'US-SERC-p99', 'US-TRE-p67', 'US-RFC-p115', 'US-RFC-p116', 'US-SERC-p88', 'US-RFC-p117', 'US-SERC-p87', 'US-RFC-p114', 'US-SERC-p109', 'US-RFC-p111', 'US-RFC-p118', 'US-SERC-p85', 'US-WECC-p2', 'US-WECC-p21', 'US-WECC-p23', 'US-WECC-p24', 'US-WECC-p12', 'US-RFC-p121', 'US-SERC-p108', 'US-SERC-p92', 'US-SERC-p91', 'US-SERC-p93', 'US-SERC-p98', 'US-RFC-p105', 'US-SERC-p89', 'US-RFC-p107', 'US-RFC-p103', 'US-SERC-p90', 'US-WECC-p25', 'US-SERC-p81', 'US-SPP-p53']
loc_list2 = ['US-NPCC-p134', 'US-WECC-p33', 'US-RFC-p80','US']

if loc_flag == True:
       df2 = df[df['process_location'].isin(loc_list2)]

       print("Reducing dataset size")

else:
     df2=df  


df2.to_csv(filename,index=False)