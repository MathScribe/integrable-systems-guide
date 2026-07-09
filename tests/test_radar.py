import importlib.util
import pathlib
import sys
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
            p.title_fingerprint = radar.title_fingerprint(p.title)
            p.key = radar.canonical_key(p)
            radar.score_and_classify(p)
        text = radar.render_registry_entries(papers, "2026-07-10", "2026-W28")
        self.assertEqual(text.count("- id:"), 2)

    def test_recent_blocks_are_reverse_chronological(self):
        weekly = "# Week\n\n---\n\n## 2026-07-09\nA\n\n---\n\n## 2026-07-10\nB\n\n---\n\n## 2026-07-08\nC\n"
        blocks = radar.recent_date_blocks(weekly, limit=2)
        self.assertTrue(blocks[0].startswith("## 2026-07-10"))
        self.assertTrue(blocks[1].startswith("## 2026-07-09"))

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
        p.title_fingerprint = radar.title_fingerprint(p.title)
        p.key = radar.canonical_key(p)
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
        p.title_fingerprint = radar.title_fingerprint(p.title)
        p.key = radar.canonical_key(p)
        radar.score_and_classify(p)
        self.assertEqual(p.status, "rejected")


if __name__ == "__main__":
    unittest.main()
