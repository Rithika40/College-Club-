from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from backend.auth import (
    LOCK_MINUTES,
    MAX_FAILED,
    create_token,
    get_current_user,
    hash_password,
    verify_password,
)
from backend.database import get_db
from backend.models import Announcement, Attendance, Club, Event, Member, Registration, User
from backend.schemas import (
    AnnouncementIn,
    AttendanceIn,
    ClubIn,
    EventIn,
    LoginRequest,
    MemberIn,
    ProfileUpdate,
    RegistrationIn,
)

router = APIRouter()


def _club_out(c: Club) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "created_by": c.created_by,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "member_count": len(c.members or []),
        "event_count": len(c.events or []),
    }


def _member_out(m: Member) -> dict:
    return {
        "id": m.id,
        "name": m.name,
        "email": m.email,
        "role": m.role,
        "club_id": m.club_id,
        "club_name": m.club.name if m.club else None,
    }


def _event_out(e: Event) -> dict:
    return {
        "id": e.id,
        "name": e.name,
        "event_date": e.event_date.isoformat(),
        "description": e.description,
        "club_id": e.club_id,
        "club_name": e.club.name if e.club else None,
        "registration_count": len(e.registrations or []),
    }


# --- Auth ---
@router.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.username) == payload.username.strip().lower()).first()
    now = datetime.utcnow()
    if user and user.locked_until and user.locked_until > now:
        remaining = int((user.locked_until - now).total_seconds() // 60) + 1
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked after 3 failed attempts. Try again in {remaining} minute(s).",
        )
    if not user or not verify_password(payload.password, user.password_hash):
        if user:
            user.failed_attempts = (user.failed_attempts or 0) + 1
            if user.failed_attempts >= MAX_FAILED:
                user.locked_until = now + timedelta(minutes=LOCK_MINUTES)
                user.failed_attempts = 0
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Account locked for 5 minutes after 3 failed login attempts.",
                )
            db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
    user.failed_attempts = 0
    user.locked_until = None
    user.last_activity = now
    db.commit()
    token = create_token(user.username)
    return {
        "token": token,
        "user": {
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
        },
    }


@router.get("/auth/me")
def me(user: User = Depends(get_current_user)):
    return {"username": user.username, "full_name": user.full_name, "email": user.email}


@router.put("/auth/profile")
def update_profile(payload: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.full_name = payload.full_name.strip()
    user.email = payload.email.strip()
    if payload.password:
        user.password_hash = hash_password(payload.password)
    db.commit()
    return {"username": user.username, "full_name": user.full_name, "email": user.email}


# --- Clubs ---
@router.get("/clubs")
def list_clubs(q: str = Query(""), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Club)
    if q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(or_(Club.name.ilike(like), Club.description.ilike(like)))
    return [_club_out(c) for c in query.order_by(Club.name).all()]


@router.post("/clubs", status_code=201)
def create_club(payload: ClubIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    club = Club(name=payload.name.strip(), description=payload.description.strip(), created_by=user.username)
    db.add(club)
    db.commit()
    db.refresh(club)
    return _club_out(club)


@router.put("/clubs/{club_id}")
def update_club(club_id: int, payload: ClubIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found.")
    club.name = payload.name.strip()
    club.description = payload.description.strip()
    db.commit()
    db.refresh(club)
    return _club_out(club)


@router.delete("/clubs/{club_id}")
def delete_club(club_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found.")
    for member in club.members:
        member.club_id = None
    for event in club.events:
        event.club_id = None
    for notice in club.announcements:
        notice.club_id = None
    db.delete(club)
    db.commit()
    return {"ok": True}


# --- Members ---
@router.get("/members")
def list_members(q: str = Query(""), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Member)
    if q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(or_(Member.name.ilike(like), Member.email.ilike(like), Member.role.ilike(like)))
    return [_member_out(m) for m in query.order_by(Member.name).all()]


@router.post("/members", status_code=201)
def create_member(payload: MemberIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exists = db.query(Member).filter(func.lower(Member.email) == payload.email.lower()).first()
    if exists:
        raise HTTPException(status_code=400, detail="A member with this email already exists.")
    if payload.club_id and not db.query(Club).filter(Club.id == payload.club_id).first():
        raise HTTPException(status_code=400, detail="Selected club does not exist.")
    member = Member(name=payload.name.strip(), email=payload.email, role=payload.role.strip(), club_id=payload.club_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return _member_out(member)


@router.put("/members/{member_id}")
def update_member(member_id: int, payload: MemberIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found.")
    other = db.query(Member).filter(func.lower(Member.email) == payload.email.lower(), Member.id != member_id).first()
    if other:
        raise HTTPException(status_code=400, detail="A member with this email already exists.")
    member.name = payload.name.strip()
    member.email = payload.email
    member.role = payload.role.strip()
    member.club_id = payload.club_id
    db.commit()
    db.refresh(member)
    return _member_out(member)


@router.delete("/members/{member_id}")
def delete_member(member_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found.")
    db.delete(member)
    db.commit()
    return {"ok": True}


# --- Events ---
@router.get("/events")
def list_events(q: str = Query(""), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Event)
    if q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(or_(Event.name.ilike(like), Event.description.ilike(like)))
    return [_event_out(e) for e in query.order_by(Event.event_date.desc()).all()]


@router.post("/events", status_code=201)
def create_event(payload: EventIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.club_id and not db.query(Club).filter(Club.id == payload.club_id).first():
        raise HTTPException(status_code=400, detail="Selected club does not exist.")
    event = Event(
        name=payload.name.strip(),
        event_date=payload.event_date,
        description=payload.description.strip(),
        club_id=payload.club_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return _event_out(event)


@router.put("/events/{event_id}")
def update_event(event_id: int, payload: EventIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    event.name = payload.name.strip()
    event.event_date = payload.event_date
    event.description = payload.description.strip()
    event.club_id = payload.club_id
    db.commit()
    db.refresh(event)
    return _event_out(event)


@router.delete("/events/{event_id}")
def delete_event(event_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    db.delete(event)
    db.commit()
    return {"ok": True}


# --- Registrations ---
@router.get("/registrations")
def list_registrations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Registration).order_by(Registration.registered_at.desc()).all()
    return [
        {
            "id": r.id,
            "event_id": r.event_id,
            "member_id": r.member_id,
            "event_name": r.event.name if r.event else None,
            "member_name": r.member.name if r.member else None,
            "registered_at": r.registered_at.isoformat() if r.registered_at else None,
        }
        for r in rows
    ]


@router.post("/registrations", status_code=201)
def create_registration(payload: RegistrationIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == payload.event_id).first()
    member = db.query(Member).filter(Member.id == payload.member_id).first()
    if not event:
        raise HTTPException(status_code=400, detail="Event not found.")
    if not member:
        raise HTTPException(status_code=400, detail="Member not found.")
    exists = (
        db.query(Registration)
        .filter(Registration.event_id == payload.event_id, Registration.member_id == payload.member_id)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="This member is already registered for the event.")
    row = Registration(event_id=payload.event_id, member_id=payload.member_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "event_id": row.event_id,
        "member_id": row.member_id,
        "event_name": event.name,
        "member_name": member.name,
        "registered_at": row.registered_at.isoformat(),
    }


@router.delete("/registrations/{reg_id}")
def delete_registration(reg_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(Registration).filter(Registration.id == reg_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Registration not found.")
    db.delete(row)
    db.commit()
    return {"ok": True}


# --- Attendance ---
@router.get("/attendance")
def list_attendance(event_id: int | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Attendance)
    if event_id:
        query = query.filter(Attendance.event_id == event_id)
    rows = query.order_by(Attendance.marked_at.desc()).all()
    return [
        {
            "id": a.id,
            "event_id": a.event_id,
            "member_id": a.member_id,
            "event_name": a.event.name if a.event else None,
            "member_name": a.member.name if a.member else None,
            "status": a.status,
            "marked_at": a.marked_at.isoformat() if a.marked_at else None,
        }
        for a in rows
    ]


@router.post("/attendance", status_code=201)
def mark_attendance(payload: AttendanceIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == payload.event_id).first()
    member = db.query(Member).filter(Member.id == payload.member_id).first()
    if not event or not member:
        raise HTTPException(status_code=400, detail="Event or member not found.")
    row = (
        db.query(Attendance)
        .filter(Attendance.event_id == payload.event_id, Attendance.member_id == payload.member_id)
        .first()
    )
    if row:
        row.status = payload.status
        row.marked_at = datetime.utcnow()
    else:
        row = Attendance(event_id=payload.event_id, member_id=payload.member_id, status=payload.status)
        db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "event_id": row.event_id,
        "member_id": row.member_id,
        "event_name": event.name,
        "member_name": member.name,
        "status": row.status,
        "marked_at": row.marked_at.isoformat(),
    }


# --- Announcements ---
@router.get("/announcements")
def list_announcements(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Announcement).order_by(Announcement.created_at.desc()).all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "author": a.author,
            "club_id": a.club_id,
            "club_name": a.club.name if a.club else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in rows
    ]


@router.post("/announcements", status_code=201)
def create_announcement(payload: AnnouncementIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.club_id and not db.query(Club).filter(Club.id == payload.club_id).first():
        raise HTTPException(status_code=400, detail="Selected club does not exist.")
    row = Announcement(
        title=payload.title.strip(),
        content=payload.content.strip(),
        author=user.username,
        club_id=payload.club_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "title": row.title,
        "content": row.content,
        "author": row.author,
        "club_id": row.club_id,
        "created_at": row.created_at.isoformat(),
    }


@router.delete("/announcements/{item_id}")
def delete_announcement(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(Announcement).filter(Announcement.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Announcement not found.")
    db.delete(row)
    db.commit()
    return {"ok": True}


# --- Dashboard & reports ---
@router.get("/dashboard")
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    announcements = db.query(Announcement).order_by(Announcement.created_at.desc()).limit(5).all()
    upcoming = db.query(Event).order_by(Event.event_date.asc()).limit(5).all()
    return {
        "user": {"username": user.username, "full_name": user.full_name},
        "stats": {
            "clubs": db.query(Club).count(),
            "members": db.query(Member).count(),
            "events": db.query(Event).count(),
            "registrations": db.query(Registration).count(),
            "attendance": db.query(Attendance).count(),
            "announcements": db.query(Announcement).count(),
        },
        "recent_announcements": [
            {"id": a.id, "title": a.title, "content": a.content, "author": a.author, "created_at": a.created_at.isoformat()}
            for a in announcements
        ],
        "upcoming_events": [_event_out(e) for e in upcoming],
    }


@router.get("/reports")
def reports(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    clubs = db.query(Club).order_by(Club.name).all()
    events = db.query(Event).order_by(Event.event_date.desc()).all()
    club_rows = []
    for c in clubs:
        club_rows.append(
            {
                "club": c.name,
                "members": len(c.members or []),
                "events": len(c.events or []),
                "announcements": len(c.announcements or []),
            }
        )
    event_rows = []
    for e in events:
        registered = len(e.registrations or [])
        present = sum(1 for a in (e.attendance or []) if a.status == "present")
        rate = round((present / registered) * 100, 1) if registered else 0
        event_rows.append(
            {
                "event": e.name,
                "date": e.event_date.isoformat(),
                "club": e.club.name if e.club else "—",
                "registrations": registered,
                "present": present,
                "attendance_rate": rate,
            }
        )
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "totals": {
            "clubs": db.query(Club).count(),
            "members": db.query(Member).count(),
            "events": db.query(Event).count(),
            "registrations": db.query(Registration).count(),
            "present_marks": db.query(Attendance).filter(Attendance.status == "present").count(),
        },
        "by_club": club_rows,
        "by_event": event_rows,
    }
