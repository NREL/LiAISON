"""reeds_ecoinvent_matcher.py
Clean, end‑to‑end ReEDS → ecoinvent pipeline
Author: NREL – TJ (2025‑06‑27)

This single script covers two tasks:
1. Build *U.S. grid‑mix* technosphere inventories for each year.
2. Build *technology‑specific* inventories (production, technosphere, biosphere) and
   back‑fill missing exchanges using ecoinvent v3.8, ready for Brightway2 import.

Key improvements vs. legacy notebooks/scripts
──────────────────────────────────────────────
✓ All constants collected at top (no magic strings).
✓ Modular, reusable helpers with docstrings.
✓ Robust path handling via os.path.join.
✓ No chained assignments; `.loc` used explicitly.
✓ Weighted‑average helper centralised.
✓ Extensive logging instead of print‑spam.
✓ Debug CSV dumping behind `DEBUG` flag.
✓ Year loop drives both grid‑mix and tech‑level outputs.

Run: `python reeds_ecoinvent_matcher.py --debug` (optional) or without.
"""

from __future__ import annotations
import argparse
import logging
import os
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────
BRIDGE_DIR = Path("./")               # directory containing all bridge .xlsx files
REEDS_OUTPUT_DIR = Path("./ReEDS_Outputs")
OUTPUT_DIR = Path("./outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

SCENARIO_BASE = "Mid_Case"
YEARS: List[int] = [2020, 2024, 2028, 2032, 2036, 2042, 2048]
DEBUG = False  # toggled by CLI

# ──────────────────────────────────────────────────────────────────────────────
# Logging setup
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ──────────────────────────────────────────────────────────────────────────────

def xl(name: str) -> pd.DataFrame:
    """Load an Excel file from `BRIDGE_DIR`."""
    fp = BRIDGE_DIR / name
    if not fp.exists():
        raise FileNotFoundError(fp)
    return pd.read_excel(fp)


def save_dbg(df: pd.DataFrame, name: str) -> None:
    if DEBUG:
        df.to_csv(OUTPUT_DIR / f"DEBUG_{name}.csv", index=False)


def w_avg(df: pd.DataFrame, value: str, weight: str) -> float:
    """Row‑wise weighted average (skip divide‑by‑zero)."""
    d, w = df[value], df[weight]
    return (d * w).sum() / w.sum() if w.sum() else 0.0

# ──────────────────────────────────────────────────────────────────────────────
# Bridge‑file bundle (loaded once)
# ──────────────────────────────────────────────────────────────────────────────
BRIDGES: Dict[str, pd.DataFrame] = {
    "biosphere": xl("BiosphereBridgeFile.xlsx"),
    "production": xl("ProductionBridgeFile.xlsx"),
    "technosphere": xl("TechnosphereBridgeFile.xlsx"),
    "tech_fuel": xl("ReEDS_Tech_Fuel.xlsx"),
    "regions": xl("ReEDS_NERC.xlsx"),
    "tech_map": xl("ReEDS_EcoInvent_TechMapping.xlsx"),
    "ecoinvent_raw": xl("ecoinvent38_USA.xlsx").fillna("no information"),
}

# Clean ecoinvent electricity flows – reuse for all years
prod_mask = BRIDGES["ecoinvent_raw"]["type_of_flow"] == "production"
_elec = BRIDGES["ecoinvent_raw"][prod_mask & BRIDGES["ecoinvent_raw"]["flows"].str.contains("electricity", case=False)]["output"]
ECOINVENT_CLEAN = BRIDGES["ecoinvent_raw"].merge(_elec, on="output")
ECOINVENT_CLEAN.loc[prod_mask, ["inpu_t", "supplying activity"]] = "No Information"

del BRIDGES["ecoinvent_raw"]  # free memory

# ──────────────────────────────────────────────────────────────────────────────
# Core builders
# ──────────────────────────────────────────────────────────────────────────────

def build_grid_mix(reeds_year: pd.DataFrame) -> pd.DataFrame:
    """Return US‑wide grid‑mix technosphere dataset for given year."""
    prod_long = (
        reeds_year.melt(id_vars=["ReEDS_Tech", "BA", "Year"],
                        value_vars=["Generation (MWh)"],
                        var_name="ReEDS_flow", value_name="Amount")
        .merge(BRIDGES["production"], on=["ReEDS_flow", "ReEDS_Tech"])
        .merge(BRIDGES["tech_map"][["ReEDS_Tech"]], on="ReEDS_Tech")
        .merge(BRIDGES["regions"], left_on="BA", right_on="Region")
        .dropna()
        .drop_duplicates()
    )
    prod_long["Ecoinvent_process_to_be_created"] = (
        "Electricity production_" + prod_long["ReEDS_Tech"] + "_ReEDS"
    )

    df = prod_long.copy()
    df["type_of_flow"] = "technosphere"
    df["location"] = df["NERC"] + "-" + df["Region"]
    df["input"] = "TRUE"
    df["process_location"] = "US"
    df["supplying_location"] = df["location"]

    df = df.rename(columns={
        "ReEDS_Tech": "process",
        "flows": "flow",
        "Year": "year",
        "type_of_flow": "type",
        "Amount": "value",
        "Unit": "unit",
    })

    df["process"] = "ReEDS_US_Grid_Mix"
    df["flow"] = df["Ecoinvent_process_to_be_created"]
    df["comments"] = "none"

    # Re‑scale to unity
    df_sum = df["value"].sum()
    df["value"] = df["value"] / df_sum if df_sum else df["value"]

    # Add production row
    prod_row = {
        "process": "ReEDS_US_Grid_Mix",
        "flow": "electricity high voltage",
        "value": 1.0,
        "unit": "kilowatt hour",
        "input": "FALSE",
        "year": reeds_year["Year"].iloc[0],
        "type": "production",
        "process_location": "US",
        "supplying_location": "No information",
        "comments": "none",
    }
    df = pd.concat([df, pd.DataFrame([prod_row])]).sort_values("supplying_location")
    return df


def build_reeds_restructured(reeds_year: pd.DataFrame) -> pd.DataFrame:
    """Combine production, technosphere, biosphere into a single long dataframe."""

    # Biosphere
    bio = (
        reeds_year[["ReEDS_Tech", "BA", "Year", "EmissionsType", "EmissionsRate (kg/kWh)"]]
        .merge(BRIDGES["biosphere"], left_on="EmissionsType", right_on="ReEDS_flow")
    )
    bio["Amount"], bio["Unit"] = bio["EmissionsRate (kg/kWh)"], "kilogram"
    bio = bio[["ReEDS_Tech", "ReEDS_flow", "BA", "Year", "EcoInvent_flow", "Type", "Amount", "Unit"]]

    # Production
    prod = (
        reeds_year.melt(id_vars=["ReEDS_Tech", "BA", "Year"], value_vars=["Generation (MWh)"],
                        var_name="ReEDS_flow", value_name="Amount")
        .merge(BRIDGES["production"], on=["ReEDS_flow", "ReEDS_Tech"])
    )
    prod["Amount"] = 1

    # Technosphere
    tech = (
        reeds_year[["ReEDS_Tech", "BA", "Year", "Fuel Input (kg or m3 / kWh)"]]
        .merge(BRIDGES["tech_fuel"], on="ReEDS_Tech")
        .merge(BRIDGES["technosphere"], on=["ReEDS_flow", "Unit"])
    )
    tech["Amount"] = tech["Fuel Input (kg or m3 / kWh)"]
    tech = tech[["ReEDS_Tech", "BA", "Year", "ReEDS_flow", "EcoInvent_flow", "Amount", "Type", "Unit"]]

    # Combine and add region data
    df = pd.concat([prod, tech, bio])
    df = df.merge(BRIDGES["regions"], left_on="BA", right_on="Region").drop(columns="BA")

    df["Ecoinvent_process_to_be_created"] = (
        "Electricity production_" + df["ReEDS_Tech"] + "_ReEDS"
    )
    df = df.sort_values("ReEDS_Tech")
    return df


def fill_with_ecoinvent(reeds_df: pd.DataFrame) -> pd.DataFrame:
    """For each unique (tech, region, year) build completed inventory using ecoinvent."""
    tech_fuel_df = reeds_df[[
        "ReEDS_Tech", "Region", "NERC", "Ecoinvent_process_to_be_created", "Year"
    ]].drop_duplicates()

    out_frames = []
    tech_map2 = BRIDGES["tech_map"][["ReEDS_Tech", "EcoInvent_Tech", "Weight"]]

    for _, row in tech_fuel_df.iterrows():
        subset = reeds_df[
            (reeds_df["Ecoinvent_process_to_be_created"] == row["Ecoinvent_process_to_be_created"]) &
            (reeds_df["Region"] == row["Region"]) &
            (reeds_df["Year"] == row["Year"])
        ]

        # Map ReEDS tech to eco tech
        subset_map = subset[[
            "ReEDS_Tech", "Region", "NERC", "Year", "Ecoinvent_process_to_be_created"
        ]].drop_duplicates().merge(
            tech_map2[["ReEDS_Tech", "EcoInvent_Tech"]], on="ReEDS_Tech"
        )

        # Exact region match first
        merged = ECOINVENT_CLEAN.merge(
            subset_map,
            left_on=["process", "process location"],
            right_on=["EcoInvent_Tech", "NERC"]
        )

        # Fallback without region
        if merged.empty:
            merged = ECOINVENT_CLEAN.merge(
                subset_map, left_on="process", right_on="EcoInvent_Tech"
            )

        if merged.empty:
            logger.warning("No ecoinvent match for %s", row.to_dict())
            continue

        # Bring in Amount from ReEDS where available
        new_data = subset[["Amount", "EcoInvent_flow"]].drop_duplicates()
        merged = merged.merge(new_data, left_on="flows", right_on="EcoInvent_flow", how="left")
        merged["Amount"] = merged["Amount"].fillna(0)
        merged["amount"] = np.where(merged["Amount"] != 0, merged["Amount"], merged["amount"])

        merged = merged.merge(tech_map2, on=["ReEDS_Tech", "EcoInvent_Tech"])
        merged["amount"] *= merged["Weight"]
        merged["Weight"] = 1

        # Weighted averaging across duplicated flows
        grp_cols = [
            "ReEDS_Tech", "Region", "Year", "NERC", "flows", "type_of_flow", "unit",
            "Ecoinvent_process_to_be_created", "inpu_t", "supplying activity"
        ]
        merged = merged.groupby(grp_cols).apply(w_avg, "amount", "Weight").reset_index(name="amount")
        out_frames.append(merged)

    if not out_frames:
        return pd.DataFrame()

    result = pd.concat(out_frames)
    return result


def brightway_format(df: pd.DataFrame) -> pd.DataFrame:
    df["location"] = df["NERC"] + "-" + df["Region"]
    df["input"] = np.where(df["type_of_flow"] == "technosphere", "TRUE", "FALSE")
    df["process_location"] = df["location"]
    df["supplying_location"] = np.where(
        df["type_of_flow"] == "production", df["location"], "US")

    df = df.rename(columns={
        "ReEDS_Tech": "process",
        "flows": "flow",
        "Year": "year",
        "type_of_flow": "type",
        "amount": "value",
    })

    df["process"] = df["Ecoinvent_process_to_be_created"]
    df["comments"] = np.where(df["type"] == "biosphere", "stack", "none")

    cols = [
        "process", "flow", "value", "unit", "input", "year", "comments", "type",
        "process_location", "supplying_location"
    ]
    return df[cols]

# ──────────────────────────────────────────────────────────────────────────────
# Main driver
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    reeds_raw = pd.read_csv(REEDS_OUTPUT_DIR / f"{SCENARIO_BASE}_output_BA.csv")
    for yr in YEARS:
        logger.info("Year %s", yr)
        yr_df = reeds_raw[reeds_raw["Year"] == yr]

        # 1) Grid mix
        grid_mix_df = build_grid_mix(yr_df)
        grid_mix_df.to_csv(OUTPUT_DIR / f"{SCENARIO_BASE}{yr}_grid_mix.csv", index=False)

        # 2) Tech‑level inventory
        restruct = build_reeds_restructured(yr_df)
        save_dbg(restruct, f"restructured_{yr}")

        filled = fill_with_ecoinvent(restruct)
        if filled.empty:
            logger.warning("No filled inventory for %s", yr)
            continue

        bw_df = brightway_format(filled)
        bw_df.to_csv(OUTPUT_DIR / f"{SCENARIO_BASE}{yr}_brightway.csv", index=False)
        logger.info("Saved inventory for %s", yr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ReEDS → ecoinvent matcher")
    parser.add_argument("--debug", action="store_true", help="Dump intermediate CSVs")
    args = parser.parse_args()
    DEBUG = args.debug
    main()
