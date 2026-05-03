"""배출량 컬럼 단위를 보정한 `dummy_test_result_corrected.csv`를 생성한다."""

from pathlib import Path

import pandas as pd

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
INPUT_FILE = OUTPUT_DIR / "dummy_test_result.csv"
OUTPUT_FILE = OUTPUT_DIR / "dummy_test_result_corrected.csv"

EF_tCO2eq_per_MWh = 0.4173
EF_kgCO2eq_per_kWh = 0.4173

print(f"input_file={INPUT_FILE}")
df = pd.read_csv(INPUT_FILE)
print(f"rows={len(df):,}")

df["_orig_emission_kgCO2eq"] = df["emission_kgCO2eq"]
df["_orig_emission_tCO2eq"] = df["emission_tCO2eq"]

df["emission_tCO2eq"] = df["load_MWh"] * EF_tCO2eq_per_MWh
df["emission_kgCO2eq"] = df["load_MWh"] * 1000 * EF_kgCO2eq_per_kWh

ratio = df["emission_kgCO2eq"] / df["emission_tCO2eq"]
assert (ratio.round(6) == 1000.0).all(), "kgCO2eq / tCO2eq ratio check failed"
print("ratio_check=passed")

check_cols = [
    "datetime", "load_MWh",
    "_orig_emission_kgCO2eq", "emission_kgCO2eq",
    "_orig_emission_tCO2eq", "emission_tCO2eq"
]
print("sample_head=")
print(df[check_cols].head(3).to_string(index=False))

output_cols = [
    "datetime", "load_MWh", "month", "hour", "season", "load_type",
    "rate_won_per_kWh", "electricity_cost_won",
    "emission_kgCO2eq", "emission_tCO2eq"
]
df[output_cols].to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
print(f"output_file={OUTPUT_FILE}")
print(f"output_rows={len(df):,}")
