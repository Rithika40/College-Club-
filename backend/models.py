from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False)
    failed_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, default=datetime.utcnow)


class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50), nullable=False)

    members = relationship("Member", back_populates="club")
    events = relationship("Event", back_populates="club")
    announcements = relationship("Announcement", back_populates="club")


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    role = Column(String(60), nullable=False, default="Member")
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    club = relationship("Club", back_populates="members")
    registrations = relationship("Registration", back_populates="member", cascade="all, delete-orphan")
    attendance = relationship("Attendance", back_populates="member", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    event_date = Column(Date, nullable=False)
    description = Column(Text, nullable=False, default="")
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    club = relationship("Club", back_populates="events")
    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")
    attendance = relationship("Attendance", back_populates="event", cascade="all, delete-orphan")


class Registration(Base):
    __tablename__ = "registrations"
    __table_args__ = (UniqueConstraint("event_id", "member_id", name="uq_event_member"),)

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="registrations")
    member = relationship("Member", back_populates="registrations")


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("event_id", "member_id", name="uq_attendance_event_member"),)

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, default="present")
    marked_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="attendance")
    member = relationship("Member", back_populates="attendance")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True)
    title = Column(String(160), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(50), nullable=False)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    club = relationship("Club", back_populates="announcements")
