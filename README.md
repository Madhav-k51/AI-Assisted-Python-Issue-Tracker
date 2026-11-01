# Python Issue Tracker & Bug Management System

A beginner-friendly command-line application for recording software issues, assigning priority, updating status, searching records, and storing data in SQLite.

## Technology
- Python 3.10+
- SQLite (included with standard Python installations)
- `unittest` for automated tests

No third-party packages are required.

## Features
- Create, list, view, update, and delete issues (CRUD)
- Priority levels: Low, Medium, High, Critical
- Status workflow: Open, In Progress, Resolved, Closed
- Search by title, description, or assignee
- Input validation and useful error messages
- Parameterized SQL queries to reduce SQL injection risk
- SQLite transaction handling and automatic database initialization
- Automated tests for common success and error cases

## Project structure
```text
python_issue_tracker/
├── issue_tracker.py
├── tests/
│   └── test_issue_tracker.py
├── README.md
└── PROJECT_DOCUMENTATION.docx  # supplied in the package documents folder
```

## Requirements
Install Python 3.10 or newer. Verify:
```bash
python --version
```
On some systems, use `python3` instead of `python`.

## Run the application
From this folder:
```bash
python issue_tracker.py
```
The application creates `issues.db` automatically in the same folder.

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Example workflow
1. Choose `1` and create an issue titled `Login page error`.
2. Choose `2` to list issues and note the assigned ID.
3. Choose `5` to change the status to `In Progress`.
4. Choose `7` to search for `Login`.
5. Choose `3` to view the full record.

## Design notes
- `IssueTracker` contains database and business operations.
- `connection()` uses a context manager to commit successful work, roll back failed work, and close the connection.
- SQL statements use placeholders (`?`) rather than string concatenation.
- Validation errors raise `ValueError`; the command-line interface catches and displays them.
- `created_at` and `updated_at` use ISO-formatted local timestamps.

## Known limitations
- Single-user command-line interface; no login, permissions, or web UI.
- SQLite is appropriate for a learning/demo project, not every multi-user production workload.
- Timestamps use the computer's local time and do not include a timezone.
- Search is simple substring matching.
- There is no issue history/audit log yet.

## Suggested improvements
1. Add user authentication and role-based permissions.
2. Add comments and an audit trail for status changes.
3. Add a Flask or FastAPI interface after learning web frameworks.
4. Move to PostgreSQL for a multi-user deployment.
5. Add CI automation and code coverage reporting.

## Before using this on a resume
Run the application and test suite yourself. Read and understand each method, personalise sample data, and be prepared to explain the architecture, SQL queries, validation, and limitations. Do not claim deployment or production use unless you have actually done it.
