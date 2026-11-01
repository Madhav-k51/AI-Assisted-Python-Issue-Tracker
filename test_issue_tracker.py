import tempfile
import unittest
from pathlib import Path

from issue_tracker import IssueTracker


class IssueTrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_issues.db"
        self.tracker = IssueTracker(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_issue_starts_open(self):
        issue = self.tracker.create_issue("Login page error", "Page returns error", "High", "Madhav")
        self.assertEqual(issue["title"], "Login page error")
        self.assertEqual(issue["status"], "Open")
        self.assertEqual(issue["priority"], "High")

    def test_blank_title_is_rejected(self):
        with self.assertRaises(ValueError):
            self.tracker.create_issue("   ")

    def test_invalid_priority_is_rejected(self):
        with self.assertRaises(ValueError):
            self.tracker.create_issue("A bug", priority="Urgent-ish")

    def test_update_status(self):
        issue = self.tracker.create_issue("Search broken")
        self.assertTrue(self.tracker.update_status(issue["id"], "Resolved"))
        self.assertEqual(self.tracker.get_issue(issue["id"])["status"], "Resolved")

    def test_invalid_status_is_rejected(self):
        with self.assertRaises(ValueError):
            self.tracker.update_status(1, "Done-ish")

    def test_search_finds_title(self):
        self.tracker.create_issue("Payment page timeout")
        self.tracker.create_issue("Profile icon missing")
        results = self.tracker.list_issues(search="payment")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Payment page timeout")

    def test_delete_issue(self):
        issue = self.tracker.create_issue("Temporary issue")
        self.assertTrue(self.tracker.delete_issue(issue["id"]))
        self.assertIsNone(self.tracker.get_issue(issue["id"]))

    def test_update_issue_details(self):
        issue = self.tracker.create_issue("Old title")
        self.assertTrue(self.tracker.update_issue(issue["id"], title="New title", priority="Critical"))
        updated = self.tracker.get_issue(issue["id"])
        self.assertEqual(updated["title"], "New title")
        self.assertEqual(updated["priority"], "Critical")

    def test_missing_issue_update_returns_false(self):
        self.assertFalse(self.tracker.update_status(9999, "Closed"))


if __name__ == "__main__":
    unittest.main()
