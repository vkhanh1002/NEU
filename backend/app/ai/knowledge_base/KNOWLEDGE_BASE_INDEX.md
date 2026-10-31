# Study AI University Knowledge Base

Metadata convention: `document_id` is stable; `status: draft` means content is not a school policy until approved. Reviewed 2026-10-31. Scope is general Vietnam higher-education guidance plus accurate descriptions of the Study demo. See `knowledge_sources.md` for official references and verification limits.

| File | ID | Domain | Dynamic or stable | Main intents |
|---|---|---|---|---|
| [00_STUDY_OVERVIEW.md](00_STUDY_OVERVIEW.md) | STUDY-KB-000 | System/AI scope and access | Stable system docs; revise with source changes | study_system_guide, out_of_scope |
| [01_ADMISSIONS_GUIDE.md](01_ADMISSIONS_GUIDE.md) | STUDY-KB-001 | Admissions | Year-specific regulation is dynamic | admissions_consultation, application_procedure |
| [02_MAJORS_CAREER_GUIDE.md](02_MAJORS_CAREER_GUIDE.md) | STUDY-KB-002 | 10 majors and careers | General descriptions; curriculum changes | major_information, career_guidance |
| [03_ACADEMIC_GUIDE.md](03_ACADEMIC_GUIDE.md) | STUDY-KB-003 | Teaching/learning | Local academic regulations dynamic | academic_regulations, grade_calculation, course_registration |
| [04_TUITION_SCHOLARSHIP_GUIDE.md](04_TUITION_SCHOLARSHIP_GUIDE.md) | STUDY-KB-004 | Tuition and aid | Highly dynamic; official schedule or DB only | tuition_information, scholarship_information |
| [05_STUDENT_PROFILE_PROCEDURES.md](05_STUDENT_PROFILE_PROCEDURES.md) | STUDY-KB-005 | Student records and procedures | Institutional forms/processes dynamic | student_profile, student_procedure |
| [06_STUDENT_LIFE_GUIDE.md](06_STUDENT_LIFE_GUIDE.md) | STUDY-KB-006 | Student life and study skills | General guidance; internal rules dynamic | general_university_knowledge |
| [07_STUDENT_SUPPORT_GUIDE.md](07_STUDENT_SUPPORT_GUIDE.md) | STUDY-KB-007 | Support center workflow | Study UI behavior; service levels dynamic | student_support, support_ticket_tracking |
| [08_STAFF_LECTURER_GUIDE.md](08_STAFF_LECTURER_GUIDE.md) | STUDY-KB-008 | Staff/lecturer | System docs; HR policy is not supplied | lecturer_information, staff_information |
| [09_STUDY_USER_MANUAL.md](09_STUDY_USER_MANUAL.md) | STUDY-KB-009 | How to use Study | Revise with app release | study_system_guide, account_support |
| [10_UNIVERSITY_FAQ.md](10_UNIVERSITY_FAQ.md) | STUDY-KB-010 | 200 question-answer pairs | Check linked source for current rules | All common intents |
| [11_UNIVERSITY_GLOSSARY.md](11_UNIVERSITY_GLOSSARY.md) | STUDY-KB-011 | Terminology and variants | Stable terms; review periodically | Intent/query normalization |
| [12_CHATBOT_CONVERSATION_SCENARIOS.md](12_CHATBOT_CONVERSATION_SCENARIOS.md) | STUDY-KB-012 | 50 sample dialogs | Training examples, not policy | Multi-turn dialog behavior |
| [13_AI_TRUST_AND_SAFETY.md](13_AI_TRUST_AND_SAFETY.md) | STUDY-KB-013 | Trust, privacy, boundaries | Re-review with law and API changes | Safety fallback |
| [intent_catalog.json](intent_catalog.json) | — | 20 intents and routing hints | Revise when API capabilities change | Intent routing |
| [faq_dataset.json](faq_dataset.json) | — | Structured FAQ data, 200 items | Same governance as FAQ markdown | Retrieval/QA |
| [knowledge_sources.md](knowledge_sources.md) | — | Sources and checked dates | Recheck before policy answers | Provenance |
| [rag_recommendations.md](rag_recommendations.md) | — | Ingestion/retrieval settings | Re-evaluate with corpus and evaluation | RAG operations |
| [README.md](README.md) | — | Admin workflow and gaps | Update with release | Knowledge maintenance |

## Data routing at a glance

Static concepts → RAG. Year-/school-specific rules → approved, versioned official material plus clarification. User-specific state → authenticated backend API with object-level authorization; never infer from RAG. Unsupported workflow → disclose limitation and offer support-ticket path.

The glossary includes 254 term groups; the dialogue set has 50 scenarios. All documents are drafts and are not automatically indexed merely because they exist in this repository. An administrator must upload approved Markdown files through Study.
