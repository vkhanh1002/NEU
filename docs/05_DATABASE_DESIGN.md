# Database design

ORM source: `backend/app/models/entities.py`; migrations `backend/migrations/versions/0001`–`0006`. String UUID primary keys and timestamp mixin are common. See [ERD](06_DATABASE_DIAGRAM.md). `KnowledgeChunk.embedding` is pgvector(1536), with SQLite JSON variant for tests.

| Module | Tables | Core relationships/constraints |
|---|---|---|
| Access | users, notifications | users.email unique; notifications.owner_id → users |
| Catalog/admission | faculties, majors, applicants | Major.code unique; major→faculty; applicant→major; optional unique student_id |
| Student/academic | students, semesters, courses, course_offerings, course_enrollments, exams, conduct_records, student_charges, payment_transactions, assignments, assignment_submissions | student user_id/applicant_id unique optional; offering unique(course,semester,section); enrollment unique(student,offering); conduct unique(student,semester); submission unique(assignment,student) |
| Personnel | personnel | optional unique user_id FK users; optional faculty FK; indexed kind/status |
| Support | support_tickets, ticket_messages, ticket_attachments | ticket owner/assignee→users; child records cascade from ticket |
| Chat/knowledge | chat_conversations, chat_messages, guest_chat_sessions, guest_chat_messages, knowledge_documents, knowledge_chunks, faqs | conversation owner→users; guest uses token_hash; chunk→document; FAQ publication flag |
| News | news_articles, university_events | slug unique; published/status fields |

All listed names come from ORM model declarations; column-by-column nullable/default/type details are defined in the ORM and should be checked there before schema surgery. Migration history must be compared with the target DB via Alembic; do not use `down -v` as a schema repair.
