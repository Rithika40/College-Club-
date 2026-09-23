from sqlalchemy.orm import Session

from backend.auth import hash_password
from backend.database import SessionLocal, engine
from backend.models import Announcement, Attendance, Base, Club, Event, Member, Registration, User


def seed_if_empty() -> None:
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add_all(
                [
                    User(
                        username="User1",
                        password_hash=hash_password("password123"),
                        full_name="User One",
                        email="user1@college.edu",
                    ),
                    User(
                        username="User2",
                        password_hash=hash_password("password123"),
                        full_name="User Two",
                        email="user2@college.edu",
                    ),
                ]
            )
        if db.query(Club).count() == 0:
            tech = Club(name="Tech Club", description="Coding, robotics, and campus tech events.", created_by="User1")
            arts = Club(name="Arts Club", description="Music, theatre, and visual arts.", created_by="User1")
            db.add_all([tech, arts])
            db.flush()
            alice = Member(name="Alice Smith", email="alice@college.edu", role="President", club_id=tech.id)
            bob = Member(name="Bob Jones", email="bob@college.edu", role="Member", club_id=tech.id)
            db.add_all([alice, bob])
            db.flush()
            event = Event(
                name="Tech Symposium",
                event_date=__import__("datetime").date(2026, 4, 15),
                description="Annual coding and robotics showcase.",
                club_id=tech.id,
            )
            db.add(event)
            db.flush()
            db.add(Registration(event_id=event.id, member_id=alice.id))
            db.add(Attendance(event_id=event.id, member_id=alice.id, status="present"))
            db.add(
                Announcement(
                    title="Welcome Spring 2026",
                    content="Club registrations are open. Join a club and sign up for events.",
                    author="User1",
                    club_id=tech.id,
                )
            )
        db.commit()
    finally:
        db.close()
