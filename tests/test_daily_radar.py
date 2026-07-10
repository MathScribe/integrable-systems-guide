import datetime as dt
import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("run_daily_radar", SCRIPTS / "run_daily_radar.py")
daily = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(daily)


class ResearchRadarPublicationGateTests(unittest.TestCase):
    def test_recent_window_is_inclusive_and_rejects_future_old_and_unknown_dates(self):
        edition = dt.date(2026, 7, 10)
        self.assertTrue(daily.publication_eligible("2026-07-10", edition, 30))
        self.assertTrue(daily.publication_eligible("2026-06-11T23:00:00Z", edition, 30))
        self.assertFalse(daily.publication_eligible("2026-06-10", edition, 30))
        self.assertFalse(daily.publication_eligible("2026-07-11", edition, 30))
        self.assertFalse(daily.publication_eligible(None, edition, 30))
        self.assertFalse(daily.publication_eligible("not-a-date", edition, 30))

    def test_older_recommendation_is_retained_as_backlog_candidate(self):
        original = daily.radar.score_and_classify
        try:
            def fake_score(paper):
                paper.status = "recommended"
                paper.level = "重点推荐"
                paper.reason = "strong DNLS and RHP match"

            daily.radar.score_and_classify = fake_score
            daily.install_publication_gate(dt.date(2026, 7, 10), 30)
            paper = daily.radar.Paper(
                id="arxiv:old",
                title="DNLS Riemann-Hilbert analysis",
                authors=["A"],
                url="https://example.test/old",
                source_type="arxiv",
                published="2021-01-01",
            )
            daily.radar.score_and_classify(paper)
            self.assertEqual(paper.status, "candidate")
            self.assertEqual(paper.level, "值得补读候选")
            self.assertIn("backlog review", paper.reason)
        finally:
            daily.radar.score_and_classify = original

    def test_recent_recommendation_remains_publishable(self):
        original = daily.radar.score_and_classify
        try:
            def fake_score(paper):
                paper.status = "recommended"
                paper.level = "重点推荐"
                paper.reason = "strong coupled NLS match"

            daily.radar.score_and_classify = fake_score
            daily.install_publication_gate(dt.date(2026, 7, 10), 30)
            paper = daily.radar.Paper(
                id="arxiv:new",
                title="Coupled NLS Darboux transformation",
                authors=["A"],
                url="https://example.test/new",
                source_type="arxiv",
                published="2026-07-09",
            )
            daily.radar.score_and_classify(paper)
            self.assertEqual(paper.status, "recommended")
        finally:
            daily.radar.score_and_classify = original


if __name__ == "__main__":
    unittest.main()
