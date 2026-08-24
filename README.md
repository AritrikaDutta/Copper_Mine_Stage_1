# Copper Mine Stage 1 — Synthetic Dataset Pipeline

Regenerate the **47-column, 365-day** open-pit copper mine trip dataset from scratch.

Final deliverable after a full run:

`copper_mine_final_with_geomet_365days.csv` (~875,846 trips)

Design details: [`docs/COPPER_MINE_FINAL_DATASET_REFERENCE.md`](docs/COPPER_MINE_FINAL_DATASET_REFERENCE.md)

---

## Setup

```bash
cd Copper_mine_Stage_1
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

Run every script from **this folder** so relative CSV paths resolve correctly.

Random seed across the pipeline is **42** (reproducible).

---

## Run order

Execute steps **in order**. Steps `04a`–`04e` can run in any order relative to each other, but all five must finish before step `05`.

| Step | Script | What it does | Main output(s) |
|---|---|---|---|
| 1 | `01_truck_timeline.py` | Fleet timeline (80 trucks, 365 days) | `truck_simulation_365_days.csv` |
| 2 | `02_block_depletion.py` | Block pool, shovel queues, trip→block depletion | `block_pool_option1_fixed_365days.csv`, `shovel_subpools_option1_fixed_365days.csv`, `shovel_queues_option1_fixed_365days.csv`, `truck_block_depletion_option1_fixed_365days.csv`, `option1_validation_report_365days.txt` |
| 3 | `03_build_master_dataset.py` | Join depletion + geology into 20-col master | `copper_mine_master_dataset_365days.csv` |
| 4a | `04a_andesite_mineralogy.py` | Andesite domain chemistry | `Andesite_data.csv` |
| 4b | `04b_qmp_mineralogy.py` | QMP domain chemistry | `QMP_data.csv` |
| 4c | `04c_granodiorite_mineralogy.py` | Granodiorite domain chemistry | `Granodiorite_data.csv` |
| 4d | `04d_granite_mineralogy.py` | Granite domain chemistry | `Granite_data.csv` |
| 4e | `04e_diorite_mineralogy.py` | Diorite domain chemistry | `Diorite_data.csv` |
| 5 | `05_merge_mineralogy.py` | 1:1 shuffle-merge chemistry onto master | `copper_mine_final_combined_365days.csv` (36 cols), `merge_mineralogy_validation.txt` |
| 6 | `06_calculate_geomet.py` | Derived geometallurgical columns | **`copper_mine_final_with_geomet_365days.csv` (47 cols)** |

### Example (Windows PowerShell)

```powershell
python 01_truck_timeline.py
python 02_block_depletion.py
python 03_build_master_dataset.py
python 04a_andesite_mineralogy.py
python 04b_qmp_mineralogy.py
python 04c_granodiorite_mineralogy.py
python 04d_granite_mineralogy.py
python 04e_diorite_mineralogy.py
python 05_merge_mineralogy.py
python 06_calculate_geomet.py
```

---

## Runtime notes

- Steps 1–2 are the longest (full-year fleet + depletion).
- Intermediate CSVs are written next to the scripts (same folder). They are **not** committed here on purpose — regenerate locally.
- Disk: expect several GB of intermediates plus the final CSV.
- Do not rename the intermediate CSV filenames unless you also edit the constants inside the scripts that read them.

---

## Partial regenerations

| If you change… | Re-run from… |
|---|---|
| Truck timing / fleet rules | Step 1 onward |
| Block pool / dispatch / depletion | Step 2 onward (keep step 1 CSV) |
| Master column layout / lithology labels | Step 3 onward |
| One lithology’s chemistry model | That `04*` script, then 5–6 |
| Geomet formulas only | Step 6 only (keep combined CSV) |

---

## Repository layout

```text
Copper_mine_Stage_1/
├── README.md
├── requirements.txt
├── 01_truck_timeline.py
├── 02_block_depletion.py
├── 03_build_master_dataset.py
├── 04a_andesite_mineralogy.py
├── 04b_qmp_mineralogy.py
├── 04c_granodiorite_mineralogy.py
├── 04d_granite_mineralogy.py
├── 04e_diorite_mineralogy.py
├── 05_merge_mineralogy.py
├── 06_calculate_geomet.py
└── docs/
    └── COPPER_MINE_FINAL_DATASET_REFERENCE.md
```

GitHub tip: add a `.gitignore` that excludes `*.csv` (and optionally `.venv/`) before your first push so large generated files stay local.
