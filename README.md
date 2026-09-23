# College Club Management System

Local web app for managing college clubs, members, events, registrations, attendance, announcements, and reports. Built from `srs.md` and `REQUIREMENTS.md`.

## Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python FastAPI
- Database: SQLite (`data/club_management.db`)

## Features (v1)

1. Login and account/profile management (User1 and User2)
2. Club CRUD and search
3. Member CRUD and search
4. Event CRUD and search
5. Event registration and attendance tracking
6. Dashboard, activity reports, and announcement board

## Default logins

| Username | Password |
|----------|----------|
| User1 | password123 |
| User2 | password123 |

Passwords are stored as salted SHA-256 hashes. After 3 failed logins the account locks for 5 minutes. Sessions expire after 15 minutes of inactivity.

## Setup

From the project folder:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS / Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python run.py
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

The API is served at `/api`. Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Tests

```bash
python -m pytest -q
```

## Project layout

```
backend/     FastAPI app, models, auth, routes
frontend/    Login and application UI
data/        SQLite database (created on first run)
tests/       API tests
srs.md
REQUIREMENTS.md
```
