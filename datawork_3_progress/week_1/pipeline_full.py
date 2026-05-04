"""지역본부별 시간대별 부하 데이터에 TOU 요금과 배출계수를 적용한다."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
OUTPUT_DIR = PROJECT_ROOT / "output"

LOAD_FILE = RAW_DIR / "(개방용) 지역본부별 시간대별 전력사용량_20241231.csv"
TARIFF_FILE = REFERENCE_DIR / "tariff_tou.csv"
EMISSION_FILE = REFERENCE_DIR / "emission_factor.csv"

DEFAULT_RESULT_FILE = OUTPUT_DIR / "result_base.csv"
DEFAULT_SUMMARY_FILE = OUTPUT_DIR / "result_base_monthly_summary.csv"
DEFAULT_SAMPLE_FILE = OUTPUT_DIR / "week1_prepared_sample.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Base 시나리오 결과 파일 생성"
    )
    parser.add_argument(
        "--emission-basis",
        choices=["2023", "avg_2021_2023"],
        default="2023",
        help="배출계수 기준",
    )
    parser.add_argument(
        "--result-file",
        type=Path,
        default=DEFAULT_RESULT_FILE,
        help="전체 결과 CSV 경로",
    )
    parser.add_argument(
        "--summary-file",
        type=Path,
        default=DEFAULT_SUMMARY_FILE,
        help="월별 요약 CSV 경로",
    )
    parser.add_argument(
        "--sample-file",
        type=Path,
        default=DEFAULT_SAMPLE_FILE,
        help="샘플 CSV 경로",
    )
    return parser.parse_args()


def load_emission_factor(basis: str) -> tuple[float, float, str]:
    emission = pd.read_csv(EMISSION_FILE, encoding="utf-8-sig")

    basis_key = "2023" if basis == "2023" else "2021-2023평균"
    row = emission[
        (emission["기준연도"].astype(str) == basis_key) & (emission["구분"] == "소비단")
    ]
    if row.empty:
        raise ValueError(f"Emission factor row not found for basis={basis_key}")

    record = row.iloc[0]
    ef_t = float(record["CO2eq_tCO2eq_per_MWh"])
    ef_kg = float(record["CO2eq_kgCO2eq_per_kWh"])
    label = f"{basis_key} 소비단"
    return ef_t, ef_kg, label


def build_base_dataframe(emission_basis: str) -> pd.DataFrame:
    load = pd.read_csv(LOAD_FILE, encoding="cp949", parse_dates=["기준일자"])
    tariff = pd.read_csv(TARIFF_FILE, encoding="utf-8-sig")
    ef_t, ef_kg, ef_label = load_emission_factor(emission_basis)

    load = load.rename(
        columns={
            "기준일자": "date",
            "기준시": "hour_ending",
            "본부명": "headquarter",
            "전력사용량(MWh)": "load_MWh",
            "고객호수": "customer_count",
        }
    )

    load["hour_ending"] = load["hour_ending"].astype(int)
    load["month"] = load["date"].dt.month
    load["hour"] = load["hour_ending"] - 1

    merged = load.merge(
        tariff,
        on=["month", "hour"],
        how="left",
        validate="many_to_one",
    )

    if merged["rate_won_per_kWh"].isna().any():
        missing = int(merged["rate_won_per_kWh"].isna().sum())
        raise ValueError(f"Tariff join failed: {missing} rows have null rate_won_per_kWh")

    if not merged["hour"].between(0, 23).all():
        raise ValueError("Hour conversion failed: values outside 0~23 exist")

    merged["electricity_cost_won"] = merged["load_MWh"] * merged["rate_won_per_kWh"] * 1000
    merged["emission_tCO2eq"] = merged["load_MWh"] * ef_t
    merged["emission_kgCO2eq"] = merged["load_MWh"] * 1000 * ef_kg
    merged["emission_factor_basis"] = ef_label

    ratio = merged["emission_kgCO2eq"] / merged["emission_tCO2eq"]
    if not (ratio.round(6) == 1000.0).all():
        raise ValueError("Emission ratio validation failed: kg/t ratio is not 1000")

    merged["year"] = merged["date"].dt.year
    merged = merged.sort_values(["date", "headquarter", "hour_ending"]).reset_index(drop=True)
    merged["date"] = merged["date"].dt.strftime("%Y-%m-%d")

    return merged[
        [
            "date",
            "year",
            "month",
            "hour_ending",
            "hour",
            "headquarter",
            "customer_count",
            "load_MWh",
            "season",
            "load_type",
            "rate_won_per_kWh",
            "base_charge_won_per_kW",
            "electricity_cost_won",
            "emission_factor_basis",
            "emission_tCO2eq",
            "emission_kgCO2eq",
        ]
    ]


def build_monthly_summary(base_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        base_df.groupby(["year", "month", "headquarter"], as_index=False)
        .agg(
            hour_count=("hour", "count"),
            load_MWh=("load_MWh", "sum"),
            electricity_cost_won=("electricity_cost_won", "sum"),
            emission_tCO2eq=("emission_tCO2eq", "sum"),
            emission_kgCO2eq=("emission_kgCO2eq", "sum"),
        )
        .sort_values(["year", "month", "headquarter"])
        .reset_index(drop=True)
    )
    return summary


def build_week1_sample(base_df: pd.DataFrame) -> pd.DataFrame:
    sample = base_df[
        (base_df["date"] == "2024-12-31") & (base_df["headquarter"] == "경기북부본부")
    ].copy()
    if sample.empty:
        sample = base_df.head(24).copy()
    return sample


def main() -> None:
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    base_df = build_base_dataframe(args.emission_basis)
    summary_df = build_monthly_summary(base_df)
    sample_df = build_week1_sample(base_df)

    args.result_file.parent.mkdir(parents=True, exist_ok=True)
    args.summary_file.parent.mkdir(parents=True, exist_ok=True)
    args.sample_file.parent.mkdir(parents=True, exist_ok=True)

    base_df.to_csv(args.result_file, index=False, encoding="utf-8-sig")
    summary_df.to_csv(args.summary_file, index=False, encoding="utf-8-sig")
    sample_df.to_csv(args.sample_file, index=False, encoding="utf-8-sig")

    print(f"result_file={args.result_file}")
    print(f"rows={len(base_df):,}")
    print(f"date_range={base_df['date'].min()} ~ {base_df['date'].max()}")
    print(f"headquarter_count={base_df['headquarter'].nunique()}")
    print(f"emission_basis={base_df['emission_factor_basis'].iloc[0]}")
    print(f"summary_file={args.summary_file}")
    print(f"summary_rows={len(summary_df):,}")
    print(f"sample_file={args.sample_file}")
    print(f"sample_rows={len(sample_df):,}")


if __name__ == "__main__":
    main()
