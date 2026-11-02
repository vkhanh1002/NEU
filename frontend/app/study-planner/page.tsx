"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertCircle,
  Bot,
  Calendar,
  CheckCircle2,
  Clock,
  Filter,
  GraduationCap,
  Plus,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { DemoTag, EmptyState, PageTitle } from "@/components/ui";

type StudyTask = {
  id: string;
  user_id: string;
  title: string;
  course_name: string;
  task_type: "assignment" | "exam" | "quiz" | "project";
  due_date: string;
  priority: "high" | "medium" | "low";
  status: "pending" | "in_progress" | "completed";
  notes: string;
  created_at: string;
  updated_at: string;
};

type StudySummary = {
  total_tasks: number;
  pending_tasks: number;
  upcoming_deadlines: number;
  upcoming_exams: number;
  tasks: StudyTask[];
};

export default function StudyPlannerPage() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<StudyTask[]>([]);
  const [summary, setSummary] = useState<StudySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [modalOpen, setModalOpen] = useState(false);
  const [formBusy, setFormBusy] = useState(false);

  // Form State
  const [title, setTitle] = useState("");
  const [courseName, setCourseName] = useState("");
  const [taskType, setTaskType] = useState<"assignment" | "exam" | "quiz" | "project">("assignment");
  const [dueDate, setDueDate] = useState("");
  const [priority, setPriority] = useState<"high" | "medium" | "low">("medium");
  const [notes, setNotes] = useState("");

  const loadData = async () => {
    if (!user) {
      setLoading(false);
      return;
    }
    try {
      const [tasksRes, summaryRes] = await Promise.all([
        api<StudyTask[]>("/study/tasks"),
        api<StudySummary>("/study/summary"),
      ]);
      setTasks(tasksRes);
      setSummary(summaryRes);
    } catch {
      // Demo fallback if backend is offline or empty
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
  }, [user]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !courseName || !dueDate) return;
    setFormBusy(true);
    try {
      await api<StudyTask>("/study/tasks", {
        method: "POST",
        body: JSON.stringify({
          title,
          course_name: courseName,
          task_type: taskType,
          due_date: new Date(dueDate).toISOString(),
          priority,
          notes,
        }),
      });
      setModalOpen(false);
      setTitle("");
      setCourseName("");
      setDueDate("");
      setNotes("");
      await loadData();
    } catch (err) {
      alert("Không thể lưu mục học tập: " + (err instanceof Error ? err.message : "Đã có lỗi xảy ra"));
    } finally {
      setFormBusy(false);
    }
  };

  const handleToggleStatus = async (task: StudyTask) => {
    const nextStatus = task.status === "completed" ? "pending" : "completed";
    try {
      await api(`/study/tasks/${task.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: nextStatus }),
      });
      setTasks((prev) => prev.map((t) => (t.id === task.id ? { ...t, status: nextStatus } : t)));
      void loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Bạn có chắc chắn muốn xóa mục này?")) return;
    try {
      await api(`/study/tasks/${id}`, { method: "DELETE" });
      setTasks((prev) => prev.filter((t) => t.id !== id));
      void loadData();
    } catch (err) {
      alert("Không thể xóa: " + (err instanceof Error ? err.message : "Lỗi"));
    }
  };

  const filteredTasks = tasks.filter((t) => {
    if (filterType !== "all" && t.task_type !== filterType) return false;
    if (filterStatus === "pending" && t.status === "completed") return false;
    if (filterStatus === "completed" && t.status !== "completed") return false;
    return true;
  });

  const getDaysLeft = (dateStr: string) => {
    const diff = new Date(dateStr).getTime() - new Date().getTime();
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    if (days < 0) return { label: `Quá hạn ${Math.abs(days)} ngày`, alert: true };
    if (days === 0) return { label: "Hôm nay", alert: true };
    if (days === 1) return { label: "Ngày mai", alert: true };
    return { label: `Còn ${days} ngày`, alert: days <= 3 };
  };

  return (
    <div className="study-planner-container">
      <div className="page-title-row">
        <div>
          <div className="eyebrow">HỖ TRỢ NGƯỜI HỌC CÁ NHÂN HÓA</div>
          <h1>Kế hoạch học tập & Lịch thi</h1>
          <p>
            Theo dõi hạn nộp bài tập, lịch thi kết thúc môn và tương tác cùng Study AI để lập thời gian biểu ôn tập khoa học.
          </p>
        </div>
        <div className="title-action">
          <button className="button button-primary" onClick={() => setModalOpen(true)}>
            <Plus size={16} /> Thêm bài tập / Lịch thi
          </button>
        </div>
      </div>

      {/* Stats row */}
      <div className="stat-grid" style={{ marginBottom: 24 }}>
        <div className="stat-card">
          <div className="stat-card-top">
            <span>Deadline sắp tới</span>
            <div className="stat-icon amber">
              <Clock size={16} />
            </div>
          </div>
          <div className="stat-value">{summary?.upcoming_deadlines ?? 0}</div>
          <div className="stat-footer">
            <span>Bài tập & đồ án cần nộp</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-top">
            <span>Lịch thi cận kề</span>
            <div className="stat-icon blue">
              <Calendar size={16} />
            </div>
          </div>
          <div className="stat-value">{summary?.upcoming_exams ?? 0}</div>
          <div className="stat-footer">
            <span>Môn kiểm tra / kết thúc học phần</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-top">
            <span>Nhiệm vụ đang chờ</span>
            <div className="stat-icon violet">
              <GraduationCap size={16} />
            </div>
          </div>
          <div className="stat-value">{summary?.pending_tasks ?? 0}</div>
          <div className="stat-footer">
            <span>Tổng việc học cần xử lý</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-top">
            <span>Trạng thái hoàn thành</span>
            <div className="stat-icon green">
              <CheckCircle2 size={16} />
            </div>
          </div>
          <div className="stat-value">
            {summary && summary.total_tasks > 0
              ? `${Math.round(((summary.total_tasks - summary.pending_tasks) / summary.total_tasks) * 100)}%`
              : "100%"}
          </div>
          <div className="stat-footer">
            <span>Tiến độ học tập hiện tại</span>
          </div>
        </div>
      </div>

      {/* AI Smart Planner Callout */}
      <div className="ai-planner-banner">
        <div className="ai-planner-content">
          <div className="ai-planner-tag">
            <Sparkles size={14} /> AI STUDY PLANNER SẴN SÀNG
          </div>
          <h3>Nhờ Study AI lập lịch ôn thi & sắp xếp thời gian biểu</h3>
          <p>
            AI có thể đọc trực tiếp các deadline và ngày thi ở trên để phân chia bài học theo ngày, gợi ý phương pháp Pomodoro và nhắc nhở ôn luyện đúng lúc.
          </p>
        </div>
        <Link
          href="/assistant"
          className="button button-light"
          style={{ textDecoration: "none", whiteSpace: "nowrap" }}
        >
          <Bot size={16} /> Mở Chat AI Lập kế hoạch
        </Link>
      </div>

      {/* Filter and Content */}
      <div className="planner-main-box">
        <div className="module-toolbar">
          <div className="tab-switch">
            <button
              className={filterType === "all" ? "selected" : ""}
              onClick={() => setFilterType("all")}
            >
              Tất cả <span>{tasks.length}</span>
            </button>
            <button
              className={filterType === "assignment" ? "selected" : ""}
              onClick={() => setFilterType("assignment")}
            >
              Bài tập / Đồ án
            </button>
            <button
              className={filterType === "exam" ? "selected" : ""}
              onClick={() => setFilterType("exam")}
            >
              Lịch thi
            </button>
            <button
              className={filterType === "quiz" ? "selected" : ""}
              onClick={() => setFilterType("quiz")}
            >
              Kiểm tra / Quiz
            </button>
          </div>

          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="select-filter"
            >
              <option value="all">Tất cả trạng thái</option>
              <option value="pending">Chưa hoàn thành</option>
              <option value="completed">Đã hoàn thành</option>
            </select>
          </div>
        </div>

        {/* Task List */}
        {filteredTasks.length === 0 ? (
          <EmptyState
            title="Chưa có mục học tập nào"
            description="Bạn chưa có deadline hoặc lịch thi nào phù hợp với bộ lọc hiện tại. Hãy tạo mới để bắt đầu theo dõi."
          />
        ) : (
          <div className="task-grid">
            {filteredTasks.map((t) => {
              const daysInfo = getDaysLeft(t.due_date);
              const isDone = t.status === "completed";
              return (
                <div key={t.id} className={`task-item-card ${isDone ? "done" : ""}`}>
                  <div className="task-item-header">
                    <button
                      className={`check-circle-btn ${isDone ? "checked" : ""}`}
                      onClick={() => handleToggleStatus(t)}
                      title={isDone ? "Đánh dấu chưa xong" : "Đánh dấu hoàn thành"}
                    >
                      <CheckCircle2 size={20} />
                    </button>
                    <div className="task-info">
                      <span className="task-course">{t.course_name}</span>
                      <h4 className={`task-title ${isDone ? "line-through" : ""}`}>{t.title}</h4>
                    </div>
                    <button
                      className="task-delete-btn"
                      onClick={() => handleDelete(t.id)}
                      title="Xóa mục"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>

                  {t.notes && <p className="task-notes">{t.notes}</p>}

                  <div className="task-item-footer">
                    <div className="task-type-badge">
                      {t.task_type === "exam"
                        ? "Lịch thi"
                        : t.task_type === "assignment"
                        ? "Bài tập"
                        : t.task_type === "quiz"
                        ? "Kiểm tra"
                        : "Đồ án"}
                    </div>

                    <div className={`task-due-badge ${daysInfo.alert && !isDone ? "urgent" : ""}`}>
                      <Calendar size={13} />
                      <span>{new Date(t.due_date).toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" })}</span>
                      <span className="days-countdown">({daysInfo.label})</span>
                    </div>

                    <div className={`priority-tag ${t.priority}`}>
                      {t.priority === "high" ? "Ưu tiên cao" : t.priority === "medium" ? "Trung bình" : "Thấp"}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Modal Add Task */}
      {modalOpen && (
        <div className="modal-backdrop" onClick={() => setModalOpen(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Thêm mục học tập & lịch thi</h3>
              <button className="modal-close" onClick={() => setModalOpen(false)}>
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleCreate} className="form-stack" style={{ marginTop: 14 }}>
              <label>
                Tên bài tập / Sự kiện thi
                <input
                  type="text"
                  required
                  placeholder="Ví dụ: Thi kết thúc học phần Cơ sở dữ liệu"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </label>

              <label>
                Môn học / Học phần
                <input
                  type="text"
                  required
                  placeholder="Ví dụ: Cơ sở dữ liệu"
                  value={courseName}
                  onChange={(e) => setCourseName(e.target.value)}
                />
              </label>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <label>
                  Loại mục
                  <select
                    value={taskType}
                    onChange={(e) => setTaskType(e.target.value as any)}
                  >
                    <option value="assignment">Bài tập về nhà</option>
                    <option value="exam">Lịch thi</option>
                    <option value="quiz">Kiểm tra / Quiz</option>
                    <option value="project">Đồ án / Báo cáo</option>
                  </select>
                </label>

                <label>
                  Mức độ ưu tiên
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as any)}
                  >
                    <option value="high">Cao</option>
                    <option value="medium">Trung bình</option>
                    <option value="low">Thấp</option>
                  </select>
                </label>
              </div>

              <label>
                Hạn chót / Ngày giờ thi
                <input
                  type="datetime-local"
                  required
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                />
              </label>

              <label>
                Ghi chú / Phạm vi ôn tập
                <textarea
                  rows={3}
                  placeholder="Ví dụ: Ôn tập chương 1 đến chương 4, mang theo máy tính Casio..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </label>

              <div style={{ display: "flex", gap: 10, justifyContent: "flex-end", marginTop: 14 }}>
                <button
                  type="button"
                  className="button button-ghost"
                  onClick={() => setModalOpen(false)}
                >
                  Hủy
                </button>
                <button type="submit" className="button button-primary" disabled={formBusy}>
                  {formBusy ? "Đang lưu..." : "Lưu vào kế hoạch"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
