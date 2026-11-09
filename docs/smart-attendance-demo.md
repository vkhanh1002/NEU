# Demo Smart Attendance

## Prepare

From the project root, start the local stack and wait for `db` and `backend` to report healthy:

```powershell
docker compose up --build -d
docker compose ps
docker compose logs --tail=100 backend
```

The sample data assigns the lecturer account to classes that have enrolled students. Use an incognito window or sign out when switching accounts.
The seed creates six repeatable demo section `D02` offerings for the lecturer, using the first six courses in the sample catalog. They each have a distinct 13-student roster when the full 20-student seed set is present; re-running the seed does not duplicate offerings or enrollments. Existing section `02` data is left as it is.

| Role | Login | Password |
| --- | --- | --- |
| Lecturer | `lecturer@neu.local` | `NEUStaff2026!` |
| Student 1 | `student@neu.local` | `NEUStudent2026!` |
| Student 2 | `student02@neu.local` | `NEUStudent2026!` |
| Student 3 | `student03@neu.local` | `NEUStudent2026!` |
| Administrator | `admin@neu.local` | `NEUStaff2026!` |

## Grades

As the lecturer, open **Kết quả học tập**, select a class you teach, change one existing score field (0–10) and save. The page shows a before/after audit entry. The matching student's **Kết quả học tập** page reads the same enrollment row. The system does not invent a weighting formula; lecturers edit the existing attendance, midterm, final, total and letter-grade fields explicitly.

## Attendance and review walkthrough

1. Sign in as the lecturer. Open **Lớp học phần** or **Điểm danh**, select an assigned course section, then choose **Mở phiên điểm danh**.
   Open **Xem danh sách** on a class to search and page through its enrolled students. Use **Tra cứu** with a student number, review the returned student and confirm to add that student to this offering. The API checks lecturer ownership and prevents duplicate enrollment.
2. The attendance screen focuses on one enrolled student. Press **Space** to record Có mặt and advance. Use the arrow keys to navigate. Students left untouched remain Vắng when the session is closed.
3. Before closing the session, sign in as `student02@neu.local` and `student03@neu.local` in separate browsers. Open **Lịch sử điểm danh**, select the active class session and choose **Chụp ảnh minh chứng**. Allow camera access; the app captures from the live camera and immediately sends the image. The API timestamps receipt on the server.
4. Return to the lecturer account and choose **Kết thúc phiên**. The two students with evidence may now submit **Yêu cầu điểm danh bù** from their attendance history. They must provide a reason of at least 10 characters. The state remains Vắng while requests are waiting.
5. Open **Yêu cầu điểm danh bù** as the lecturer. Filter by course, class and status, then review each student's reason, image and timestamps. Accept one request and reject the other with a reason. The accepted record becomes Muộn; the rejected record stays Vắng and the reason appears for the student. Students also receive an in-app notification.
6. Sign in as either student to see the updated result in attendance history. Sign in as the administrator and open **Giám sát điểm danh** to view sessions and audit events.

For local testing, `http://localhost:3000` is a browser secure context for camera access. A mobile phone treats `localhost` as the phone itself; use a trusted HTTPS development URL to test from a phone. Camera capture has not been verified on a physical device by this repository test run.

The sample seed provides assigned offerings and enrolled students. It does not pre-create fake camera evidence or attendance requests; create those records through this walkthrough so that image evidence is genuinely submitted by the camera flow.

## Apply the schema and seed updates

The backend container startup runs both commands automatically:

```powershell
alembic upgrade head
python -m app.seed
```

To run them explicitly with Compose while keeping the current PostgreSQL data volume:

```powershell
docker compose build backend
docker compose up -d db
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python -m app.seed
docker compose up --build -d
docker compose ps
```

These commands do not remove or reset the database volume. The additive migration `0015_attendance_makeup_reason` adds the student reason column to existing attendance request tables; a fresh database reaches the same schema through the migration chain.
