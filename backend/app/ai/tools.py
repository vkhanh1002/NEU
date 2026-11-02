"""Structured lookup tools for Study AI."""
import re
from typing import Any
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import AdmissionProgram, AdmissionScore, Department, TuitionFee

STOPWORDS = {
    "ngành", "chuyên", "khoa", "điểm", "chuẩn", "học", "phí",
    "chỉ", "tiêu", "xét", "tuyển", "phương", "thức", "tổ", "hợp", "nào", "mấy",
    "bao", "nhiêu", "thế", "là", "của", "cho", "ở", "đâu", "trường", "đại", "neu", "kinh", "tế", "quốc", "dân"
}

ACRONYM_MAP = {
    "hp": "học phí",
    "ktx": "ký túc xá",
    "dseb": "khoa học dữ liệu dseb",
    "cntt": "công nghệ thông tin",
    "clc": "chất lượng cao",
    "aep": "tiên tiến",
    "bn": "bao nhiêu",
    "qtkd": "quản trị kinh doanh",
    "kdqt": "kinh doanh quốc tế",
    "tckt": "tài chính ngân hàng",
}

def extract_search_keywords(text: str) -> list[str]:
    # Expand acronyms
    normalized = text.lower()
    for acr, expansion in ACRONYM_MAP.items():
        normalized = re.sub(rf"\b{acr}\b", expansion, normalized)
    words = re.findall(r"[\wÀ-ỹ]+", normalized)
    meaningful = [w for w in words if len(w) > 1 and w not in STOPWORDS]
    return meaningful


def get_admission_info(db: Session, query: str = "", year: int | None = None) -> list[dict[str, Any]]:
    """Tra cứu chỉ tiêu, ngành tuyển sinh, tổ hợp môn xét tuyển."""
    all_programs = db.scalars(select(AdmissionProgram).order_by(AdmissionProgram.major_code)).all()
    if year:
        all_programs = [p for p in all_programs if p.year == year]

    keywords = extract_search_keywords(query)
    if not keywords:
        return [
            {
                "major_code": r.major_code,
                "name": r.name,
                "program_type": r.program_type,
                "quota": r.quota,
                "methods": r.methods,
                "subject_groups": r.subject_groups,
                "year": r.year,
                "note": r.note,
            }
            for r in all_programs[:6]
        ]

    matched = []
    for r in all_programs:
        target_text = f"{r.name} {r.major_code} {r.program_type} {r.note}".lower()
        score = sum(1 for kw in keywords if kw in target_text)
        if score > 0:
            matched.append((score, r))

    matched.sort(key=lambda x: x[0], reverse=True)
    results = []
    for _, r in matched:
        results.append({
            "major_code": r.major_code,
            "name": r.name,
            "program_type": r.program_type,
            "quota": r.quota,
            "methods": r.methods,
            "subject_groups": r.subject_groups,
            "year": r.year,
            "note": r.note,
        })
    return results


def get_admission_scores(db: Session, query: str = "", year: int | None = None) -> list[dict[str, Any]]:
    """Tra cứu điểm chuẩn tuyển sinh chính xác theo ngành, năm và phương thức xét tuyển."""
    all_scores = db.scalars(select(AdmissionScore).order_by(AdmissionScore.year.desc(), AdmissionScore.score.desc())).all()
    if year:
        all_scores = [s for s in all_scores if s.year == year]

    keywords = extract_search_keywords(query)
    if not keywords:
        return [
            {
                "program_code": r.program_code,
                "program_name": r.program_name,
                "year": r.year,
                "method": r.method,
                "score": r.score,
                "scale": r.scale,
                "note": r.note,
            }
            for r in all_scores[:8]
        ]

    matched = []
    for r in all_scores:
        target_text = f"{r.program_name} {r.program_code} {r.method} {r.note}".lower()
        score = sum(1 for kw in keywords if kw in target_text)
        if score > 0:
            matched.append((score, r))

    matched.sort(key=lambda x: (x[0], x[1].year), reverse=True)
    results = []
    for _, r in matched:
        results.append({
            "program_code": r.program_code,
            "program_name": r.program_name,
            "year": r.year,
            "method": r.method,
            "score": r.score,
            "scale": r.scale,
            "note": r.note,
        })
    return results


def get_tuition(db: Session, query: str = "", cohort: str = "") -> list[dict[str, Any]]:
    """Tra cứu mức học phí chính thức theo chương trình đào tạo và khóa học."""
    all_tuitions = db.scalars(select(TuitionFee)).all()
    if cohort:
        all_tuitions = [t for t in all_tuitions if cohort.lower() in t.cohort.lower()]

    keywords = extract_search_keywords(query)
    if not keywords:
        return [
            {
                "program_name": r.program_name,
                "cohort": r.cohort,
                "academic_year": r.academic_year,
                "per_credit_vnd": r.per_credit_vnd,
                "per_year_vnd": r.per_year_vnd,
                "note": r.note,
            }
            for r in all_tuitions
        ]

    matched = []
    for r in all_tuitions:
        target_text = f"{r.program_name} {r.program_code} {r.note}".lower()
        score = sum(1 for kw in keywords if kw in target_text)
        if score > 0:
            matched.append((score, r))

    matched.sort(key=lambda x: x[0], reverse=True)
    target_list = matched if matched else [(0, r) for r in all_tuitions]
    results = []
    for _, r in target_list:
        results.append({
            "program_name": r.program_name,
            "cohort": r.cohort,
            "academic_year": r.academic_year,
            "per_credit_vnd": r.per_credit_vnd,
            "per_year_vnd": r.per_year_vnd,
            "note": r.note,
        })
    return results


def get_department_contact(db: Session, topic_or_name: str = "") -> list[dict[str, Any]]:
    """Tra cứu thông tin liên hệ phòng ban, văn phòng chức năng tại NEU theo chủ đề hoặc tên phòng."""
    all_depts = db.scalars(select(Department)).all()
    keywords = extract_search_keywords(topic_or_name)
    if not keywords:
        return [
            {
                "name": r.name,
                "code": r.code,
                "description": r.description,
                "email": r.email,
                "phone": r.phone,
                "location": r.location,
                "office_hours": r.office_hours,
            }
            for r in all_depts
        ]

    matched = []
    for r in all_depts:
        target_text = f"{r.name} {r.code} {r.description} {r.location}".lower()
        score = sum(1 for kw in keywords if kw in target_text)
        if score > 0:
            matched.append((score, r))

    matched.sort(key=lambda x: x[0], reverse=True)
    results = []
    for _, r in matched:
        results.append({
            "name": r.name,
            "code": r.code,
            "description": r.description,
            "email": r.email,
            "phone": r.phone,
            "location": r.location,
            "office_hours": r.office_hours,
        })
    return results

