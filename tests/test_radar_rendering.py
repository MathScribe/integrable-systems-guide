import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("run_daily_radar_rendering", SCRIPTS / "run_daily_radar.py")
daily = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(daily)


class CompactRadarRenderingTests(unittest.TestCase):
    def test_card_keeps_all_authors_and_links_the_source_not_the_title(self):
        paper = daily.radar.Paper(
            id="arxiv:2606.24435",
            title="Asymptotics of Soliton Gas for the Derivative Nonlinear Schrödinger Equation",
            authors=["Deng Shan Wang", "Xinyu Wang", "Third Author", "Fourth Author"],
            url="https://arxiv.org/abs/2606.24435",
            source_type="arxiv",
            published="2026-06-30",
            arxiv_id="2606.24435",
            tags=["DNLS", "soliton gas", "RHP"],
            reason="strong research match",
        )

        rendered = daily.render_compact_card(paper)

        self.assertTrue(rendered.startswith("**Asymptotics of Soliton Gas"))
        self.assertNotIn("[Asymptotics of Soliton Gas", rendered)
        self.assertIn("Deng Shan Wang, Xinyu Wang, Third Author, Fourth Author", rendered)
        self.assertIn("[arXiv:2606.24435](https://arxiv.org/abs/2606.24435)", rendered)
        self.assertIn("2026-06", rendered)
        self.assertIn("`DNLS` `soliton gas` `RHP`", rendered)
        self.assertNotIn("作者：", rendered)
        self.assertNotIn("来源：", rendered)
        self.assertNotIn("标签：", rendered)

    def test_home_block_omits_long_comments_but_keeps_metadata(self):
        paper = daily.radar.Paper(
            id="arxiv:2607.06409",
            title="Elliptic localized solutions",
            authors=["Wang Tang", "Guo-Fu Yu"],
            url="https://arxiv.org/abs/2607.06409",
            source_type="arxiv",
            published="2026-07-08",
            arxiv_id="2607.06409",
            tags=["Fokas--Lenells", "Darboux"],
            reason="a deliberately long comment that belongs only in the full brief",
        )
        block = "## 2026-07-09\n\n### 近期关注\n\n" + daily.render_compact_card(paper)

        rendered = daily.compact_home_block(block)

        self.assertIn("## 2026-07-09", rendered)
        self.assertIn("- **Elliptic localized solutions**", rendered)
        self.assertIn("Wang Tang, Guo-Fu Yu", rendered)
        self.assertIn("[arXiv:2607.06409]", rendered)
        self.assertIn("`Fokas--Lenells` `Darboux`", rendered)
        self.assertNotIn("deliberately long comment", rendered)

    def test_publication_label_prefers_year_month(self):
        self.assertEqual(daily.publication_label("2026-07-08"), "2026-07")
        self.assertEqual(daily.publication_label("2026"), "2026")
        self.assertEqual(daily.publication_label(None), "")


if __name__ == "__main__":
    unittest.main()
