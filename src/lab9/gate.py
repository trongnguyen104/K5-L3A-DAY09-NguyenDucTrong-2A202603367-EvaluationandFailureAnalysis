"""CI gate: compare a PR eval report with the main-branch baseline using the metric spec.

    python -m lab9.gate --pr reports/eval_workflow.json --baseline reports/baseline_v1.json

exit 0 = merge, exit 1 = blocked. Safety metrics: max 0, no averaging away.
Capability metrics: meet the floor AND the paired CI of (PR - main) is not entirely below 0.
Thresholds may only get stricter on the same eval-set version (ratchet).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats
from lab9.eval import SPEC, load_spec, per_item


def integrity_check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> list[str]:
    """M7 (Expert): refuse to compare reports that cannot be trusted. Return a list of problems
    (empty = trustworthy). A gate that passes a broken report is worse than no gate.
    Must catch at least:
      - any metric value in pr["metrics"] that is NaN or inf
      - len(pr["rows"]) != manifest items x len(manifest seeds)   (dropped / duplicated rows)
      - the (item_id, seed) set of PR differs from the baseline's (cherry-picked seeds/items)
      - pr["evaluator_failures"] non-empty, or a row whose value for a graded spec metric is
        None (a crashed grader silently scores as "missing" and drops out of the mean)
      - base_spec given and a threshold in spec is LOOSER than in base_spec for the same
        eval-set version (ratchet: max may not rise, min may not fall, a blocking metric may
        not become non-blocking, a metric may not disappear; the same for spec["slices"],
        including dropping no_significant_drop)
      - an item's slice tags in PR rows differ from the baseline's (relabelling an item out of a
        slice hides its regression from the slice gate)"""
    # TODO M7
    import math

    problems = []

    # 1. Kiểm tra metric không được là NaN hoặc Inf
    for metric_id, value in pr.get("metrics", {}).items():
        if isinstance(value, (int, float)):
            if not math.isfinite(value):
                problems.append(f"metric {metric_id} is not finite")

    # 2. Kiểm tra số lượng rows theo manifest
    manifest = pr.get("manifest", {})
    expected = manifest.get("items", 0) * len(manifest.get("seeds", []))
    rows = pr.get("rows", [])

    if len(rows) != expected:
        problems.append(
            f"row count mismatch: expected {expected}, got {len(rows)}"
        )

    # 3. Kiểm tra trùng hoặc thiếu cặp (item_id, seed)
    def row_keys(report):
        return [
            (row.get("item_id"), row.get("seed"))
            for row in report.get("rows", [])
        ]

    pr_keys = row_keys(pr)
    base_keys = row_keys(base)

    if len(pr_keys) != len(set(pr_keys)):
        problems.append("duplicate (item_id, seed) rows in PR")

    if set(pr_keys) != set(base_keys):
        problems.append("(item_id, seed) set differs from baseline")

    # 4. Kiểm tra evaluator failures
    if pr.get("evaluator_failures"):
        problems.append("evaluator_failures is not empty")

    # 5. Kiểm tra metric bị thiếu trong từng row
    for metric in spec.get("metrics", []):
        metric_id = metric["id"]

        for row in rows:
            if row.get(metric_id) is None:
                problems.append(
                    f"row {row.get('item_id')}/{row.get('seed')} "
                    f"has missing metric {metric_id}"
                )
                break

    # 6. Kiểm tra slice tags không bị thay đổi so với baseline
    def slice_map(report):
        result = {}
        for row in report.get("rows", []):
            item_id = row.get("item_id")
            tags = frozenset(row.get("slices") or [])
            if item_id in result and result[item_id] != tags:
                result[item_id] = None
            else:
                result[item_id] = tags
        return result

    if slice_map(pr) != slice_map(base):
        problems.append("slice tags differ from baseline")

    # 7. Ratchet: chỉ so sánh khi cùng eval-set version
    if (
        base_spec is not None
        and spec.get("eval_set_version") == base_spec.get("eval_set_version")
    ):
        current_metrics = {
            m["id"]: m for m in spec.get("metrics", [])
        }
        previous_metrics = {
            m["id"]: m for m in base_spec.get("metrics", [])
        }

        # Không được xóa metric đã tồn tại
        for metric_id in previous_metrics:
            if metric_id not in current_metrics:
                problems.append(f"metric {metric_id} was removed")

        # Không được nới lỏng threshold hoặc bỏ blocking
        for metric_id, old in previous_metrics.items():
            new = current_metrics.get(metric_id)
            if new is None:
                continue

            old_th = old.get("threshold", {})
            new_th = new.get("threshold", {})

            if "max" in old_th and (
                "max" not in new_th or new_th["max"] > old_th["max"]
            ):
                problems.append(f"metric {metric_id} max threshold loosened")

            if "min" in old_th and (
                "min" not in new_th or new_th["min"] < old_th["min"]
            ):
                problems.append(f"metric {metric_id} min threshold loosened")

            if old.get("blocking", False) and not new.get("blocking", False):
                problems.append(f"metric {metric_id} became non-blocking")

            if (
                old_th.get("no_significant_drop", False)
                and not new_th.get("no_significant_drop", False)
            ):
                problems.append(
                    f"metric {metric_id} removed no_significant_drop"
                )

        # Ratchet cho slice
        current_slices = {
            s["name"]: s for s in spec.get("slices", [])
        }
        previous_slices = {
            s["name"]: s for s in base_spec.get("slices", [])
        }

        for name, old in previous_slices.items():
            new = current_slices.get(name)

            if new is None:
                problems.append(f"slice {name} was removed")
                continue

            if old.get("metric") != new.get("metric"):
                problems.append(f"slice {name} metric changed")

            if "min" in old and (
                "min" not in new or new["min"] < old["min"]
            ):
                problems.append(f"slice {name} min threshold loosened")

            if "max" in old and (
                "max" not in new or new["max"] > old["max"]
            ):
                problems.append(f"slice {name} max threshold loosened")

            if old.get("blocking", False) and not new.get("blocking", False):
                problems.append(f"slice {name} became non-blocking")

            if (
                old.get("no_significant_drop", False)
                and not new.get("no_significant_drop", False)
            ):
                problems.append(
                    f"slice {name} removed no_significant_drop"
                )

    return problems

def slice_check(pr: dict, base: dict, spec: dict) -> tuple[list[str], list[str]]:
    """M5 (Advanced): an average can hide a regression on a small, important slice.
    For each entry of spec["slices"] ({"name", "metric", "min"?, "no_significant_drop"?, "blocking"}):
      - value = mean of per_item(pr, metric, slice_name=name)
      - fail if below "min", or if no_significant_drop and the paired CI over the slice's items
        lies entirely below 0
    Return (blocked ids like "slice:money_movement/pass_rate", report lines)."""
    # TODO M5
    import statistics

    blocked = []
    lines = []

    bootstrap = spec.get("bootstrap", {})
    n_resamples = bootstrap.get("n_resamples", 1000)
    rng = bootstrap.get("rng", 2027)

    for slice_spec in spec.get("slices", []):
        name = slice_spec["name"]
        metric = slice_spec["metric"]
        threshold = slice_spec.get("min")
        blocking = slice_spec.get("blocking", False)

        # Lấy kết quả theo từng item trong slice
        pr_values = per_item(pr, metric, slice_name=name)
        base_values = per_item(base, metric, slice_name=name)

        slice_id = f"slice:{name}/{metric}"
        verdict = "ok"
        note = ""

        if not pr_values:
            verdict = "missing"
            note = "no PR data"

        else:
            value = statistics.fmean(pr_values.values())

            if threshold is not None and value < threshold:
                verdict = "fail"

            # Kiểm tra paired confidence interval
            if slice_spec.get("no_significant_drop"):
                keys = sorted(set(pr_values) & set(base_values))

                if not keys:
                    verdict = "missing"
                    note = "no paired baseline data"
                else:
                    d, lo, hi = stats.paired_bootstrap(
                        [pr_values[k] for k in keys],
                        [base_values[k] for k in keys],
                        n_resamples=n_resamples,
                        rng=rng
                    )

                    note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"

                    if hi < 0:
                        verdict = "fail"

        if verdict != "ok" and blocking:
            blocked.append(slice_id)

        label = (
            "ok" if verdict == "ok"
            else "BLOCK" if blocking
            else "warn"
        )

        lines.append(
            f"  {slice_id:<32} {note:<30} {label}"
        )

    return blocked, lines

def check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> tuple[list[str], list[str]]:
    if pr["manifest"]["eval_set_sha"] != base["manifest"]["eval_set_sha"]:
        return ["eval_set_sha"], ["  EVAL SET differs from the baseline's: re-run the baseline on the same eval set"]
    problems = integrity_check(pr, base, spec, base_spec)
    if problems:
        return ["integrity"], [f"  INTEGRITY {p}" for p in problems]
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for m in spec["metrics"]:
        mid, th, val = m["id"], m.get("threshold", {}), pr["metrics"].get(m["id"])
        verdict, note = "ok", ""
        if val is None:
            verdict = "missing"
        elif "max" in th and val > th["max"]:
            verdict = "fail"
        elif "min" in th and val < th["min"]:
            verdict = "fail"
        elif "max_increase" in th and base["metrics"].get(mid):
            if val > base["metrics"][mid] * (1 + th["max_increase"]):
                verdict = "fail"
        if th.get("no_significant_drop") and val is not None:
            a, b = per_item(pr, mid), per_item(base, mid)
            keys = sorted(set(a) & set(b))
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                                               n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027))
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            if hi < 0:
                verdict = "fail"
        if verdict != "ok" and m.get("blocking"):
            blocked.append(mid)
        label = {"ok": "ok", "missing": "MISSING"}.get(verdict, "BLOCK" if m.get("blocking") else "warn")
        lines.append(f"  {mid:<22} {val!s:<8} {json.dumps(th):<40} {note:<28} {label}")
    if spec.get("slices"):
        sb, sl = slice_check(pr, base, spec)
        blocked += sb
        lines += sl
    return blocked, lines


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.gate")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--spec", default=str(SPEC))
    ap.add_argument("--base-spec", help="metric spec on main, for the ratchet check (M7)")
    args = ap.parse_args(argv)
    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base_spec = load_spec(Path(args.base_spec)) if args.base_spec else None
    blocked, lines = check(pr, base, load_spec(Path(args.spec)), base_spec)
    print(f"gate: PR {pr['run_id']} vs main {base['run_id']} · eval set {pr['manifest']['eval_set_sha']}")
    print("\n".join(lines))
    if blocked:
        print(f"exit 1 — blocked: {', '.join(blocked)}")
        return 1
    print("exit 0 — merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
