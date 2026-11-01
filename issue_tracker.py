"""
Python Issue Tracker & Bug Management System
A beginner-friendly command-line application using Python and SQLite.

Run:
    python issue_tracker.py

Run tests:
    python -m unittest discover -s tests -v
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime

DB_PATH = Path(__file__).with_name("issues.db")
STATUSES = {"Open", "In Progress", "Resolved", "Closed"}
PRIORITIES = {"Low", "Medium", "High", "Critical"}


class IssueTracker:
    """Database-backed operations for tracking software issues."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = str(db_path)
        self.initialize_database()

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_database(self):
        with self.connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    priority TEXT NOT NULL CHECK(priority IN
                        ('Low', 'Medium', 'High', 'Critical')),
                    status TEXT NOT NULL CHECK(status IN
                        ('Open', 'In Progress', 'Resolved', 'Closed')),
                    assignee TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

    @staticmethod
    def _clean_required(value, field_name):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} cannot be empty.")
        return value.strip()

    def create_issue(self, title, description="", priority="Medium", assignee=""):
        title = self._clean_required(title, "Title")
        if priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(sorted(PRIORITIES))}.")
        if not isinstance(description, str):
            raise ValueError("Description must be text.")
        if not isinstance(assignee, str):
            raise ValueError("Assignee must be text.")

        now = datetime.now().isoformat(timespec="seconds")
        with self.connection() as conn:
            cursor = conn.execute("""
                INSERT INTO issues
                    (title, description, priority, status, assignee, created_at, updated_at)
                VALUES (?, ?, ?, 'Open', ?, ?, ?)
            """, (title, description.strip(), priority, assignee.strip(), now, now))
            issue_id = cursor.lastrowid
        return self.get_issue(issue_id)

    def get_issue(self, issue_id):
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM issues WHERE id = ?", (issue_id,)).fetchone()
        return dict(row) if row else None

    def list_issues(self, status=None, priority=None, search=None):
        if status is not None and status not in STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(sorted(STATUSES))}.")
        if priority is not None and priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(sorted(PRIORITIES))}.")

        query = "SELECT * FROM issues WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        if search:
            query += " AND (title LIKE ? OR description LIKE ? OR assignee LIKE ?)"
            term = f"%{search.strip()}%"
            params.extend([term, term, term])
        query += " ORDER BY id DESC"

        with self.connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def update_status(self, issue_id, status):
        if status not in STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(sorted(STATUSES))}.")
        now = datetime.now().isoformat(timespec="seconds")
        with self.connection() as conn:
            cursor = conn.execute(
                "UPDATE issues SET status = ?, updated_at = ? WHERE id = ?",
                (status, now, issue_id)
            )
            if cursor.rowcount == 0:
                return False
        return True

    def update_issue(self, issue_id, title=None, description=None,
                     priority=None, assignee=None):
        current = self.get_issue(issue_id)
        if current is None:
            return False
        new_title = current["title"] if title is None else self._clean_required(title, "Title")
        new_description = current["description"] if description is None else description
        new_priority = current["priority"] if priority is None else priority
        new_assignee = current["assignee"] if assignee is None else assignee

        if not isinstance(new_description, str):
            raise ValueError("Description must be text.")
        if not isinstance(new_assignee, str):
            raise ValueError("Assignee must be text.")
        if new_priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(sorted(PRIORITIES))}.")

        now = datetime.now().isoformat(timespec="seconds")
        with self.connection() as conn:
            conn.execute("""
                UPDATE issues
                SET title = ?, description = ?, priority = ?, assignee = ?, updated_at = ?
                WHERE id = ?
            """, (new_title, new_description.strip(), new_priority,
                  new_assignee.strip(), now, issue_id))
        return True

    def delete_issue(self, issue_id):
        with self.connection() as conn:
            cursor = conn.execute("DELETE FROM issues WHERE id = ?", (issue_id,))
        return cursor.rowcount > 0


def print_issue(issue):
    if not issue:
        print("Issue not found.")
        return
    print("-" * 60)
    for key in ("id", "title", "description", "priority", "status",
                "assignee", "created_at", "updated_at"):
        print(f"{key.replace('_', ' ').title()}: {issue[key]}")
    print("-" * 60)


def prompt_nonempty(label):
    while True:
        value = input(label).strip()
        if value:
            return value
        print("This field cannot be empty.")


def run_cli():
    tracker = IssueTracker()
    menu = """
=== Python Issue Tracker ===
1. Create issue
2. List issues
3. View issue by ID
4. Update issue details
5. Change issue status
6. Delete issue
7. Search issues
0. Exit
"""
    while True:
        print(menu)
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                title = prompt_nonempty("Title: ")
                description = input("Description (optional): ")
                print("Priorities:", ", ".join(sorted(PRIORITIES)))
                priority = input("Priority [Medium]: ").strip() or "Medium"
                assignee = input("Assignee (optional): ")
                issue = tracker.create_issue(title, description, priority, assignee)
                print(f"Issue created successfully. ID: {issue['id']}")
            elif choice == "2":
                issues = tracker.list_issues()
                if not issues:
                    print("No issues found.")
                for item in issues:
                    print(f"#{item['id']} | {item['status']} | {item['priority']} | {item['title']}")
            elif choice == "3":
                issue = tracker.get_issue(int(input("Issue ID: ")))
                print_issue(issue)
            elif choice == "4":
                issue_id = int(input("Issue ID to update: "))
                if not tracker.get_issue(issue_id):
                    print("Issue not found.")
                    continue
                print("Leave a field blank to keep its current value.")
                title = input("New title: ").strip() or None
                description = input("New description: ").strip()
                description = description if description else None
                priority = input("New priority (Low/Medium/High/Critical): ").strip() or None
                assignee = input("New assignee: ").strip()
                assignee = assignee if assignee else None
                print("Updated." if tracker.update_issue(
                    issue_id, title, description, priority, assignee
                ) else "Issue not found.")
            elif choice == "5":
                issue_id = int(input("Issue ID: "))
                status = prompt_nonempty("New status (Open/In Progress/Resolved/Closed): ")
                print("Status updated." if tracker.update_status(issue_id, status) else "Issue not found.")
            elif choice == "6":
                issue_id = int(input("Issue ID to delete: "))
                confirm = input("Type DELETE to confirm: ").strip()
                if confirm == "DELETE":
                    print("Deleted." if tracker.delete_issue(issue_id) else "Issue not found.")
                else:
                    print("Deletion cancelled.")
            elif choice == "7":
                term = input("Search title, description, or assignee: ").strip()
                results = tracker.list_issues(search=term)
                if not results:
                    print("No matching issues found.")
                for item in results:
                    print(f"#{item['id']} | {item['status']} | {item['priority']} | {item['title']}")
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Please choose a valid menu option.")
        except ValueError as exc:
            print(f"Input error: {exc}")
        except sqlite3.Error as exc:
            print(f"Database error: {exc}")


if __name__ == "__main__":
    run_cli()
