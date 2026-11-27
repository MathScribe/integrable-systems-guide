import unittest
from copy import deepcopy
from unittest.mock import MagicMock, patch

from check_journal_release import release_errors
from verify_radar_deployment import verify


class JournalReleaseTests(unittest.TestCase):
    def setUp(self):
        self.paper = dict(id="a", title="Title", authors=["Author"], doi="10.1234/a",
                          journal="Journal", year=2027, published="2026-11-04", volume="4",
                          article_number="123", first_online_evidence={
                              "url": "https://doi.org/10.1234/a", "date": "2026-11-04",
                              "statement": "Available online 4 November 2026", "unassigned": ["issue"]})
        self.entry = dict(signal_type="journal-publication", signal_date="2026-11-04")
        self.current = ({"a": self.paper}, {"a": self.entry})
        self.empty = ({}, {})

    def test_verified_date_with_next_year_issue(self):
        self.assertEqual(release_errors(self.empty, self.current), [])

    def test_legacy_and_new_incomplete_entries(self):
        self.paper.pop("published")
        self.entry.update(signal_date=None, added_on="2026-11-13")
        self.assertEqual(release_errors(deepcopy(self.current), self.current), [])
        self.assertIn("exact published date", release_errors(self.empty, self.current)[0])
        self.paper["published"] = "2026-11"
        self.assertIn("exact published date", release_errors(self.empty, self.current)[0])

    def test_metadata_update_keeps_preprint_event(self):
        self.entry.update(signal_type="new-preprint", signal_date="2026-08-10")
        self.assertEqual(release_errors(self.empty, self.current), [])
        self.paper.pop("first_online_evidence")
        self.assertIn("first_online_evidence.url", release_errors(self.empty, self.current)[0])

    def test_changed_card_and_stale_evidence(self):
        old = deepcopy(self.current)
        self.entry["signal_date"] = "2026-11-05"
        self.paper["published"] = self.entry["signal_date"]
        self.assertIn("evidence.date matching", release_errors(old, self.current)[0])
        self.paper["pages"] = ""
        self.paper.pop("article_number")
        self.assertIn("locator", release_errors(old, self.current)[0])

    @patch("verify_radar_deployment.urlopen")
    def test_live_homepage_must_match_uploaded_build(self, opener):
        index = MagicMock()
        index.read_bytes.return_value = b"new page with corrected bibliography"
        response = MagicMock(status=200)
        opener.return_value.__enter__.return_value = response
        response.read.side_effect = [b"old page", index.read_bytes(), b"stale"]
        verify(index, "https://example.org/radar/", attempts=2, delay=0)
        with self.assertRaises(SystemExit):
            verify(index, "https://example.org/radar/", attempts=1)


if __name__ == "__main__":
    unittest.main()
