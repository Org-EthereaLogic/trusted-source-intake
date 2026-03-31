"""Deterministic sample data generator for the four intake test scenarios.

Each batch exercises a specific enterprise intake failure mode:
  - batch_001_clean:        All rows valid, no drift, no replay
  - batch_002_schema_drift: Extra column, type mismatch, field rename
  - batch_003_replay:       Same batch_id as batch_001, different file name
  - batch_004_partial:      Null required fields, negative order_total
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

_BASE_TS = datetime(2026, 3, 15, 8, 0, 0, tzinfo=timezone.utc)


def _ts(offset_hours: int) -> str:
    return (_BASE_TS + timedelta(hours=offset_hours)).isoformat()


def batch_001_clean() -> list[dict]:
    """10 valid order rows — baseline for downstream counts."""
    return [
        {
            "batch_id": "B-001",
            "order_id": f"ORD-{1000 + i}",
            "customer_id": f"CUST-{200 + i}",
            "order_total": round(50.0 + i * 12.5, 2),
            "event_ts": _ts(i),
            "product_category": ["Electronics", "Apparel", "Home", "Grocery", "Auto"][i % 5],
            "region": ["West", "East", "Central", "South", "North"][i % 5],
        }
        for i in range(10)
    ]


def batch_002_schema_drift() -> list[dict]:
    """8 rows with schema problems Auto Loader would rescue.

    - Rows 0-2: extra column 'loyalty_tier' (not in contract)
    - Rows 3-5: order_total is a string "N/A" (type mismatch)
    - Rows 6-7: field 'Event_TS' instead of 'event_ts' (case mismatch)
    """
    rows: list[dict] = []
    # Extra column
    for i in range(3):
        rows.append({
            "batch_id": "B-002",
            "order_id": f"ORD-{2000 + i}",
            "customer_id": f"CUST-{300 + i}",
            "order_total": round(75.0 + i * 10, 2),
            "event_ts": _ts(20 + i),
            "product_category": "Electronics",
            "region": "West",
            "loyalty_tier": "Gold",
            "_rescued_data": json.dumps({"loyalty_tier": "Gold"}),
        })
    # Type mismatch on order_total
    for i in range(3):
        rows.append({
            "batch_id": "B-002",
            "order_id": f"ORD-{2010 + i}",
            "customer_id": f"CUST-{310 + i}",
            "order_total": None,  # would fail CAST in SQL
            "event_ts": _ts(23 + i),
            "product_category": "Apparel",
            "region": "East",
            "_rescued_data": json.dumps({"order_total": "N/A"}),
        })
    # Case mismatch — event_ts missing, Event_TS present
    for i in range(2):
        rows.append({
            "batch_id": "B-002",
            "order_id": f"ORD-{2020 + i}",
            "customer_id": f"CUST-{320 + i}",
            "order_total": 99.99,
            "event_ts": None,
            "product_category": "Home",
            "region": "Central",
            "_rescued_data": json.dumps({"Event_TS": _ts(26 + i)}),
        })
    return rows


def batch_003_replay() -> list[dict]:
    """10 rows with the same batch_id as batch_001 — duplicate replay.

    The data is identical to batch_001 but arrives under a different file name.
    The batch registry should flag this as a replay.
    """
    rows = batch_001_clean()
    # Mark these so the registry can distinguish them
    for row in rows:
        row["_source_file_hint"] = "batch_003_replay_of_001.json"
    return rows


def batch_004_partial() -> list[dict]:
    """5 rows with missing required fields and invalid amounts."""
    return [
        {
            "batch_id": None,
            "order_id": "ORD-4000",
            "customer_id": "CUST-400",
            "order_total": 25.00,
            "event_ts": _ts(40),
            "product_category": "Grocery",
            "region": "South",
        },
        {
            "batch_id": "B-004",
            "order_id": None,
            "customer_id": "CUST-401",
            "order_total": 30.00,
            "event_ts": _ts(41),
            "product_category": "Auto",
            "region": "North",
        },
        {
            "batch_id": "B-004",
            "order_id": "ORD-4002",
            "customer_id": None,
            "order_total": 35.00,
            "event_ts": _ts(42),
            "product_category": "Electronics",
            "region": "West",
        },
        {
            "batch_id": "B-004",
            "order_id": "ORD-4003",
            "customer_id": "CUST-403",
            "order_total": -15.00,
            "event_ts": _ts(43),
            "product_category": "Apparel",
            "region": "East",
        },
        {
            "batch_id": "B-004",
            "order_id": "ORD-4004",
            "customer_id": "CUST-404",
            "order_total": 40.00,
            "event_ts": None,
            "product_category": "Home",
            "region": "Central",
        },
    ]


ALL_BATCHES = {
    "batch_001_clean": batch_001_clean,
    "batch_002_schema_drift": batch_002_schema_drift,
    "batch_003_replay": batch_003_replay,
    "batch_004_partial": batch_004_partial,
}


def write_sample_data(output_dir: str | Path) -> dict[str, int]:
    """Write all four sample batches as JSON files. Returns batch_name → row_count."""
    output_path = Path(output_dir)
    counts: dict[str, int] = {}
    for name, generator in ALL_BATCHES.items():
        batch_dir = output_path / name
        batch_dir.mkdir(parents=True, exist_ok=True)
        rows = generator()
        file_path = batch_dir / f"{name}.json"
        # Write as JSON lines (one object per line, wrapped in array)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
        counts[name] = len(rows)
    return counts


if __name__ == "__main__":
    import sys

    dest = sys.argv[1] if len(sys.argv) > 1 else "data/sample"
    counts = write_sample_data(dest)
    for name, count in counts.items():
        print(f"  {name}: {count} rows")
    print(f"\nSample data written to {dest}/")
