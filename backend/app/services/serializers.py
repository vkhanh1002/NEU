from app.models import Applicant, Personnel, Student, SupportTicket


def applicant_public(applicant: Applicant) -> dict:
    return {
        "id": applicant.id, "email": applicant.email, "full_name": applicant.full_name,
        "phone": applicant.phone, "desired_major_id": applicant.desired_major_id,
        "major_name": applicant.major.name, "admission_method": applicant.admission_method,
        "status": applicant.status, "review_note": applicant.review_note,
        "details": applicant.details or {},
        "preferences": [{"major_id": row.major_id, "major_name": row.major.name,
                         "program_name": row.program_name or row.major.name,
                         "preference_order": row.preference_order, "admission_method": row.admission_method}
                        for row in applicant.preferences]
        or [{"major_id": applicant.desired_major_id, "major_name": applicant.major.name,
             "program_name": applicant.major.name, "preference_order": 1,
             "admission_method": applicant.admission_method}],
        "created_at": applicant.created_at, "student_id": applicant.student_id,
    }


def student_public(student: Student) -> dict:
    return {
        "id": student.id, "student_number": student.student_number, "full_name": student.full_name,
        "email": student.email, "phone": student.phone, "major_id": student.major_id,
        "date_of_birth": student.date_of_birth, "gender": student.gender, "address": student.address,
        "emergency_contact": student.emergency_contact,
        "major_name": student.major.name, "cohort": student.cohort, "class_name": student.class_name,
        "study_status": student.study_status, "enrollment_date": student.enrollment_date,
        "is_demo": student.is_demo,
    }


def ticket_public(ticket: SupportTicket) -> dict:
    return {
        "id": ticket.id, "code": ticket.code, "owner_id": ticket.owner_id,
        "owner_name": ticket.owner.full_name, "category": ticket.category, "subject": ticket.subject,
        "description": ticket.description, "priority": ticket.priority, "status": ticket.status,
        "assignee_id": ticket.assignee_id, "created_at": ticket.created_at,
        "satisfaction_rating": ticket.satisfaction_rating, "satisfaction_feedback": ticket.satisfaction_feedback,
        "messages": [{"id": message.id, "author_id": message.author_id, "body": message.body, "created_at": message.created_at} for message in ticket.messages],
        "attachments": [{"id": row.id, "filename": row.filename, "media_type": row.media_type,
                         "size_bytes": row.size_bytes, "uploaded_at": row.created_at} for row in ticket.attachments],
    }


def personnel_public(row: Personnel) -> dict:
    return {
        "id": row.id, "code": row.code, "kind": row.kind, "full_name": row.full_name, "email": row.email,
        "phone": row.phone, "date_of_birth": row.date_of_birth, "gender": row.gender, "address": row.address,
        "avatar_url": row.avatar_url, "education_level": row.education_level, "academic_rank": row.academic_rank,
        "specialty": row.specialty, "faculty_id": row.faculty_id, "faculty_name": row.faculty.name if row.faculty else None,
        "department": row.department, "position": row.position, "start_date": row.start_date,
        "work_status": row.work_status, "notes": row.notes, "is_demo": row.is_demo,
    }
