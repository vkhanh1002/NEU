from datetime import date, timedelta

from app.models import CourseOffering

# Reference shifts are a central display convention until the university sets official hours.
STUDY_SHIFTS = (
    ("Ca 1", "07:00", "09:30"),
    ("Ca 2", "09:30", "12:00"),
    ("Ca 3", "13:00", "15:30"),
    ("Ca 4", "15:30", "18:00"),
    ("Ca 5", "18:00", "20:30"),
)
WEEKDAYS = ("", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật")


def _occurrence_date(offering: CourseOffering, today: date) -> date:
    start = offering.semester.starts_on
    end = offering.semester.ends_on
    first = start + timedelta(days=(offering.weekday - start.isoweekday()) % 7)
    candidate = max(first, today)
    candidate += timedelta(days=(offering.weekday - candidate.isoweekday()) % 7)
    if candidate <= end:
        return candidate
    last = end - timedelta(days=(end.isoweekday() - offering.weekday) % 7)
    return last if last >= start else first


def serialize_schedule(offering: CourseOffering, today: date | None = None) -> dict:
    today = today or date.today()
    starts_at = offering.starts_at.strftime("%H:%M")
    ends_at = offering.ends_at.strftime("%H:%M")
    shift = next((name for name, start, end in STUDY_SHIFTS if (start, end) == (starts_at, ends_at)), "Ca linh hoạt")
    return {
        "offering_id": offering.id,
        "course_code": offering.course.code,
        "course_name": offering.course.name,
        "section": offering.section,
        "section_name": f"Lớp học phần {offering.section}",
        "section_code": f"{offering.course.code}-{offering.section}",
        "lecturer": offering.lecturer.full_name if offering.lecturer else "Chưa phân công",
        "lecturer_code": offering.lecturer.code if offering.lecturer else "",
        "weekday": offering.weekday,
        "weekday_label": WEEKDAYS[offering.weekday] if 1 <= offering.weekday <= 7 else "Chưa xác định",
        "class_date": _occurrence_date(offering, today).isoformat(),
        "study_shift": shift,
        "starts_at": starts_at,
        "ends_at": ends_at,
        "room": offering.room,
        "semester_id": offering.semester_id,
        "semester_code": offering.semester.code,
        "semester_name": offering.semester.name,
        "academic_year": offering.semester.academic_year,
        "semester_starts_on": offering.semester.starts_on.isoformat(),
        "semester_ends_on": offering.semester.ends_on.isoformat(),
        "delivery_mode": offering.delivery_mode,
        "note": offering.note,
    }
