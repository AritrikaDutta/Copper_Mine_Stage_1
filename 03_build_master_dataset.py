"""
Build the final 20-column master CSV from the depletion output and block pool.
"""

import pandas as pd

# --- Paths ---
DEPLETION_FILE = "truck_block_depletion_option1_fixed_365days.csv"
BLOCK_POOL_FILE = "block_pool_option1_fixed_365days.csv"
OUTPUT_FILE = "copper_mine_master_dataset_365days.csv"

# --- Lithology code mapping ---
LITH_CODE = {
    "Andesite": "AND",
    "QMP": "QMP",
    "Granodiorite": "GRD",
    "Diorite": "DIO",
    "Granite": "GRN",
}

# --- Operational zone mapping ---
ZONE_MAP = {
    ("QMP", "Potassic"): "CORE",
    ("QMP", "Phyllic"): "CORE",
    ("QMP", "Propylitic"): "CORE",
    ("Granodiorite", "Potassic"): "CORE",
    ("Granodiorite", "Phyllic"): "CORE",
    ("Granodiorite", "Propylitic"): "CORE",
    ("Andesite", "Potassic"): "MARGIN",
    ("Andesite", "Phyllic"): "MARGIN",
    ("Andesite", "Propylitic"): "MARGIN",
    ("Diorite", "Potassic"): "MARGIN",
    ("Diorite", "Phyllic"): "MARGIN",
    ("Diorite", "Propylitic"): "MARGIN",
    ("Granite", "Potassic"): "OUTER",
    ("Granite", "Phyllic"): "OUTER",
    ("Granite", "Propylitic"): "OUTER",
    ("Granite", "Argillic"): "OUTER",
    ("Andesite", "Argillic"): "OUTER",
    ("Diorite", "Argillic"): "OUTER",
    ("Granodiorite", "Argillic"): "OUTER",
    ("QMP", "Argillic"): "OUTER",
    ("Andesite", "Advanced Argillic"): "CAP",
    ("Diorite", "Advanced Argillic"): "CAP",
    ("Granodiorite", "Advanced Argillic"): "CAP",
    ("QMP", "Advanced Argillic"): "CAP",
    ("Granite", "Advanced Argillic"): "CAP",
    ("Andesite", "Sodic-Calcic"): "CAP",
    ("Diorite", "Sodic-Calcic"): "CAP",
    ("Granodiorite", "Sodic-Calcic"): "CAP",
    ("QMP", "Sodic-Calcic"): "CAP",
    ("Granite", "Sodic-Calcic"): "CAP",
}


def main():
    print("Reading depletion file...")
    df = pd.read_csv(DEPLETION_FILE)

    print("Reading block pool...")
    pool = pd.read_csv(BLOCK_POOL_FILE, usecols=["Block_ID", "Lithology", "Alteration_Zone"])
    pool = pool.rename(columns={"Lithology": "Lithology_Name", "Alteration_Zone": "Alteration_Name"})

    print("Merging geological attributes...")
    df = df.merge(pool, on="Block_ID", how="left")

    print("Adding Lithology_Code...")
    df["Lithology_Code"] = df["Lithology_Name"].map(LITH_CODE)

    print("Adding Operational_Zone...")
    df["Operational_Zone"] = df.apply(
        lambda r: ZONE_MAP.get((r["Lithology_Name"], r["Alteration_Name"]), "UNKNOWN"), axis=1
    )

    print("Adding Operator_ID...")
    truck_nums = df["Truck_ID"].str.extract(r"T(\d+)")[0].astype(int)
    is_night = df["Shift_ID"] == "NIGHT"
    op_nums = truck_nums.where(~is_night, truck_nums + 80)
    df["Operator_ID"] = "OP-" + op_nums.astype(str).str.zfill(3)

    # Final column order (20 columns)
    columns = [
        "Roster_Date",
        "Calendar_Date",
        "Shift_ID",
        "Shovel_ID",
        "Truck_ID",
        "Operator_ID",
        "Trip_ID",
        "Block_ID",
        "Lithology_Code",
        "Lithology_Name",
        "Alteration_Name",
        "Operational_Zone",
        "Bulk_Density_t_m3",
        "Block_Tonnage_t",
        "Remaining_Tonnage_t",
        "Block_Status",
        "Payload_t",
        "Arrival_Time",
        "Departure_Time",
        "Dwell_Minutes",
    ]

    df = df[columns]
    df["Bulk_Density_t_m3"] = df["Bulk_Density_t_m3"].round(4)
    df["Block_Tonnage_t"] = df["Block_Tonnage_t"].round(2)
    df["Remaining_Tonnage_t"] = df["Remaining_Tonnage_t"].round(2)
    df["Payload_t"] = df["Payload_t"].round(2)
    df["Dwell_Minutes"] = df["Dwell_Minutes"].round(2)

    print(f"Writing {OUTPUT_FILE} ({len(df):,} rows, {len(columns)} columns)...")
    df.to_csv(OUTPUT_FILE, index=False)
    print("Done.")
    print(df.head(3).to_string())


if __name__ == "__main__":
    main()
