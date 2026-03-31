"""Tests for the local demo metrics — handoff summary and batch registry."""

from intake.demo_metrics import compute_demo_metrics


class TestHandoffSummary:
    def setup_method(self):
        self.summary, self.registry = compute_demo_metrics()

    def test_total_landed(self):
        # 10 (clean) + 8 (drift) + 10 (replay) + 5 (partial) = 33
        assert self.summary.total_landed == 33

    def test_ready_count_positive(self):
        assert self.summary.total_ready > 0

    def test_quarantine_count_positive(self):
        assert self.summary.total_quarantined > 0

    def test_ready_plus_quarantine_equals_landed(self):
        total = self.summary.total_ready + self.summary.total_quarantined
        assert total == self.summary.total_landed

    def test_replay_duplicates_detected(self):
        assert self.summary.replay_duplicates > 0

    def test_rescued_rows_detected(self):
        assert self.summary.rescued_rows > 0

    def test_replay_batches_detected(self):
        assert self.summary.replay_batches >= 1

    def test_ready_ratio_range(self):
        assert 0.0 < self.summary.ready_ratio < 1.0

    def test_quarantine_ratio_range(self):
        assert 0.0 < self.summary.quarantine_ratio < 1.0

    def test_ratios_sum_to_one(self):
        assert abs(self.summary.ready_ratio + self.summary.quarantine_ratio - 1.0) < 0.01


class TestBatchRegistry:
    def setup_method(self):
        self.summary, self.registry = compute_demo_metrics()

    def test_registry_has_entries(self):
        assert len(self.registry) > 0

    def test_b001_is_replay(self):
        b001 = [e for e in self.registry if e.batch_id == "B-001"]
        assert len(b001) == 1
        assert b001[0].is_replay is True

    def test_b001_file_count(self):
        b001 = [e for e in self.registry if e.batch_id == "B-001"]
        assert b001[0].file_count == 2  # clean + replay

    def test_b002_not_replay(self):
        b002 = [e for e in self.registry if e.batch_id == "B-002"]
        assert len(b002) == 1
        assert b002[0].is_replay is False

    def test_b004_rows(self):
        b004 = [e for e in self.registry if e.batch_id == "B-004"]
        assert b004[0].total_rows >= 4  # at least the non-null-batch rows


class TestDeterminism:
    def test_repeated_runs_match(self):
        s1, r1 = compute_demo_metrics()
        s2, r2 = compute_demo_metrics()
        assert s1 == s2
        assert r1 == r2
