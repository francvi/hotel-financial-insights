#!/usr/bin/env python
"""
Evaluations CLI — Hotel Financial Insights

El servidor debe estar corriendo antes de ejecutar 'run'.

Usage (desde la raíz del proyecto, con venv activo):
    python evaluations/cli.py run
    python evaluations/cli.py run --module agent
    python evaluations/cli.py run --case agent_kpi_directo
    python evaluations/cli.py run --base-url http://localhost:8000
    python evaluations/cli.py benchmark
    python evaluations/cli.py benchmark --last 5
    python evaluations/cli.py benchmark --run-a <run_id> --run-b <run_id>
    python evaluations/cli.py list-cases
    python evaluations/cli.py list-runs
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluations.db import get_latest_evaluation, get_run_detail, get_run_full, get_test_cases, list_runs
from evaluations.runner import run as run_evaluations, seed_cases


# ── Helpers ──────────────────────────────────────────────────

def _bar(score: float, width: int = 10) -> str:
    filled = round(score * width)
    return "█" * filled + "░" * (width - filled)


def _pct(v: float) -> str:
    return f"{v * 100:.0f}%"


# ── Commands ─────────────────────────────────────────────────

def cmd_run(args: argparse.Namespace) -> None:
    run_evaluations(
        base_url=args.base_url,
        module=args.module,
        case_id=args.case,
        verbose=True,
    )


def cmd_benchmark(args: argparse.Namespace) -> None:
    runs = list_runs()
    if not runs:
        print("No hay ejecuciones almacenadas. Ejecuta primero: cli.py run")
        return

    if args.run_a and args.run_b:
        _benchmark_compare(args.run_a, args.run_b)
        return

    limit = args.last or len(runs)
    runs = runs[:limit]

    print(f"\n{'═' * 72}")
    print(f"  BENCHMARK — últimas {len(runs)} ejecucion(es)")
    print(f"{'═' * 72}")
    print(f"  {'RUN ID':<10} {'FECHA':<20} {'TOTAL':>5} {'PASS':>5} {'FAIL':>5} {'RATE':>6}  {'AVG SCORE'}")
    print(f"  {'─' * 68}")

    for r in runs:
        rate = r["passed"] / r["total"] if r["total"] else 0
        bar = _bar(r["avg_score"])
        print(
            f"  {r['run_id']:<10} {r['started_at'][:19]:<20} "
            f"{r['total']:>5} {r['passed']:>5} {r['failed']:>5} "
            f"{_pct(rate):>6}  {bar} {_pct(r['avg_score'])}"
        )

    print(f"{'═' * 72}\n")
    print("Para comparar dos runs: cli.py benchmark --run-a <id> --run-b <id>")
    print()


def _benchmark_compare(run_a: str, run_b: str) -> None:
    detail_a = {r["test_case_id"]: r for r in get_run_detail(run_a)}
    detail_b = {r["test_case_id"]: r for r in get_run_detail(run_b)}

    all_ids = sorted(set(detail_a) | set(detail_b))
    if not all_ids:
        print("No se encontraron resultados para los run_id indicados.")
        return

    print(f"\n{'═' * 76}")
    print(f"  COMPARACIÓN  {run_a}  vs  {run_b}")
    print(f"{'═' * 76}")
    print(f"  {'CASO':<32} {'MOD':<12} {run_a:>8}  {run_b:>8}  {'DELTA':>7}")
    print(f"  {'─' * 72}")

    improved, regressed, unchanged = 0, 0, 0
    for cid in all_ids:
        a = detail_a.get(cid)
        b = detail_b.get(cid)
        score_a = a["overall_score"] if a else None
        score_b = b["overall_score"] if b else None
        module = (a or b)["module"]

        sa_str = _pct(score_a) if score_a is not None else "  N/A"
        sb_str = _pct(score_b) if score_b is not None else "  N/A"

        if score_a is not None and score_b is not None:
            delta = score_b - score_a
            delta_str = f"{delta:+.0%}"
            if delta > 0:
                improved += 1
                flag = " ▲"
            elif delta < 0:
                regressed += 1
                flag = " ▼"
            else:
                unchanged += 1
                flag = "  "
        else:
            delta_str = "   N/A"
            flag = "  "

        print(f"  {cid:<32} {module:<12} {sa_str:>8}  {sb_str:>8}  {delta_str:>7}{flag}")

    print(f"{'─' * 76}")
    print(f"  Mejorados: {improved}  |  Empeorados: {regressed}  |  Sin cambio: {unchanged}")
    print(f"{'═' * 76}\n")


def cmd_list_cases(args: argparse.Namespace) -> None:
    seed_cases()
    cases = get_test_cases(module=args.module)
    if not cases:
        print("No hay casos de prueba.")
        return

    current_module = None
    print()
    for c in cases:
        if c["module"] != current_module:
            current_module = c["module"]
            print(f"  [{current_module.upper()}]")
        n = len(c["criteria"])
        print(f"    {c['id']:<35} {n} criterio(s)  —  {c['description']}")
    print()


def cmd_show(args: argparse.Namespace) -> None:
    ev = get_latest_evaluation(args.case_id)
    if not ev:
        print(f"No hay evaluaciones para el caso '{args.case_id}'.")
        return
    print(f"\n  Caso     : {ev['test_case_id']}")
    print(f"  Run      : {ev['run_id']}")
    print(f"  Score    : {_pct(ev['overall_score'])}  ({'PASS' if ev['passed'] else 'FAIL'})")
    print(f"  Latencia : {ev['latency_ms']}ms")
    if ev["error"]:
        print(f"  Error    : {ev['error']}")
    print(f"\n── Respuesta del agente {'─' * 38}\n")
    print(ev["response"] or "(vacía)")
    print(f"\n── Criterios {'─' * 48}\n")
    for s in ev["scores"]:
        mark = "✓" if s["passed"] else "✗"
        print(f"  {mark}  {s['criterion']}")
        if not s["passed"]:
            print(f"     → {s['reasoning']}")
    print()


def cmd_report(args: argparse.Namespace) -> None:
    runs = list_runs()
    if not runs:
        print("No hay ejecuciones almacenadas. Ejecuta primero: cli.py run")
        return

    run_id = args.run or runs[0]["run_id"]
    meta = next((r for r in runs if r["run_id"] == run_id), None)
    if not meta:
        print(f"Run '{run_id}' no encontrado.")
        return

    cases = get_run_full(run_id)
    fmt = args.format or "md"
    content = _report_md(run_id, meta, cases) if fmt == "md" else _report_html(run_id, meta, cases)

    ext = fmt
    out_dir = Path(__file__).parent.parent / "reports"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"uat-{run_id}.{ext}"
    out_path.write_text(content, encoding="utf-8")
    print(f"Reporte generado: {out_path}")


def _report_md(run_id: str, meta: dict, cases: list[dict]) -> str:
    date = meta["started_at"][:19]
    total, passed = meta["total"], meta["passed"]
    rate = passed / total if total else 0

    lines = [
        f"# Reporte UAT — run `{run_id}`",
        f"",
        f"**Fecha:** {date}  ",
        f"**Resultado:** {passed}/{total} casos pasados ({rate:.0%})  ",
        f"**Score medio:** {meta['avg_score'] * 100:.0f}%",
        f"",
        "---",
        "",
    ]

    # Per-module summary
    modules: dict[str, list] = {}
    for c in cases:
        modules.setdefault(c["module"], []).append(c)

    lines += ["## Resumen por módulo", ""]
    lines += ["| Módulo | Casos | Pasados | Fallidos | Score medio |", "|---|---|---|---|---|"]
    for mod, mod_cases in modules.items():
        n = len(mod_cases)
        p = sum(1 for c in mod_cases if c["passed"])
        avg = sum(c["overall_score"] for c in mod_cases) / n
        lines.append(f"| {mod} | {n} | {p} | {n - p} | {avg * 100:.0f}% |")

    lines += ["", "---", ""]

    # Per-case detail
    lines.append("## Detalle de casos")
    for mod, mod_cases in modules.items():
        lines += ["", f"### {mod.capitalize()}", ""]
        for c in mod_cases:
            status = "✅ PASS" if c["passed"] else "❌ FAIL"
            lines += [
                f"#### {status} `{c['test_case_id']}` — {c['description']}",
                f"",
                f"**Score:** {c['overall_score'] * 100:.0f}%  |  **Latencia:** {c['latency_ms']}ms",
                "",
            ]
            if c["error"]:
                lines += [f"> ⚠️ Error: {c['error']}", ""]
            else:
                for s in c["scores"]:
                    mark = "✓" if s["passed"] else "✗"
                    lines.append(f"- {mark} {s['criterion']}")
                    if not s["passed"]:
                        lines.append(f"  - *{s['reasoning']}*")
            lines.append("")

    lines += ["---", "", f"*Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}*", ""]
    return "\n".join(lines)


def _report_html(run_id: str, meta: dict, cases: list[dict]) -> str:
    date = meta["started_at"][:19]
    total, passed = meta["total"], meta["passed"]
    rate = passed / total if total else 0

    modules: dict[str, list] = {}
    for c in cases:
        modules.setdefault(c["module"], []).append(c)

    def badge(ok: bool) -> str:
        cls = "pass" if ok else "fail"
        label = "PASS" if ok else "FAIL"
        return f'<span class="badge {cls}">{label}</span>'

    mod_rows = ""
    for mod, mod_cases in modules.items():
        n = len(mod_cases)
        p = sum(1 for c in mod_cases if c["passed"])
        avg = sum(c["overall_score"] for c in mod_cases) / n
        mod_rows += f"<tr><td>{mod}</td><td>{n}</td><td>{p}</td><td>{n-p}</td><td>{avg*100:.0f}%</td></tr>\n"

    case_sections = ""
    for mod, mod_cases in modules.items():
        case_sections += f"<h3>{mod.capitalize()}</h3>\n"
        for c in mod_cases:
            criteria_html = ""
            if c["error"]:
                criteria_html = f'<p class="error">⚠️ {c["error"]}</p>'
            else:
                for s in c["scores"]:
                    mark = "✓" if s["passed"] else "✗"
                    cls = "crit-pass" if s["passed"] else "crit-fail"
                    criteria_html += f'<div class="{cls}">{mark} {s["criterion"]}'
                    if not s["passed"]:
                        criteria_html += f'<div class="reasoning">{s["reasoning"]}</div>'
                    criteria_html += "</div>\n"

            case_sections += f"""
<details {'open' if not c['passed'] else ''}>
  <summary>{badge(c['passed'])} <code>{c['test_case_id']}</code> — {c['description']}
    <span class="meta">{c['overall_score']*100:.0f}% · {c['latency_ms']}ms</span>
  </summary>
  <div class="criteria">{criteria_html}</div>
</details>
"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Reporte UAT — {run_id}</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 860px; margin: 40px auto; padding: 0 20px; color: #1a1a1a; }}
  h1 {{ border-bottom: 2px solid #e5e5e5; padding-bottom: 10px; }}
  h3 {{ margin-top: 32px; color: #444; text-transform: capitalize; }}
  .summary {{ display: flex; gap: 24px; margin: 20px 0; }}
  .stat {{ background: #f5f5f5; border-radius: 8px; padding: 12px 20px; text-align: center; }}
  .stat-value {{ font-size: 2em; font-weight: 700; }}
  .stat-label {{ font-size: 0.8em; color: #666; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
  th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid #e5e5e5; }}
  th {{ background: #f5f5f5; font-weight: 600; }}
  .badge {{ padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 700; }}
  .badge.pass {{ background: #d1fae5; color: #065f46; }}
  .badge.fail {{ background: #fee2e2; color: #991b1b; }}
  details {{ border: 1px solid #e5e5e5; border-radius: 6px; margin: 8px 0; }}
  summary {{ padding: 10px 14px; cursor: pointer; display: flex; align-items: center; gap: 8px; }}
  summary:hover {{ background: #f9f9f9; }}
  .meta {{ margin-left: auto; font-size: 0.8em; color: #888; }}
  .criteria {{ padding: 12px 16px; border-top: 1px solid #f0f0f0; }}
  .crit-pass {{ color: #065f46; margin: 4px 0; }}
  .crit-fail {{ color: #991b1b; margin: 4px 0; }}
  .reasoning {{ margin: 2px 0 6px 16px; font-size: 0.9em; color: #b91c1c; font-style: italic; }}
  .error {{ color: #b91c1c; }}
  footer {{ margin-top: 40px; color: #999; font-size: 0.85em; border-top: 1px solid #e5e5e5; padding-top: 12px; }}
</style>
</head>
<body>
<h1>Reporte UAT <code>{run_id}</code></h1>
<p><strong>Fecha:</strong> {date}</p>

<div class="summary">
  <div class="stat"><div class="stat-value">{passed}/{total}</div><div class="stat-label">Casos pasados</div></div>
  <div class="stat"><div class="stat-value">{rate:.0%}</div><div class="stat-label">Pass rate</div></div>
  <div class="stat"><div class="stat-value">{meta['avg_score']*100:.0f}%</div><div class="stat-label">Score medio</div></div>
</div>

<h2>Resumen por módulo</h2>
<table>
  <tr><th>Módulo</th><th>Casos</th><th>Pasados</th><th>Fallidos</th><th>Score medio</th></tr>
  {mod_rows}
</table>

<h2>Detalle de casos</h2>
{case_sections}

<footer>Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}</footer>
</body>
</html>"""


def cmd_list_runs(args: argparse.Namespace) -> None:
    runs = list_runs()
    if not runs:
        print("No hay ejecuciones almacenadas.")
        return
    print()
    for r in runs:
        rate = r["passed"] / r["total"] if r["total"] else 0
        print(f"  {r['run_id']}  {r['started_at'][:19]}  {_pct(rate)} pass  (avg {_pct(r['avg_score'])})")
    print()


# ── Entry point ───────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="evaluations",
        description="CLI de evaluaciones UAT — Hotel Financial Insights",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Ejecutar evaluaciones contra la API")
    p_run.add_argument("--module", choices=["agent", "insights", "suggestions"], help="Filtrar por módulo")
    p_run.add_argument("--case", metavar="CASE_ID", help="Ejecutar un caso concreto")
    p_run.add_argument("--base-url", default="http://localhost:8000", metavar="URL")
    p_run.set_defaults(func=cmd_run)

    p_bench = sub.add_parser("benchmark", help="Comparar resultados de ejecuciones")
    p_bench.add_argument("--last", type=int, metavar="N", help="Mostrar las últimas N ejecuciones")
    p_bench.add_argument("--run-a", metavar="RUN_ID")
    p_bench.add_argument("--run-b", metavar="RUN_ID")
    p_bench.set_defaults(func=cmd_benchmark)

    p_lc = sub.add_parser("list-cases", help="Listar todos los casos de prueba")
    p_lc.add_argument("--module", choices=["agent", "insights", "suggestions"])
    p_lc.set_defaults(func=cmd_list_cases)

    p_report = sub.add_parser("report", help="Generar reporte de una ejecución en markdown o HTML")
    p_report.add_argument("--run", metavar="RUN_ID", help="Run a reportar (por defecto: el más reciente)")
    p_report.add_argument("--format", choices=["md", "html"], default="md", help="Formato de salida (por defecto: md)")
    p_report.set_defaults(func=cmd_report)

    p_show = sub.add_parser("show", help="Mostrar la respuesta y criterios de la última evaluación de un caso")
    p_show.add_argument("case_id", metavar="CASE_ID")
    p_show.set_defaults(func=cmd_show)

    p_lr = sub.add_parser("list-runs", help="Listar todas las ejecuciones almacenadas")
    p_lr.set_defaults(func=cmd_list_runs)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
