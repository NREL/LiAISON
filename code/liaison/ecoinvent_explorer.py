import pandas as pd

def extract_electricity_mix(updated_project_name: str, output_dir: str, results_filename: str,
                             updated_database: str, bw: 'brightway2') -> None:
    """
    Extracts electricity mix data and saves it to CSV files.

    Parameters:
    - updated_project_name (str): The name of the updated project.
    - output_dir (str): The output directory for saving CSV files.
    - results_filename (str): The filename for results (not used in the function).
    - updated_database (str): The name of the updated database.
    - bw ('brightway2'): An object of the type representing the Brightway2 database.

    Returns:
    None
    """
    bw.projects.set_current(updated_project_name)
    ei_cf_36_db = bw.Database(updated_database)

    elec_data = {
        'elec_type': [],
        'elec_amount kwh': [],
        'elec_loc': [],
        'elec_mix ratio': [],
        'database': [],
    }

    for act in ei_cf_36_db:
        if (act['name'] == 'market group for electricity, high voltage' or
                act['name'] == 'market group for electricity, low voltage') and act['location'] == 'USA':
            for exch in act.exchanges():
                if exch['type'] == 'technosphere':
                    elec_data['elec_type'].append(exch['name'])
                    elec_data['elec_amount kwh'].append(exch['amount'])
                    elec_data['elec_loc'].append(exch['location'])
                    elec_data['elec_mix ratio'].append(exch['amount'])
                    elec_data['database'].append(updated_database)

    elec_df = pd.DataFrame(elec_data)

    if not elec_df.empty:
        elec_df['total_flow'] = elec_df['elec_amount kwh']
        elec_df.to_csv(output_dir + updated_database + '_electricity_mix_raw.csv', index=False)

        elec_df_f = elec_df[['elec_type', 'database', 'total_flow']]
        elec_df_f = elec_df_f.groupby(['elec_type', 'database'])['total_flow'].agg('sum').reset_index()

        elec_df_f = elec_df_f[elec_df_f['elec_type'].str.contains('electricity production')]
        total = sum(elec_df_f['total_flow'])
        elec_df_f['total_flow'] = elec_df_f['total_flow'] / total
        elec_df_f.to_csv(output_dir + updated_database + '_electricity_mix.csv', index=False)
