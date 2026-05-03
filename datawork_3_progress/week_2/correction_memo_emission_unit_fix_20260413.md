# 배출량 컬럼 단위 오류 수정 메모

- 상태: 수정 완료
- 작성일: 2026-04-13

## 1. 개요

`dummy_test_result.csv`의 `emission_kgCO2eq`, `emission_tCO2eq` 컬럼에 단위 불일치가 확인되어 수정본 `dummy_test_result_corrected.csv`를 생성했다.

## 2. 원본 오류

| 컬럼명 | 표기 단위 | 실제 값 단위 | 비고 |
|---|---|---|---|
| `emission_kgCO2eq` | kgCO2eq | tCO2eq | 1000배 작게 저장 |
| `emission_tCO2eq` | tCO2eq | tCO2eq | `emission_kgCO2eq`와 동일값 저장 |

원본 계산식 추정:

```text
emission_kgCO2eq = load_MWh × 0.4173
emission_tCO2eq  = emission_kgCO2eq
```

## 3. 수정식

```text
emission_tCO2eq  = load_MWh × 0.4173
emission_kgCO2eq = load_MWh × 1000 × 0.4173
```

## 4. 적용 계수

| 항목 | 값 |
|---|---|
| 기준연도 | 2023 |
| 구분 | 소비단 |
| `CO2eq_tCO2eq_per_MWh` | `0.4173` |
| `CO2eq_kgCO2eq_per_kWh` | `0.4173` |

## 5. 샘플 확인

| datetime | load_MWh | 원본 `emission_kgCO2eq` | 수정 `emission_kgCO2eq` | 원본 `emission_tCO2eq` | 수정 `emission_tCO2eq` |
|---|---|---|---|---|---|
| 2024-01-01 00:00:00 | 31.4901 | 13.14 | 13,140.84 | 13.14 | 13.14 |
| 2024-01-01 01:00:00 | 27.5852 | 11.51 | 11,511.31 | 11.51 | 11.51 |
| 2024-01-01 02:00:00 | 28.9431 | 12.08 | 12,077.94 | 12.08 | 12.08 |

전체 168행에서 `emission_kgCO2eq / emission_tCO2eq = 1000.0`을 확인했다.

## 6. 변경 파일

| 파일명 | 내용 |
|---|---|
| `dummy_test_result.csv` | 원본 유지 |
| `dummy_test_result_corrected.csv` | 수정본 |
| `correct_emission.py` | 보정 스크립트 |

## 7. 사용 기준

- 배출량 수치는 `dummy_test_result_corrected.csv` 기준으로 사용한다.
- 원본 `dummy_test_result.csv`는 검증 참고용으로만 보관한다.
