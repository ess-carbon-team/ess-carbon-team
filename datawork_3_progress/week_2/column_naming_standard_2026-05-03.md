# 컬럼명 규칙

## 원칙

- 원본 파일은 한글 컬럼명을 유지한다.
- 가공 결과 파일은 영문 `snake_case` 컬럼명을 사용한다.
- 분류값은 필요 시 한글 표기를 유지한다.

## 적용 범위

- 대상 파일: `result_base.csv`, `result_base_monthly_summary.csv`, `week1_prepared_sample.csv`
- 동일한 규칙을 후속 산출물에도 적용한다.

## 매핑

| 원본 컬럼 | 가공 컬럼 |
|---|---|
| `기준일자` | `date` |
| `기준시` | `hour_ending` |
| `본부명` | `headquarter` |
| `전력사용량(MWh)` | `load_MWh` |
| `고객호수` | `customer_count` |

## 비고

- `headquarter` 값은 `강원본부`와 같이 원문 표기를 사용한다.
- `season`, `load_type`, `emission_factor_basis`는 분류값으로 유지한다.
