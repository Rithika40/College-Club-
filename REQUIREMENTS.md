# College Club Management System — Requirements (Source of Truth)

This file distills `srs.md` into the Version 1.0 feature set. Do not implement features outside this list.

## In scope (six features)

1. **User login and account management** — User1 and User2 log in securely, update profile details, and are logged out after inactivity.
2. **Club management** — Create, view, search, update, and delete college clubs.
3. **Member management** — Add, view, search, update, and delete club members (at most five input fields on add).
4. **Event management** — Plan club events with name, date, and description; update and delete events.
5. **Registrations and attendance** — Register members for events; mark and view attendance.
6. **Activities, dashboard, and reports** — Dashboard totals plus reports for clubs, events, registrations, and attendance. Announcement board for notices.

## Out of scope

- Payments, fees, or ticket sales
- Email/SMS, social media, calendar, Zoom, or other third-party integrations
- Mobile apps, live streaming, or video conferencing
- Feedback/inquiry ticketing (not in the agreed six-feature set)
- Open public self-registration of extra logins (exactly two system users: User1 and User2)
- Cloud/multi-campus deployment

## Users

| Username | Default password | Role in v1 |
|----------|------------------|------------|
| User1 | password123 | Full access after login |
| User2 | password123 | Full access after login |

## Non-functional (must implement)

- Passwords stored hashed (SHA-256 with salt), never plain text
- Valid credentials required for all protected functions
- Account lock for 5 minutes after 3 consecutive failed logins
- Session ends after 15 minutes of inactivity
- Validation/error messages for invalid input
- SQLite persistence after restart
- Python backend; local SQLite database
