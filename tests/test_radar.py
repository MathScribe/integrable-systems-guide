import importlib.util
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("radar", ROOT / "scripts" / "radar.py")
radar = importlib.util.module_from_spec(SPEC)
sys.modules["radar"] = radar
assert SPEC.loader is not None
SPEC.loader.exec_module(radar)


class RadarTests(unittest.TestCase):
    def test_title_fingerprint_normalizes_schrodinger(self):
        fp = radar.title_fingerprint("Asymptotics of Soliton Gas for the Derivative Nonlinear Schrödinger Equation")
        self.assertEqual(fp, "asymptotics soliton gas derivative nonlinear schrodinger equation")

    def test_registry_entries_include_all_papers(self):
        papers = [
            radar.Paper(id="arxiv:1", title="Derivative NLS Riemann Hilbert", authors=["A"], url="https://example/a", source_type="arxiv", arxiv_id="1"),
            radar.Paper(id="arxiv:2", title="Fokas Lenells Darboux", authors=["B"], url="https://example/b", source_type="arxiv", arxiv_id="2"),
        ]
        for p in papers:
            radar.prepare_paper(p)
            radar.score_and_classify(p)
        text = radar.render_registry_entries(papers, "2026-07-10", "2026-W28")
        self.assertEqual(text.count("- id:"), 2)

    def test_recent_blocks_are_reverse_chronological(self):
        weekly = "# Week\n\n---\n\n## 2026-07-09\nA\n\n---\n\n## 2026-07-10\nB\n\n---\n\n## 2026-07-08\nC\n"
        blocks = radar.recent_date_blocks(weekly, limit=2)
        self.assertTrue(blocks[0].startswith("## 2026-07-10"))
        self.assertTrue(blocks[1].startswith("## 2026-07-09"))

    def test_recent_blocks_can_cross_week_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = radar.RADAR_DIR
            try:
                radar.RADAR_DIR = pathlib.Path(tmp)
                (radar.RADAR_DIR / "2026-W28.md").write_text("# W28\n\n---\n\n## 2026-07-12\nSun\n", encoding="utf-8")
                (radar.RADAR_DIR / "2026-W29.md").write_text("# W29\n\n---\n\n## 2026-07-13\nMon\n", encoding="utf-8")
                blocks = radar.recent_date_blocks_from_radar(limit=2)
                self.assertTrue(blocks[0].startswith("## 2026-07-13"))
                self.assertTrue(blocks[1].startswith("## 2026-07-12"))
            finally:
                radar.RADAR_DIR = original

    def test_strong_core_method_is_recommended(self):
        p = radar.Paper(
            id="arxiv:9999.00001",
            title="Long-time asymptotics for the derivative nonlinear Schrodinger equation via Riemann Hilbert methods",
            authors=["A"],
            url="https://arxiv.org/abs/9999.00001",
            source_type="arxiv",
            summary="We study the inverse scattering transform and dbar steepest descent.",
            arxiv_id="9999.00001",
        )
        radar.prepare_paper(p)
        radar.score_and_classify(p)
        self.assertEqual(p.status, "recommended")

    def test_generic_negative_is_rejected(self):
        p = radar.Paper(
            id="title:x",
            title="Machine learning for magnetic soliton simulation",
            authors=["A"],
            url="https://example/x",
            source_type="openalex",
            summary="A neural network experiment for magnetic materials.",
        )
        radar.prepare_paper(p)
        radar.score_and_classify(p)
        self.assertEqual(p.status, "rejected")

    def test_openalex_uses_filter_parameter(self):
        captured = []
        original_fetch_text = radar.fetch_text
        original_queries = radar.OPENALEX_QUERIES
        try:
            radar.OPENALEX_QUERIES = ["derivative nonlinear Schrodinger"]

            def fake_fetch_text(url, timeout=30):
                captured.append(url)
                return '{"results": []}'

            radar.fetch_text = fake_fetch_text
            radar.fetch_openalex("2026-07-01", rows=1)
        finally:
            radar.fetch_text = original_fetch_text
            radar.OPENALEX_QUERIES = original_queries
        self.assertIn("filter=from_publication_date%3A2026-07-01", captured[0])

    def test_arxiv_delay_can_be_disabled_for_tests(self):
        calls = []
        original_fetch_text = radar.fetch_text
        original_queries = radar.ARXIV_QUERIES
        try:
            radar.ARXIV_QUERIES = ['cat:nlin.SI AND all:"DNLS"', 'cat:nlin.SI AND all:"Riemann Hilbert"']

            def fake_fetch_text(url, timeout=30):
                calls.append(url)
                return '<feed xmlns="http://www.w3.org/2005/Atom"></feed>'

            radar.fetch_text = fake_fetch_text
            radar.fetch_arxiv(max_results_per_query=1, delay_seconds=0)
        finally:
            radar.fetch_text = original_fetch_text
            radar.ARXIV_QUERIES = original_queries
        self.assertEqual(len(calls), 2)

    def test_metadata_update_replaces_arxiv_doi(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = radar.PAPER_REGISTRY
            try:
                registry = pathlib.Path(tmp) / "papers.yml"
                registry.write_text(
                    '- id: "arxiv:2600.00001"\n'
                    '  title: "Derivative NLS Riemann Hilbert"\n'
                    '  title_fingerprint: "derivative nls riemann hilbert"\n'
                    '  source:\n'
                    '    type: "arxiv"\n'
                    '    url: "https://arxiv.org/abs/2600.00001"\n'
                    '    arxiv_id: "2600.00001"\n'
                    '    doi: "10.48550/arXiv.2600.00001"\n'
                    '  review_status: "script-screened"\n',
                    encoding="utf-8",
                )
                radar.PAPER_REGISTRY = registry
                p = radar.Paper(
                    id="doi:10.1000/example",
                    title="Derivative NLS Riemann Hilbert",
                    authors=["A"],
                    url="https://doi.org/10.1000/example",
                    source_type="journal",
                    doi="10.1000/example",
                )
                radar.prepare_paper(p)
                changed, updated = radar.update_known_paper_metadata([p], "2026-07-10")
                text = registry.read_text(encoding="utf-8")
                self.assertEqual(changed, 1)
                self.assertEqual(len(updated), 1)
                self.assertIn('doi: "10.1000/example"', text)
                self.assertIn('last_metadata_update: "2026-07-10"', text)
            finally:
                radar.PAPER_REGISTRY = original


if __name__ == "__main__":
    unittest.main()
