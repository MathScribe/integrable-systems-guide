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
            summary="We study a soliton-gas limit for the derivative nonlinear Schrödinger equation.",
            tags=["DNLS", "soliton gas", "RHP"],
            reason="强相关组合命中：dnls, soliton gas, rhp",
        )

        rendered = daily.render_compact_card(paper)

        self.assertTrue(rendered.startswith("**Asymptotics of Soliton Gas"))
        self.assertNotIn("[Asymptotics of Soliton Gas", rendered)
        self.assertIn("Deng Shan Wang, Xinyu Wang, Third Author, Fourth Author", rendered)
        self.assertIn("[arXiv:2606.24435](https://arxiv.org/abs/2606.24435)", rendered)
        self.assertIn("2026-06", rendered)
        self.assertIn("`DNLS` `soliton gas` `Riemann--Hilbert problem`", rendered)
        self.assertIn("We study a soliton-gas limit", rendered)
        self.assertNotIn("强相关组合命中", rendered)
        self.assertNotIn("作者：", rendered)
        self.assertNotIn("来源：", rendered)
        self.assertNotIn("标签：", rendered)

    def test_display_tags_deduplicates_variants_and_adds_title_methods(self):
        paper = daily.radar.Paper(
            id="arxiv:2606.22808",
            title="Exact Harmonic Dimensional Reduction and Conformal Lifting for Multicomponent NLS Systems",
            authors=["O. V. Kaptsov"],
            url="https://arxiv.org/abs/2606.22808",
            source_type="arxiv",
            arxiv_id="2606.22808",
            summary="The construction applies to the Manakov system and produces rogue waves and breathers.",
            tags=["coupled nonlinear schrodinger", "manakov", "rogue wave", "breather", "breathers"],
        )

        tags = daily.display_tags(paper)

        self.assertEqual(tags[:3], ["dimensional reduction", "conformal lifting", "multicomponent NLS"])
        self.assertIn("Manakov system", tags)
        self.assertIn("rogue waves", tags)
        self.assertIn("breathers", tags)
        self.assertEqual(tags.count("breathers"), 1)

    def test_internal_reason_is_not_published_without_an_abstract(self):
        paper = daily.radar.Paper(
            id="arxiv:test",
            title="Test paper",
            authors=["A. Author"],
            url="https://example.com",
            source_type="arxiv",
            reason="强相关组合命中：breather, rogue wave",
        )

        self.assertEqual(daily.compact_annotation(paper), "")
        self.assertNotIn("强相关组合命中", daily.render_compact_card(paper))

    def test_home_block_omits_long_comments_but_keeps_metadata(self):
        paper = daily.radar.Paper(
            id="arxiv:2607.06409",
            title="Elliptic localized solutions",
            authors=["Wang Tang", "Guo-Fu Yu"],
            url="https://arxiv.org/abs/2607.06409",
            source_type="arxiv",
            published="2026-07-08",
            arxiv_id="2607.06409",
            summary="A deliberately long comment that belongs only in the full brief.",
            tags=["Fokas--Lenells", "Darboux"],
        )
        block = "## 2026-07-09\n\n### 近期关注\n\n" + daily.render_compact_card(paper)

        rendered = daily.compact_home_block(block)

        self.assertIn("## 2026-07-09", rendered)
        self.assertIn("- **Elliptic localized solutions**", rendered)
        self.assertIn("Wang Tang, Guo-Fu Yu", rendered)
        self.assertIn("[arXiv:2607.06409]", rendered)
        self.assertIn("`Fokas--Lenells` `Darboux`", rendered)
        self.assertNotIn("deliberately long comment", rendered.lower())

    def test_home_keeps_multiple_recent_editions_with_a_global_limit(self):
        def block(date, titles):
            cards = []
            for number, title in enumerate(titles):
                paper = daily.radar.Paper(
                    id=f"arxiv:{date}-{number}",
                    title=title,
                    authors=["A. Author"],
                    url="https://example.com",
                    source_type="arxiv",
                    tags=["DNLS"],
                )
                cards.append(daily.render_compact_card(paper))
            return f"## {date}\n\n### 近期关注\n\n" + "\n\n".join(cards)

        rendered = daily.compact_home_blocks(
            [block("2026-07-10", ["Today"]), block("2026-07-09", ["Old 1", "Old 2"])],
            limit=3,
        )

        self.assertIn("## 2026-07-10", rendered)
        self.assertIn("## 2026-07-09", rendered)
        self.assertIn("**Today**", rendered)
        self.assertIn("**Old 1**", rendered)
        self.assertIn("**Old 2**", rendered)
        self.assertEqual(rendered.count("- **"), 3)

    def test_publication_label_prefers_year_month(self):
        self.assertEqual(daily.publication_label("2026-07-08"), "2026-07")
        self.assertEqual(daily.publication_label("2026"), "2026")
        self.assertEqual(daily.publication_label(None), "")


if __name__ == "__main__":
    unittest.main()
