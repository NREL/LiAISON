import os
import time
import secrets
import pandas as pd

from liaison.lci_calculator import (
    liaison_calc,
    search_dictionary,
    search_index_reader,
    lcia_traci_run,
    lcia_recipe_run  # Premise GWP not implemented
)
from liaison.search_activity_ecoinvent import search_activity_in_ecoinvent
from liaison.edit_activity_ecoinvent import user_controlled_editing_ecoinvent_activity


def reset_project(
    updated_project_name: str,
    number: str,
    project: str,
    updated_database: str,
    bw
) -> tuple[str, str]:
    """
    Remove any existing project copy and create a fresh copy of a Brightway2 project.

    This function ensures a unique project by appending `number` to `project`, deletes any
    pre-existing copy, then copies and switches to the new project context.

    Parameters
    ----------
    updated_project_name : str
        Name of the Brightway2 project to copy from.
    number : str
        Unique token appended to the project name to avoid collisions.
    project : str
        Base name for the new project.
    updated_database : str
        Database name to set under the new project (returned unchanged).
    bw : module
        Brightway2 module instance.

    Returns
    -------
    (str, str)
        - project_name: new project name (project_number)
        - updated_database: unchanged database name
    """
    project_name = f"{project}_{number}"
    try:
        print(f"Trying to delete project {project_name}...", flush=True)
        bw.projects.delete_project(project_name, delete_dir=True)
        print("Project deleted.", flush=True)
    except Exception:
        print("Project does not exist, skipping deletion.", flush=True)

    bw.projects.set_current(updated_project_name)
    print(f"Entered project {updated_project_name}.", flush=True)
    print("Databases:", bw.databases, flush=True)

    try:
        bw.projects.copy_project(project_name, switch=False)
        print("Project copied successfully.", flush=True)
    except Exception:
        bw.projects.purge_deleted_directories()
        bw.projects.copy_project(project_name, switch=False)
        print("Project copied after purging deleted directories.", flush=True)

    bw.projects.set_current(project_name)
    print(f"Switched to new project {project_name}.", flush=True)
    print("Databases:", bw.databases, flush=True)
    return project_name, updated_database


def main_run(
    lca_project: str,
    updated_project_name: str,
    year_of_study: str,
    results_filename: str,
    mc_foreground_flag: bool,
    lca_flag: bool,
    region_sensitivity_flag: bool,
    edit_ecoinvent_user_controlled: bool,
    region: str,
    data_dir: str,
    primary_process: str,
    process_under_study: str,
    location_under_study: str,
    unit_under_study: str,
    updated_database: str,
    mc_runs: int,
    functional_unit: str,
    inventory_filename: str,
    output_dir: str,
    bw
) -> None:
    """
    Execute LCIA workflows: single-run, Monte Carlo, and regional sensitivity.

    Orchestrates:
      1. Copying the Brightway2 project.
      2. Searching or loading the foreground inventory.
      3. Optional user editing of ecoinvent activities.
      4. Running TRACI and RECIPE LCIA methods.
      5. Outputting results and cleaning up.

    Parameters
    ----------
    lca_project : str
        Base name for copying projects.
    updated_project_name : str
        Existing project to copy from.
    year_of_study : str
        Used in activity editing.
    results_filename : str
        Prefix for result CSVs.
    mc_foreground_flag : bool
        If True, Monte Carlo sampling on foreground.
    lca_flag : bool
        If False, skip LCIA.
    region_sensitivity_flag : bool
        If True, modify inventory for a single region.
    edit_ecoinvent_user_controlled : bool
        If True, enable user editing on ecoinvent activities.
    region : str
        Region code for sensitivity.
    data_dir : str
        Directory for input and generated files.
    primary_process : str
        Identifier for the main activity.
    process_under_study : str
        Name of the process to lookup.
    location_under_study : str
        Location for process lookup.
    unit_under_study : str
        Unit for process lookup.
    updated_database : str
        Database name including scenario and year.
    mc_runs : int
        Number of Monte Carlo iterations.
    functional_unit : str
        Functional unit for LCIA calls.
    inventory_filename : str
        Path to the base inventory CSV.
    output_dir : str
        Directory for writing outputs.
    bw : module
        Brightway2 module instance.

    Returns
    -------
    None
        Writes CSVs and removes temporary projects.
    """
    print(f"\nDatabase: {updated_database}", flush=True)
    print("Starting LCA runs...\n", flush=True)
    yr = updated_database[10:14]
    number = secrets.token_hex(8)
    r = ""

    def lca_runner(
        db: str,
        r: str,
        mc_runs: int,
        mc_foreground_flag: bool,
        lca_flag: bool,
        functional_unit: str,
        run_filename: str
    ) -> pd.DataFrame | None:
        """
        Internal helper that performs one LCIA (single or Monte Carlo) run.

        Parameters
        ----------
        db : str
            Database name for the run.
        r : str
            Run identifier suffix for filenames.
        mc_runs : int
            Number of Monte Carlo samples.
        mc_foreground_flag : bool
            If True, enable Monte Carlo sampling.
        lca_flag : bool
            If False, skip LCIA.
        functional_unit : str
            Functional unit parameter for LCIA.
        run_filename : str
            CSV path for the foreground inventory.

        Returns
        -------
        pd.DataFrame or None
            DataFrame of results, or None if skipped/failed.
        """
        project_name, db = reset_project(
            updated_project_name, number, lca_project, updated_database, bw
        )
        process_dict = search_dictionary(db, bw)
        searched = search_activity_in_ecoinvent(
            process_dict,
            process_under_study,
            location_under_study,
            unit_under_study,
            run_filename,
            data_dir
        )
        if isinstance(searched, str):
            print(f"Reading inventory CSV: {run_filename}", flush=True)
            df_inventory = pd.read_csv(run_filename)
            process_dict = liaison_calc(db, df_inventory, bw)
        else:
            if edit_ecoinvent_user_controlled:
                run_filename = user_controlled_editing_ecoinvent_activity(
                    searched, year_of_study, location_under_study, output_dir
                )
                print("Activity edited and saved.", flush=True)
            process_dict = liaison_calc(db, run_filename, bw)

        if not lca_flag:
            return None

        try:
            activity = search_index_reader(
                process_under_study,
                location_under_study,
                unit_under_study,
                process_dict
            )
            res_traci, n_traci = lcia_traci_run(
                db, activity, functional_unit, mc_foreground_flag, mc_runs, bw
            )
            res_recipe, n_recipe = lcia_recipe_run(
                db, activity, functional_unit, mc_foreground_flag, mc_runs, bw
            )
            res_premise, n_premise = {}, 0

            records: list[dict] = []
            for data, count, method_name in [
                (res_traci, n_traci, "TRACI2.1"),
                (res_recipe, n_recipe, "RECIPE"),
                (res_premise, n_premise, "IPCC 2013")
            ]:
                df = pd.DataFrame.from_dict(data, orient="index")
                for idx in range(count):
                    name, val, unit_name = df["result"][0][idx]
                    records.append({
                        "lcia": name,
                        "value": val,
                        "unit": unit_name,
                        "year": db,
                        "method": method_name
                    })

            lcia_df = pd.DataFrame(records)
            out_path = os.path.join(
                output_dir,
                f"{results_filename}{r}_{db}_{primary_process}.csv"
            )
            lcia_df.to_csv(out_path, index=False)
            print(
                f"LCA complete for {process_under_study} ({location_under_study}).",
                flush=True
            )
            return lcia_df
        except Exception:
            print(
                "Warning: LCA calculation failed. Check inputs and inventory.",
                flush=True
            )
            return None

    run_file = inventory_filename
    if region_sensitivity_flag:
        df_base = pd.read_csv(inventory_filename)
        df_base["process_location"] = region
        df_base["supplying_location"] = region
        print("Regional sensitivity analysis starts.", flush=True)
        run_file = os.path.join(
            data_dir, f"sensitivity_{updated_database}_{yr}.csv"
        )
        df_base.to_csv(run_file, index=False)

    if mc_foreground_flag:
        lca_runner(
            updated_database,
            r,
            mc_runs,
            mc_foreground_flag,
            lca_flag,
            functional_unit,
            run_file
        )
    else:
        lca_runner(
            updated_database,
            r,
            mc_runs,
            mc_foreground_flag,
            lca_flag,
            functional_unit,
            run_file
        )

    try:
        bw.projects.delete_project(bw.projects.current, delete_dir=True)
        print("Cleaned up temporary project.", flush=True)
    except Exception:
        print("Issue deleting temporary project.", flush=True)
