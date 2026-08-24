"""
Merge 16 chemistry columns from the five lithology mineralogy CSVs
onto copper_mine_master_dataset_365days.csv.

Pairing rule:
  - Match on (Lithology, Alteration) with master (Lithology_Name, Alteration_Name)
  - Shuffle mineralogy rows inside each combination only
  - Attach 1 chemistry row per trip row

Assumptions:
  - All five mineralogy CSVs already contain:
      Lithology, Alteration, Chalcopyrite, Bornite, Pyrite, Chalcocite,
      Covellite, Copper_Total, Sulfur, Iron, Aluminium, Magnesium, Clay,
      Carbonate, Arsenic, Lead, Zinc, Mercury
  - Row counts in the mineralogy CSVs match master trip counts by
    (Lithology, Alteration)
"""

from __future__ import annotations

import pandas as pd


SEED = 42

MASTER_FILE = "copper_mine_master_dataset_365days.csv"
OUTPUT_FILE = "copper_mine_final_combined_365days.csv"
VALIDATION_REPORT = "merge_mineralogy_validation.txt"

MINERALOGY_FILES = [
    "Andesite_data.csv",
    "QMP_data.csv",
    "Granodiorite_data.csv",
    "Granite_data.csv",
    "Diorite_data.csv",
]

CHEMISTRY_COLUMNS = [
    "Chalcopyrite",
    "Bornite",
    "Pyrite",
    "Chalcocite",
    "Covellite",
    "Copper_Total",
    "Sulfur",
    "Iron",
    "Aluminium",
    "Magnesium",
    "Clay",
    "Carbonate",
    "Arsenic",
    "Lead",
    "Zinc",
    "Mercury",
]


def load_mineralogy() -> pd.DataFrame:
    frames = []
    required_cols = ["Lithology", "Alteration"] + CHEMISTRY_COLUMNS

    for path in MINERALOGY_FILES:
        df = pd.read_csv(path)
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"{path} is missing required columns: {missing}")
        frames.append(df[required_cols].copy())

    mineralogy = pd.concat(frames, ignore_index=True)
    return mineralogy


def main() -> None:
    print("Loading master dataset...")
    master = pd.read_csv(MASTER_FILE)
    master["_orig_order"] = range(len(master))

    print("Loading mineralogy datasets...")
    mineralogy = load_mineralogy()

    master["combo"] = (
        master["Lithology_Name"].astype(str) + "|" + master["Alteration_Name"].astype(str)
    )
    mineralogy["combo"] = (
        mineralogy["Lithology"].astype(str) + "|" + mineralogy["Alteration"].astype(str)
    )

    report_lines = []
    merged_parts = []

    master_combos = set(master["combo"].unique())
    mineralogy_combos = set(mineralogy["combo"].unique())

    only_master = sorted(master_combos - mineralogy_combos)
    only_mineralogy = sorted(mineralogy_combos - master_combos)

    if only_master:
        report_lines.append(f"Combos only in master: {only_master}")
    if only_mineralogy:
        report_lines.append(f"Combos only in mineralogy: {only_mineralogy}")

    common_combos = sorted(master_combos & mineralogy_combos)
    if not common_combos:
        raise RuntimeError("No common (Lithology, Alteration) combinations found.")

    for combo in common_combos:
        trips = master[master["combo"] == combo].copy()
        chem = mineralogy[mineralogy["combo"] == combo][CHEMISTRY_COLUMNS].copy()

        n_trips = len(trips)
        n_chem = len(chem)
        report_lines.append(f"{combo}: trips={n_trips:,}, mineralogy={n_chem:,}")

        if n_trips != n_chem:
            raise RuntimeError(
                f"Count mismatch for {combo}: trips={n_trips}, mineralogy={n_chem}"
            )

        chem = chem.sample(frac=1, random_state=SEED).reset_index(drop=True)
        trips = trips.reset_index(drop=True)

        part = pd.concat([trips, chem], axis=1)
        merged_parts.append(part)

    final = pd.concat(merged_parts, ignore_index=True)
    final = final.sort_values("_orig_order").reset_index(drop=True)

    master_cols = [c for c in master.columns if c not in ["_orig_order", "combo"]]
    final = final[master_cols + CHEMISTRY_COLUMNS]

    print(f"Writing {OUTPUT_FILE} ({len(final):,} rows, {len(final.columns)} columns)...")
    final.to_csv(OUTPUT_FILE, index=False)

    report_lines.insert(0, f"Master rows: {len(master):,}")
    report_lines.insert(1, f"Final rows: {len(final):,}")
    report_lines.insert(2, f"Final columns: {len(final.columns)}")
    report_lines.insert(3, "-" * 40)

    with open(VALIDATION_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("Done.")
    print(f"Validation report: {VALIDATION_REPORT}")


if __name__ == "__main__":
    main()
