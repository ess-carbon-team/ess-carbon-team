# Base Pipeline Validation (2026-05-03)

- 상태: 완료
- 대상 스크립트: `scripts/pipeline_full.py`

## 1. 입력 파일

- `data/raw/(개방용) 지역본부별 시간대별 전력사용량_20241231.csv`
- `data/reference/tariff_tou.csv`
- `data/reference/emission_factor.csv`

## 2. 처리 내용

1. 부하 원본에서 `month`와 `hour`를 생성한다.
2. `hour = 기준시 - 1` 규칙을 적용한다.
3. `month`, `hour` 기준으로 TOU 요금표를 결합한다.
4. `2023 소비단` 배출계수를 적용한다.
5. 전기요금과 배출량 컬럼을 계산한다.
6. 전체 결과, 월별 요약, 확인용 샘플 파일을 저장한다.

## 3. 생성 파일

| 파일 | 설명 |
|---|---|
| `output/result_base.csv` | 전체 기간 Base 결과 |
| `output/result_base_monthly_summary.csv` | 월별·본부별 요약 |
| `output/week1_prepared_sample.csv` | 24행 샘플 |

## 4. 구조 검증

| 항목 | 결과 |
|---|---|
| 전체 행 수 | **394,560행** |
| 본부 수 | **15개** |
| 기간 | **2022-01-01 ~ 2024-12-31** |
| 요약 행 수 | **540행** |
| `hour` 범위 | **0 ~ 23** |
| `month` 범위 | **1 ~ 12** |
| 요금 조인 null | **0건** |
| 배출량 비율 | `emission_kgCO2eq / emission_tCO2eq = 1000` 전 행 성립 |

## 5. 샘플 수치 확인

첫 행 기준:

- `date = 2022-01-01`
- `headquarter = 강원본부`
- `load_MWh = 2100`
- `rate_won_per_kWh = 64.3`
- `electricity_cost_won = 135,030,000`
- `emission_tCO2eq = 876.33`
- `emission_kgCO2eq = 876,330.0`

계산식:

```text
electricity_cost_won = 2100 × 64.3 × 1000 = 135,030,000
emission_tCO2eq      = 2100 × 0.4173      = 876.33
emission_kgCO2eq     = 2100 × 1000 × 0.4173 = 876,330.0
```

파일 값과 일치한다.

## 6. 적용 정리

- Week 1 범위: 전체 부하 데이터에 대한 기본 처리 코드와 결과 파일 확보
- Week 2 범위: 배출계수 기본값 확정 및 전체 데이터 계산 반영

## 7. 주의사항

1. `electricity_cost_won`은 시간대별 전력량 요금만 반영한다.
2. `base_charge_won_per_kW`는 보존하되, 계약전력 정보 부재로 총 기본요금 계산에는 사용하지 않았다.
3. 배출계수 기본값은 `2023 소비단`이며, `2021-2023평균`은 비교용 옵션으로 둔다.
