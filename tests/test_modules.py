"""
Regression tests for the metrics modules.

Each test here pins behaviour that was previously broken, so the bugs cannot
silently return.
"""

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drive_response_manager import EngagementMetrics, Response  # noqa: E402
from pace_tracker import CommitPaceTracker, ReleaseManager  # noqa: E402
from performance_optimizer import (  # noqa: E402
    MEMOIZE_MAXSIZE,
    OptimizedOperations,
    get_performance_report,
    memoize,
    profile_execution,
)


def _response(hours_old, response_id="r1"):
    created = datetime.datetime.now() - datetime.timedelta(hours=hours_old)
    return Response(id=response_id, type="issue", created_at=created)


class TestResponseOverdue:
    """Response.is_overdue must be callable with an SLA override."""

    def test_overdue_accepts_sla_argument(self):
        metrics = EngagementMetrics()
        metrics.add_response(_response(50))
        assert len(metrics.get_overdue_items(24)) == 1

    def test_not_overdue_within_sla(self):
        metrics = EngagementMetrics()
        metrics.add_response(_response(1))
        assert metrics.get_overdue_items(24) == []

    def test_custom_sla_is_respected(self):
        metrics = EngagementMetrics()
        metrics.add_response(_response(30))
        assert metrics.get_overdue_items(48) == []
        assert len(metrics.get_overdue_items(24)) == 1


class TestCommitPaceTracker:
    """Commits must aggregate per calendar day regardless of insert order."""

    def test_same_date_added_out_of_order_is_one_entry(self):
        tracker = CommitPaceTracker()
        day_one = datetime.date(2026, 1, 1)
        day_two = datetime.date(2026, 1, 2)
        tracker.add_commit(day_one, "a")
        tracker.add_commit(day_two, "b")
        tracker.add_commit(day_one, "c")

        assert len(tracker.commits) == 2
        assert tracker.calculate_average_pace() == 1.5

    def test_weekly_pace_separates_same_week_of_different_years(self):
        tracker = CommitPaceTracker()
        tracker.add_commit(datetime.date(2025, 1, 2), "a")
        tracker.add_commit(datetime.date(2026, 1, 2), "b")

        weekly = tracker.get_weekly_pace()
        assert len(weekly) == 2
        assert all(count == 1 for count in weekly.values())

    def test_empty_tracker_returns_zero_pace(self):
        assert CommitPaceTracker().calculate_average_pace() == 0.0


class TestReleaseManager:
    """Release frequency must not depend on insertion order."""

    def test_frequency_with_out_of_order_releases(self):
        manager = ReleaseManager()
        manager.add_release("v2", datetime.date(2026, 6, 1))
        manager.add_release("v1", datetime.date(2026, 1, 1))

        assert manager.get_release_frequency() > 0

    def test_frequency_matches_chronological_order(self):
        ordered = ReleaseManager()
        ordered.add_release("v1", datetime.date(2026, 1, 1))
        ordered.add_release("v2", datetime.date(2026, 6, 1))

        shuffled = ReleaseManager()
        shuffled.add_release("v2", datetime.date(2026, 6, 1))
        shuffled.add_release("v1", datetime.date(2026, 1, 1))

        assert ordered.get_release_frequency() == shuffled.get_release_frequency()

    def test_latest_release_is_newest_by_date(self):
        manager = ReleaseManager()
        manager.add_release("v2", datetime.date(2026, 6, 1))
        manager.add_release("v1", datetime.date(2026, 1, 1))

        assert manager.get_release_report()["latest_release"][0] == "v2"


class TestPerformanceOptimizer:
    """Profiling must feed the module-level report."""

    def test_profiled_function_appears_in_global_report(self):
        @profile_execution
        def sample_workload():
            return sum(range(100))

        sample_workload()
        sample_workload()

        report = get_performance_report()
        assert "sample_workload" in report
        assert report["sample_workload"]["call_count"] == 2

    def test_memoize_handles_unhashable_arguments(self):
        calls = []

        @memoize
        def length_of(items):
            calls.append(items)
            return len(items)

        assert length_of([1, 2, 3]) == 3
        assert len(calls) == 1

    def test_memoize_caches_hashable_arguments(self):
        calls = []

        @memoize
        def double(value):
            calls.append(value)
            return value * 2

        assert double(2) == 4
        assert double(2) == 4
        assert len(calls) == 1

    def test_memoize_cache_is_bounded(self):
        @memoize
        def identity(value):
            return value

        for value in range(MEMOIZE_MAXSIZE + 50):
            identity(value)

        assert len(identity.cache) <= MEMOIZE_MAXSIZE

    def test_compute_hash_is_stable(self):
        first = OptimizedOperations.compute_hash("abc")
        second = OptimizedOperations.compute_hash("abc")
        assert first == second

    def test_batch_process_splits_items(self):
        batches = list(OptimizedOperations.batch_process(list(range(10)), batch_size=4))
        assert [len(batch) for batch in batches] == [4, 4, 2]
