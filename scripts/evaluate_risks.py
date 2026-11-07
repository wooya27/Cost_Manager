"""
독립 평가셋(사람이 규정 임계값 기준으로 정답을 매긴 소표본)에 대해
위험 탐지의 Precision / Recall / F1 을 (expense_id x risk_type) 단위로 계산한다.

※ 1,000건 회귀 테스트(expected = 코드 출력)와 달리, 여기 expected 는
   코드 출력이 아니라 '규정 임계값을 보고 사람이 정의한 정답'이다.
   그래서 코드가 규정(스펙)에서 벗어나면 FP/FN 으로 드러난다.

실행: PYTHONPATH=. python scripts/evaluate_risks.py
"""

import json

import pandas as pd

from src.audit_rules import detect_risks


CASES = "tests/data/independent_cases.csv"
EXPECTED = "tests/data/independent_expected.csv"


def main():
    cases = pd.read_csv(CASES)
    expected_df = pd.read_csv(EXPECTED)

    # 배치 문맥 유지(중복/평균 규칙) → 전체를 한 번에 탐지
    result = detect_risks(cases.copy())

    # expense_id -> set(risk_type)
    actual = {
        int(row["expense_id"]): {r["risk_type"] for r in row["risks"]}
        for _, row in result.iterrows()
    }
    expected = {
        int(row["expense_id"]): set(json.loads(row["expected_risks"]))
        for _, row in expected_df.iterrows()
    }

    tp = fp = fn = 0
    mismatches = []

    for eid in sorted(expected):
        exp = expected[eid]
        act = actual.get(eid, set())
        tp += len(exp & act)      # 정답에 있고 실제도 탐지
        fp += len(act - exp)      # 실제는 탐지했지만 정답엔 없음
        fn += len(exp - act)      # 정답엔 있지만 못 탐지
        if exp != act:
            mismatches.append((eid, sorted(exp), sorted(act)))

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) else 0.0)

    print(f"표본: {len(expected)}건 (expense_id x risk_type 단위 평가)")
    print(f"TP={tp}  FP={fp}  FN={fn}")
    print(f"Precision = {precision:.3f}")
    print(f"Recall    = {recall:.3f}")
    print(f"F1        = {f1:.3f}")
    if mismatches:
        print("\n[불일치]")
        for eid, exp, act in mismatches:
            print(f"  id={eid}  expected={exp}  actual={act}")
    else:
        print("\n모든 케이스 일치 (이 소표본·규정 임계값 기준)")


if __name__ == "__main__":
    main()
