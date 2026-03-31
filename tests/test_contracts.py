"""Tests for the 7 named contract checks."""


from intake.contracts import (
    ALL_CHECKS,
    evaluate_batch,
    evaluate_row,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _valid_row(**overrides) -> dict:
    base = {
        "batch_id": "B-001",
        "order_id": "ORD-1000",
        "customer_id": "CUST-200",
        "order_total": 62.50,
        "event_ts": "2026-03-15T08:00:00+00:00",
        "product_category": "Electronics",
        "region": "West",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Check count
# ---------------------------------------------------------------------------

def test_seven_checks_registered():
    assert len(ALL_CHECKS) == 7


# ---------------------------------------------------------------------------
# Individual check tests
# ---------------------------------------------------------------------------

class TestBatchIdNotNull:
    def test_pass(self):
        assert evaluate_row(_valid_row()) == []

    def test_fail(self):
        violations = evaluate_row(_valid_row(batch_id=None))
        names = [v.check_name for v in violations]
        assert "batch_id_not_null" in names


class TestOrderIdNotNull:
    def test_pass(self):
        assert evaluate_row(_valid_row()) == []

    def test_fail(self):
        violations = evaluate_row(_valid_row(order_id=None))
        names = [v.check_name for v in violations]
        assert "order_id_not_null" in names


class TestCustomerIdNotNull:
    def test_fail(self):
        violations = evaluate_row(_valid_row(customer_id=None))
        names = [v.check_name for v in violations]
        assert "customer_id_not_null" in names


class TestOrderTotalPositive:
    def test_pass(self):
        assert evaluate_row(_valid_row(order_total=1.0)) == []

    def test_fail_none(self):
        violations = evaluate_row(_valid_row(order_total=None))
        names = [v.check_name for v in violations]
        assert "order_total_positive" in names

    def test_fail_zero(self):
        violations = evaluate_row(_valid_row(order_total=0))
        names = [v.check_name for v in violations]
        assert "order_total_positive" in names

    def test_fail_negative(self):
        violations = evaluate_row(_valid_row(order_total=-5.0))
        names = [v.check_name for v in violations]
        assert "order_total_positive" in names


class TestEventTsNotNull:
    def test_fail(self):
        violations = evaluate_row(_valid_row(event_ts=None))
        names = [v.check_name for v in violations]
        assert "event_ts_not_null" in names


class TestEventTsParseable:
    def test_pass_iso(self):
        assert evaluate_row(_valid_row(event_ts="2026-03-15T08:00:00+00:00")) == []

    def test_fail_garbage(self):
        violations = evaluate_row(_valid_row(event_ts="not-a-date"))
        names = [v.check_name for v in violations]
        assert "event_ts_parseable" in names

    def test_skip_when_null(self):
        """event_ts_parseable should not fire when event_ts is None."""
        violations = evaluate_row(_valid_row(event_ts=None))
        names = [v.check_name for v in violations]
        assert "event_ts_parseable" not in names
        assert "event_ts_not_null" in names


class TestNoRescuedData:
    def test_pass(self):
        assert evaluate_row(_valid_row()) == []

    def test_fail(self):
        violations = evaluate_row(_valid_row(_rescued_data='{"extra": "col"}'))
        names = [v.check_name for v in violations]
        assert "no_rescued_data" in names


# ---------------------------------------------------------------------------
# Batch evaluation
# ---------------------------------------------------------------------------

class TestEvaluateBatch:
    def test_all_valid(self):
        rows = [_valid_row(order_id=f"ORD-{i}") for i in range(5)]
        ready, quarantined, violations = evaluate_batch(rows)
        assert len(ready) == 5
        assert len(quarantined) == 0
        assert len(violations) == 0

    def test_mixed_batch(self):
        rows = [
            _valid_row(),
            _valid_row(order_id=None),
            _valid_row(order_total=-1),
        ]
        ready, quarantined, violations = evaluate_batch(rows)
        assert len(ready) == 1
        assert len(quarantined) == 2
        assert len(violations) >= 2

    def test_multiple_violations_per_row(self):
        row = _valid_row(batch_id=None, order_id=None, customer_id=None)
        violations = evaluate_row(row)
        assert len(violations) == 3
