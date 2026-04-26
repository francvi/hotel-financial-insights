import json
import time
import uuid
from pathlib import Path

import httpx
import yaml

from evaluations.db import get_test_cases, init_db, save_evaluation, upsert_test_case
from evaluations.judge import evaluate

CASES_FILE = Path(__file__).parent / "cases.yaml"
PASS_THRESHOLD = 0.7


def seed_cases() -> int:
    init_db()
    cases = yaml.safe_load(CASES_FILE.read_text())
    for c in cases:
        upsert_test_case(
            id=c["id"],
            module=c["module"],
            description=c["description"],
            endpoint=c["endpoint"],
            input_payload=c.get("input", {}),
            criteria=c["criteria"],
        )
    return len(cases)


def _call_agent(base_url: str, payload: dict) -> tuple[str, int]:
    chunks: list[str] = []
    t0 = time.perf_counter()
    with httpx.Client(timeout=120) as client:
        with client.stream("POST", f"{base_url}/api/chat", json=payload) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line.startswith("data: "):
                    continue
                try:
                    blocks = json.loads(line[6:])
                    for block in blocks:
                        if isinstance(block, dict) and block.get("type") == "text":
                            chunks.append(block["text"])
                except (json.JSONDecodeError, KeyError):
                    pass
    latency = int((time.perf_counter() - t0) * 1000)
    return "".join(chunks), latency


def _call_get(base_url: str, path: str) -> tuple[str, int]:
    t0 = time.perf_counter()
    with httpx.Client(timeout=30) as client:
        r = client.get(f"{base_url}{path}")
        r.raise_for_status()
    latency = int((time.perf_counter() - t0) * 1000)
    return json.dumps(r.json(), ensure_ascii=False), latency


def _call_post_json(base_url: str, path: str, payload: dict) -> tuple[str, int]:
    t0 = time.perf_counter()
    with httpx.Client(timeout=30) as client:
        r = client.post(f"{base_url}{path}", json=payload)
        r.raise_for_status()
    latency = int((time.perf_counter() - t0) * 1000)
    return json.dumps(r.json(), ensure_ascii=False), latency


def _dispatch(base_url: str, endpoint: str, payload: dict) -> tuple[str, int]:
    method, path = endpoint.split(" ", 1)
    if method == "POST" and path == "/api/chat":
        return _call_agent(base_url, payload)
    elif method == "GET":
        return _call_get(base_url, path)
    else:
        return _call_post_json(base_url, path, payload)


def run(
    base_url: str = "http://localhost:8000",
    module: str | None = None,
    case_id: str | None = None,
    verbose: bool = True,
) -> str:
    seed_cases()
    cases = get_test_cases(module=module, case_id=case_id)
    if not cases:
        raise ValueError("No test cases found for the given filters.")

    run_id = str(uuid.uuid4())[:8]
    passed_count = 0

    if verbose:
        print(f"\n{'═' * 60}")
        print(f"  RUN {run_id}  —  {len(cases)} caso(s)")
        print(f"{'═' * 60}")

    for case in cases:
        if verbose:
            print(f"\n▶  [{case['module']}] {case['id']}")
            print(f"   {case['description']}")

        response = None
        scores = None
        overall_score = 0.0
        passed = False
        latency_ms = 0
        error = None

        try:
            response, latency_ms = _dispatch(base_url, case["endpoint"], case["input"])
            judge_result = evaluate(
                question=json.dumps(case["input"], ensure_ascii=False),
                response=response,
                criteria=case["criteria"],
            )
            scores = [s.model_dump() for s in judge_result.scores]
            n = len(scores)
            overall_score = sum(1 for s in scores if s["passed"]) / n if n else 0.0
            passed = overall_score >= PASS_THRESHOLD

        except Exception as e:
            error = str(e)

        save_evaluation(
            run_id=run_id,
            test_case_id=case["id"],
            response=response,
            scores=scores,
            overall_score=overall_score,
            passed=passed,
            latency_ms=latency_ms,
            error=error,
        )

        if error:
            print(f"   ✗  ERROR: {error}")
            continue

        if verbose:
            status = "✓  PASS" if passed else "✗  FAIL"
            print(f"   {status}  —  score {overall_score:.0%}  ({latency_ms}ms)")
            for s in scores:
                mark = "  ✓" if s["passed"] else "  ✗"
                print(f"      {mark}  {s['criterion']}")
                if not s["passed"]:
                    print(f"         → {s['reasoning']}")

        if passed:
            passed_count += 1

    if verbose:
        print(f"\n{'─' * 60}")
        print(f"  Resultado: {passed_count}/{len(cases)} passed  (run_id: {run_id})")
        print(f"{'─' * 60}\n")

    return run_id
