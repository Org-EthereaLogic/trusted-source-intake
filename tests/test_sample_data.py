"""Tests for sample data generation — batch shapes and expected properties."""


from intake.sample_data import (
    ALL_BATCHES,
    batch_001_clean,
    batch_002_schema_drift,
    batch_003_replay,
    batch_004_partial,
)


class TestBatch001Clean:
    def test_row_count(self):
        assert len(batch_001_clean()) == 10

    def test_all_batch_ids_match(self):
        for row in batch_001_clean():
            assert row["batch_id"] == "B-001"

    def test_no_rescued_data(self):
        for row in batch_001_clean():
            assert "_rescued_data" not in row or row.get("_rescued_data") is None

    def test_all_required_fields_present(self):
        required = {"batch_id", "order_id", "customer_id", "order_total", "event_ts"}
        for row in batch_001_clean():
            for field in required:
                assert row.get(field) is not None, f"Missing {field}"


class TestBatch002SchemaDrift:
    def test_row_count(self):
        assert len(batch_002_schema_drift()) == 8

    def test_rescued_data_present(self):
        rescued = [r for r in batch_002_schema_drift() if r.get("_rescued_data")]
        assert len(rescued) == 8  # all rows have some drift artifact

    def test_extra_column_rows(self):
        rows = batch_002_schema_drift()[:3]
        for row in rows:
            assert "loyalty_tier" in row

    def test_type_mismatch_rows(self):
        rows = batch_002_schema_drift()[3:6]
        for row in rows:
            assert row["order_total"] is None  # failed CAST

    def test_case_mismatch_rows(self):
        rows = batch_002_schema_drift()[6:8]
        for row in rows:
            assert row["event_ts"] is None  # wrong case


class TestBatch003Replay:
    def test_row_count(self):
        assert len(batch_003_replay()) == 10

    def test_same_batch_id_as_001(self):
        for row in batch_003_replay():
            assert row["batch_id"] == "B-001"

    def test_replay_hint_present(self):
        for row in batch_003_replay():
            assert "_source_file_hint" in row


class TestBatch004Partial:
    def test_row_count(self):
        assert len(batch_004_partial()) == 5

    def test_null_batch_id(self):
        assert batch_004_partial()[0]["batch_id"] is None

    def test_null_order_id(self):
        assert batch_004_partial()[1]["order_id"] is None

    def test_null_customer_id(self):
        assert batch_004_partial()[2]["customer_id"] is None

    def test_negative_total(self):
        assert batch_004_partial()[3]["order_total"] < 0

    def test_null_event_ts(self):
        assert batch_004_partial()[4]["event_ts"] is None


class TestAllBatches:
    def test_four_batches_registered(self):
        assert len(ALL_BATCHES) == 4

    def test_total_row_count(self):
        total = sum(len(gen()) for gen in ALL_BATCHES.values())
        assert total == 33

    def test_deterministic(self):
        """Two calls produce identical data."""
        for name, gen in ALL_BATCHES.items():
            first = gen()
            second = gen()
            assert first == second, f"{name} is not deterministic"
