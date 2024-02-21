import sys
import pandas as pd
from numpy import random
import numpy as np
from pprint import pprint
from typing import Dict

def update_uncertainty(file: pd.DataFrame, yr: float, mc_runs: int) -> Dict[str, np.ndarray]:
    """
    Update uncertainty for each input parameter in the given DataFrame for a specific year.

    Parameters:
    - file (pd.DataFrame): DataFrame containing input parameters.
    - yr (float): Year for which uncertainty needs to be updated.
    - mc_runs (int): Number of Monte Carlo runs.

    Returns:
    - Dict[str, np.ndarray]: Dictionary mapping parameter names to arrays of updated values.
    """
    unc_dictionary = {}

    scaling_factors = {
        2100.0: 1,
        2090.0: 0.5,
        2080.0: 1/3,
        2070.0: 1/4,
        2060.0: 1/5,
        2050.0: 1/6,
        2040.0: 1/7,
        2030.0: 1/8,
    }

    for index, row in file.iterrows():
        if row['input']:
            scale_factor = scaling_factors.get(yr, 1/9)
            new_val = random.normal(loc=row['value'], scale=row['value'] * scale_factor, size=mc_runs)
            unc_dictionary[row['process'] + row['flow']] = new_val

    pprint(f'Updated uncertainty dictionary for year {yr}:')
    pprint(unc_dictionary)

    return unc_dictionary

def recreate_input_file(file: pd.DataFrame, unc_dictionary: Dict[str, np.ndarray], mc_runs: int, yr: float, output_dir: str) -> None:
    """
    Recreate input files with updated values based on the Monte Carlo runs.

    Parameters:
    - file (pd.DataFrame): DataFrame containing input parameters.
    - unc_dictionary (Dict[str, np.ndarray]): Dictionary mapping parameter names to arrays of updated values.
    - mc_runs (int): Number of Monte Carlo runs.
    - yr (float): Year for which uncertainty has been updated.
    - output_dir (str): Directory where output files will be saved.

    Returns:
    - None
    """
    for r in range(mc_runs):
        if mc_foreground_flag:
            for index, row in file.iterrows():
                if row['input']:
                    file.at[index, 'value'] = unc_dictionary[row['process'] + row['flow']][r]

            name = f'{output_dir}/foreground_uncertainty_lci{r}_{yr}.csv'
            pprint(f'Recreated input file {name} with uncertainty for run {r} and year {yr}:')
            pprint(file)

            file.to_csv(name, index=False)

def mc_foreground(yr: float, mc_runs: int, mc_foreground_flag: bool, inventory_filename: str, output_dir: str) -> None:
    """
    Perform Monte Carlo simulation for foreground uncertainty and recreate input files.

    Parameters:
    - yr (float): Year for which uncertainty needs to be updated.
    - mc_runs (int): Number of Monte Carlo runs.
    - mc_foreground_flag (bool): Flag indicating whether to perform Monte Carlo for foreground uncertainty.
    - inventory_filename (str): Path to the input inventory CSV file.
    - output_dir (str): Directory where output files will be saved.

    Returns:
    - None
    """
    file = pd.read_csv(inventory_filename)
    print('Updating uncertainty', flush=True)

    unc_dictionary = update_uncertainty(file, yr, mc_runs)

    file = pd.read_csv(inventory_filename)
    recreate_input_file(file, unc_dictionary, mc_runs, yr, output_dir)

# Example usage:
# mc_foreground(2050.0, 10, True, 'your_inventory.csv', 'your_output_directory')
