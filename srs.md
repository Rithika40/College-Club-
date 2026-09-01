1. User login and account management.
2. Create and manage college clubs.
3. Add and manage club members.
4. Plan and manage club events.
5. Track event registrations and attendance.
6. View club activities and reports.

Sure — based exactly on your **six features** and assuming a **Python + SQLite** first version, here is the SRS content.

## 1. Purpose and Scope

### Purpose

The purpose of the College Club Management System is to provide a centralized system for managing college clubs, members, events, registrations, attendance, activities, and reports. The system will allow authorized users to maintain club-related information using a Python application with SQLite for data storage.

### Scope

**IN Scope:**

* User login and account management.
* Creation and management of college clubs.
* Adding and managing club members.
* Planning and managing club events.
* Tracking event registrations and attendance.
* Viewing club activities and reports.

**OUT of Scope:**

* Online payment processing.
* Integration with external social media platforms.
* Mobile application development.
* Online video conferencing or live event streaming.

## 2. Functional Requirements

* **FR-01:** The system shall provide user login and account management.
* **FR-02:** The system shall allow authorized users to create and manage college clubs.
* **FR-03:** The system shall allow authorized users to add and manage club members.
* **FR-04:** The system shall allow authorized users to plan and manage club events.
* **FR-05:** The system shall track event registrations and attendance.
* **FR-06:** The system shall allow users to view club activities and reports.

## 3. Non-Functional Requirements

* **NFR-01:** The system shall respond to normal user operations within **2 seconds**.
* **NFR-02:** The system shall support at least **50 concurrent user accounts**.
* **NFR-03:** The system shall require valid credentials before allowing access to protected functions.
* **NFR-04:** The system shall log out inactive users after **15 minutes** of inactivity.
* **NFR-05:** The system shall allow a new user to complete login or account-related tasks within **3 minutes** without assistance.
* **NFR-06:** The system shall display validation or error messages within **2 seconds** of invalid input.
* **NFR-07:** The system shall maintain at least **99% data availability** during normal operating periods.
* **NFR-08:** The system shall preserve stored club, member, event, registration, and attendance data after application restart.

## 4. Assumptions

* Users have valid college-related accounts or credentials.
* Users have basic computer knowledge.
* Club and member information entered by users is accurate.
* The application runs on a computer with Python installed.
* SQLite is available as the local database.
* A single institution uses the system in the first version.

## 5. Constraints

* The application shall be developed using **Python**.
* **SQLite** shall be used as the database.
* The first version shall use a local database rather than a cloud database.
* The system shall depend on the hardware and operating system where Python is installed.
* The project shall be limited to the **six specified features** in the first version.

1. **User Authentication:** User 1 and User 2 can register, log in securely, and manage their profile details.
2. **Club Management:** User 1 can create and manage club details, while User 2 can browse and join different clubs.
3. **Event Scheduling:** User 1 can post new club events, while User 2 can view event details and register to attend.
4. **Attendance Tracking:** User 1 can record event attendance, while User 2 can view their personal event participation history.
5. **Announcements System:** User 1 can broadcast club updates, while User 2 can view notifications on their dashboard.
6. **Feedback & Inquiries:** User 2 can submit feedback or questions, while User 1 can review and respond to them.

### Purpose and Scope

**Purpose:** This document specifies the functional and non-functional requirements for the College Club Management System Version 1.0, designed to centralize club administrative tasks and student engagement.

**Scope:** The system provides a centralized digital platform for club creation, event management, attendance tracking, and internal communication within a college campus.

**In Scope:**

* Account registration, authentication, and profile management.
* Club creation, browsing, and membership requests.
* Event posting, attendee registration, and attendance tracking.
* Announcement broadcasting and user dashboard notifications.
* Feedback submission and response management.

**Out of Scope:**

* Financial management, membership fee processing, or ticket sales.
* Third-party platform integrations (e.g., Google Calendar, Slack, Zoom).
* Multi-campus support or role-based access for non-student administrative staff.

---

### Functional Requirements

* **FR-01:** The system shall allow users to register an account, log in securely, and update their personal profile details.
* **FR-02:** The system shall enable club administrators to create and manage club details, and allow students to browse active clubs and request membership.
* **FR-03:** The system shall allow club administrators to create event listings and enable students to view event details and register their attendance.
* **FR-04:** The system shall enable club administrators to record attendance for registered events and allow students to view their personal participation history.
* **FR-05:** The system shall allow club administrators to publish announcements and display those notifications on user dashboards.
* **FR-06:** The system shall enable students to submit inquiries or feedback to specific clubs and allow club administrators to review and respond.

---

### Non-Functional Requirements

* **NFR-01 (Speed):** The system shall load dashboard views and search results within 2.0 seconds under a concurrent load of 100 users.
* **NFR-02 (Security):** The system shall hash all user passwords using SHA-256 or bcrypt prior to storage and enforce session timeouts after 15 minutes of inactivity.
* **NFR-03 (Usability):** The system shall allow a first-time user to complete the club joining workflow in no more than 3 user clicks from the homepage.
* **NFR-04 (Reliability):** The system shall maintain an uptime of 99.5% during academic semester operational hours.

---

### Assumptions and Constraints

**Assumptions:**

* Users possess basic computer literacy and access to a modern web browser.
* All users belong to the same institution and use official institutional email addresses for account verification.
* Expected concurrent user traffic will remain relatively low and localized to campus demand.

**Constraints:**

* **Technology Stack:** The backend application logic must be implemented exclusively in Python.
* **Database Engine:** Data persistence must be handled using SQLite3, limiting concurrent write operations due to file-locking mechanisms.
* **Deployment Environment:** The initial release must run as a single-instance local web server without distributed database clustering.

1. Member Registration – add, update, and view club member details.
2. Club/Event Creation – create clubs or events with basic details like name, date, and description.
3. Event Registration – allow users to sign up for events or club activities.
4. Attendance Tracking – mark and view attendance for meetings or events.
5. Notice/Announcement Board – post and view important updates or announcements.
6. User Login System – simple login for User1 and User2 to access the system securely.


# Software Requirements Specification — College Club Management System

## 1. Purpose and Scope

**Purpose**
This document specifies the requirements for a College Club Management System (CCMS), a desktop/local application intended to help a college club manage members, events, attendance, and announcements. It is intended for the developer, reviewer, and any future maintainer of the system as a reference for what the software must do.

**Scope**
The first version of CCMS will support member management, event/club creation, event sign-up, attendance tracking, announcements, and basic user login for two users.

**In Scope**
- Adding, updating, and viewing member details
- Creating clubs/events with name, date, and description
- Registering members for events
- Marking and viewing attendance
- Posting and viewing announcements
- Login for two predefined users

**Out of Scope**
- Payment or fee collection
- Email/SMS notifications
- Multi-club or multi-admin role hierarchy
- Mobile application
- Reporting/analytics dashboards
- Cloud hosting or multi-user concurrent network access

---

## 2. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | The system shall allow a logged-in user to add a new club member's details. |
| FR-02 | The system shall allow a logged-in user to update an existing club member's details. |
| FR-03 | The system shall allow a logged-in user to view a list of club members. |
| FR-04 | The system shall allow a logged-in user to create a club or event with a name, date, and description. |
| FR-05 | The system shall allow a member to register for a club or event. |
| FR-06 | The system shall allow a logged-in user to mark attendance for a meeting or event. |
| FR-07 | The system shall allow a logged-in user to view attendance records for a meeting or event. |
| FR-08 | The system shall allow a logged-in user to post an announcement or notice. |
| FR-09 | The system shall allow a logged-in user to view all posted announcements or notices. |
| FR-10 | The system shall require a username and password before granting access to any system feature. |
| FR-11 | The system shall support login for exactly two predefined users, User1 and User2. |

---

## 3. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | The system shall load the main menu within 2 seconds of successful login on a standard college lab PC. |
| NFR-02 | The system shall return search or view results for member, event, or attendance data within 3 seconds for a database of up to 1,000 records. |
| NFR-03 | The system shall lock a user account for 5 minutes after 3 consecutive failed login attempts. |
| NFR-04 | The system shall store all passwords in hashed form using a minimum of SHA-256, never as plain text. |
| NFR-05 | The system shall allow a first-time user to complete member registration in no more than 5 input fields without external help. |
| NFR-06 | The system shall display an on-screen error message within 1 second for any invalid or incomplete input. |
| NFR-07 | The system shall achieve 99% successful save operations (no data loss) across 100 consecutive add/update transactions. |
| NFR-08 | The system shall support at least 500 member records and 200 event records in the SQLite database without performance degradation (response time under NFR-02). |
| NFR-09 | The system shall complete a full data backup (database file copy) in under 10 seconds. |

---

## 4. Assumptions

- Only two users (User1 and User2) will use the system; no need to support additional accounts in v1.
- The system will run on a single local machine (desktop/laptop), not over a network.
- The club has a manageable data volume (hundreds, not thousands, of members/events).
- Users have basic computer literacy and no formal training is required.
- One club/admin context is sufficient; multi-club support is not needed yet.
- Internet access is not required for core functionality.

## 5. Constraints

- The system must be built using Python as the programming language.
- The system must use SQLite as the database engine (no external DB server).
- The system is limited to a single-machine, single-database-file deployment (SQLite does not support high-concurrency multi-user access).
- No dedicated IT/server infrastructure or budget is available for hosting.
- The application must run on standard college lab computers with no special hardware requirements.
- Development time and resources are limited to what is feasible for a two-user, first-version academic/club project.
