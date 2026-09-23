import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def login(username="User1", password="password123"):
    res = client.post("/api/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, res.text
    return res.json()["token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_login_and_protected_routes():
    bad = client.post("/api/auth/login", json={"username": "User1", "password": "wrong"})
    assert bad.status_code == 401
    token = login()
    me = client.get("/api/auth/me", headers=auth(token))
    assert me.status_code == 200
    assert me.json()["username"] == "User1"
    denied = client.get("/api/members")
    assert denied.status_code == 401


def test_member_crud_and_search():
    token = login("User2")
    headers = auth(token)
    created = client.post(
        "/api/members",
        headers=headers,
        json={"name": "Test Student", "email": "test.student@college.edu", "role": "Member"},
    )
    assert created.status_code == 201, created.text
    member_id = created.json()["id"]
    listed = client.get("/api/members?q=test.student", headers=headers)
    assert any(m["id"] == member_id for m in listed.json())
    updated = client.put(
        f"/api/members/{member_id}",
        headers=headers,
        json={"name": "Test Student Updated", "email": "test.student@college.edu", "role": "Secretary"},
    )
    assert updated.json()["role"] == "Secretary"
    deleted = client.delete(f"/api/members/{member_id}", headers=headers)
    assert deleted.status_code == 200


def test_club_event_registration_attendance_report():
    token = login()
    headers = auth(token)
    club = client.post("/api/clubs", headers=headers, json={"name": "Drama Club", "description": "Stage productions"})
    assert club.status_code == 201
    club_id = club.json()["id"]
    member = client.post(
        "/api/members",
        headers=headers,
        json={"name": "Rita Rao", "email": "rita@college.edu", "role": "Member", "club_id": club_id},
    )
    member_id = member.json()["id"]
    event = client.post(
        "/api/events",
        headers=headers,
        json={"name": "Orientation Night", "event_date": "2026-09-20", "description": "Welcome event", "club_id": club_id},
    )
    event_id = event.json()["id"]
    reg = client.post("/api/registrations", headers=headers, json={"event_id": event_id, "member_id": member_id})
    assert reg.status_code == 201
    att = client.post(
        "/api/attendance",
        headers=headers,
        json={"event_id": event_id, "member_id": member_id, "status": "present"},
    )
    assert att.status_code == 201
    dash = client.get("/api/dashboard", headers=headers)
    assert dash.status_code == 200
    assert dash.json()["stats"]["clubs"] >= 1
    report = client.get("/api/reports", headers=headers)
    assert report.status_code == 200
    assert "by_club" in report.json()
    notice = client.post(
        "/api/announcements",
        headers=headers,
        json={"title": "Rehearsal", "content": "Friday 5pm in the auditorium.", "club_id": club_id},
    )
    assert notice.status_code == 201
