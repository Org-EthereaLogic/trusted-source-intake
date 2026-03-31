"""Local demo metrics — mirrors the SQL handoff summary for offline verification.

Loads all four sample batches, runs contract checks, detects replays,
and produces the same metrics the Databricks pipeline would compute.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from intake.contracts import evaluate_row
from intake.sample_data import ALL_BATCHES


@dataclass(frozen=True)
class HandoffSummary:
    """Mirrors ops_handoff_summary fields."""

    total_landed: int
    total_ready: int
    total_quarantined: int
    replay_duplicates: int
    rescued_rows: int
    total_batches: int
    replay_batches: int
    ready_ratio: float
    quarantine_ratio: float


@dataclass(frozen=True)
class BatchRegistryEntry:
    """Mirrors a single row from ops_batch_registry."""

    batch_id: str | None
    file_count: int
    total_rows: int
    is_replay: bool


def compute_demo_metrics() -> tuple[HandoffSummary, list[BatchRegistryEntry]]:
    """Run the full intake demo and return summary + batch registry."""

    all_rows: list[dict] = []
    batch_sources: dict[str | None, list[str]] = {}

    for batch_name, generator in ALL_BATCHES.items():
        rows = generator()
        for row in rows:
            row["_batch_source"] = batch_name
        all_rows.extend(rows)

        # Track which source files contribute to each batch_id
        for row in rows:
            bid = row.get("batch_id")
            if bid not in batch_sources:
                batch_sources[bid] = []
            if batch_name not in batch_sources[bid]:
                batch_sources[bid].append(batch_name)

    # Identify replay batch_ids (same batch_id from multiple sources)
    replay_batch_ids = {bid for bid, sources in batch_sources.items() if len(sources) > 1}

    # Build batch registry
    batch_registry: list[BatchRegistryEntry] = []
    batch_row_counts: Counter[str | None] = Counter()
    for row in all_rows:
        batch_row_counts[row.get("batch_id")] += 1

    for bid, sources in batch_sources.items():
        batch_registry.append(BatchRegistryEntry(
            batch_id=bid,
            file_count=len(sources),
            total_rows=batch_row_counts[bid],
            is_replay=bid in replay_batch_ids,
        ))

    # Evaluate contracts and count outcomes
    total_landed = len(all_rows)
    ready_count = 0
    quarantine_count = 0
    replay_dup_count = 0
    rescued_count = 0

    # Track first-seen order within each batch_id for replay ranking
    seen_orders: dict[tuple, int] = {}

    for row in all_rows:
        bid = row.get("batch_id")
        oid = row.get("order_id")
        key = (bid, oid)

        # Replay duplicate detection
        is_replay_dup = False
        if bid in replay_batch_ids:
            if key in seen_orders:
                is_replay_dup = True
                replay_dup_count += 1
            else:
                seen_orders[key] = 1

        # Rescued data
        if row.get("_rescued_data") is not None:
            rescued_count += 1

        # Contract checks
        violations = evaluate_row(row)

        if violations or is_replay_dup:
            quarantine_count += 1
        else:
            ready_count += 1

    summary = HandoffSummary(
        total_landed=total_landed,
        total_ready=ready_count,
        total_quarantined=quarantine_count,
        replay_duplicates=replay_dup_count,
        rescued_rows=rescued_count,
        total_batches=len(batch_sources),
        replay_batches=len(replay_batch_ids),
        ready_ratio=round(ready_count / total_landed, 4) if total_landed else 0.0,
        quarantine_ratio=round(quarantine_count / total_landed, 4) if total_landed else 0.0,
    )

    return summary, batch_registry


def print_demo_report() -> HandoffSummary:
    """Run the demo and print a human-readable report."""
    summary, registry = compute_demo_metrics()

    print("=" * 60)
    print("TRUSTED SOURCE INTAKE — Demo Report")
    print("=" * 60)
    print()
    print("Handoff Summary")
    print("-" * 40)
    print(f"  Total landed:      {summary.total_landed}")
    print(f"  Total ready:       {summary.total_ready}")
    print(f"  Total quarantined: {summary.total_quarantined}")
    print(f"  Replay duplicates: {summary.replay_duplicates}")
    print(f"  Rescued rows:      {summary.rescued_rows}")
    print(f"  Ready ratio:       {summary.ready_ratio}")
    print(f"  Quarantine ratio:  {summary.quarantine_ratio}")
    print()
    print("Batch Registry")
    print("-" * 40)
    for entry in registry:
        flag = " [REPLAY]" if entry.is_replay else ""
        print(
            f"  {entry.batch_id or '(null)'}: "
            f"{entry.total_rows} rows, "
            f"{entry.file_count} source(s){flag}"
        )
    print()
    return summary


if __name__ == "__main__":
    print_demo_report()
