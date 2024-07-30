import pandas as pd 


df1 = pd.read_csv('Ecoinvent_name_data.csv')

df2 = pd.read_csv('process_name_bridge.csv')


print(df1.columns)

print(df2.columns)

df3 = df1.merge(df2, left_on = ['Ecoinvent_name'], right_on = ['Ecoinvent_name'])

df3['Ecoinvent_code'] = df3['Ecoinvent_code2']

df3 = df3[['Common_name', 'Ecoinvent_name', 'Ecoinvent_code', 'type_of_flow']].drop_duplicates()

df3.to_csv('process_name_bridge_2.csv', index = False)