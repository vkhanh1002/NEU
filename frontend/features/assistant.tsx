"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Bot, Check, FileText, MessageCircle, MessageSquarePlus, MoreHorizontal, Pencil, Plus, Send, Sparkles, Square, Trash2, UserRound, X } from "lucide-react";
import { api, ApiError, authenticatedFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { EmptyState, ErrorNotice, Loading } from "@/components/ui";

type ChatMessage = { id: string; role: string; content: string; sources: { title: string; excerpt: string; source_type: string }[]; created_at: string };
type Conversation = { id: string; title: string; updated_at: string; messages: ChatMessage[] };
const suggestions = ["Tôi muốn tìm hiểu về các ngành đào tạo.", "Hồ sơ đăng ký xét tuyển gồm những gì?", "Tôi muốn tra cứu tình trạng hồ sơ.", "Làm thế nào để đăng ký hỗ trợ sinh viên?"];

export function Assistant() {
  const { user } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [thinking, setThinking] = useState(false);
  const [error, setError] = useState("");
  const [demoMode, setDemoMode] = useState(false);
  const [providerLabel, setProviderLabel] = useState("");
  const [thinkingStatus, setThinkingStatus] = useState("Đang tìm nguồn và soạn câu trả lời…");
  const [menuId, setMenuId] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const requestController = useRef<AbortController | null>(null);

  async function loadConversations() {
    const rows = await api<Conversation[]>("/assistant/conversations");
    setConversations(rows);
    if (rows.length) {
      const current = rows.find(row => row.id === activeId) ?? rows[0];
      setActiveId(current.id); setMessages(current.messages ?? []);
    } else { setActiveId(""); setMessages([]); }
  }
  useEffect(() => {
    if (!user) { setLoading(false); return; }
    api<Conversation[]>("/assistant/conversations").then(rows => {
      setConversations(rows);
      if (rows.length) { setActiveId(rows[0].id); setMessages(rows[0].messages ?? []); }
      api<{ provider: string; model: string; configured: boolean; fallback_provider: string | null; fallback_configured: boolean }>("/assistant/status")
        .then(status => {
          setDemoMode(!status.configured && !status.fallback_configured);
          setProviderLabel(status.configured
            ? `${status.provider} · ${status.model}${status.fallback_configured ? ` · dự phòng ${status.fallback_provider}` : ""}`
            : status.fallback_configured
              ? `Dự phòng ${status.fallback_provider} · sẽ dùng khi gửi câu hỏi`
              : "Chỉ tra cứu tài liệu");
        }).catch(() => { /* Chat still works if the optional status request fails. */ });
    }).catch(reason => setError(reason.message)).finally(() => setLoading(false));
  }, [user]);
  useEffect(() => { scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" }); }, [messages, thinking]);
  useEffect(() => () => requestController.current?.abort(), []);

  async function newConversation() {
    requestController.current?.abort();
    setError("");
    try {
      const row = await api<Conversation>("/assistant/conversations", { method: "POST", body: JSON.stringify({ title: "Cuộc trò chuyện mới" }) });
      setConversations(current => [row, ...current]); setActiveId(row.id); setMessages([]); setDemoMode(false); inputRef.current?.focus();
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không thể tạo cuộc trò chuyện."); }
  }
  async function chooseConversation(row: Conversation) {
    requestController.current?.abort();
    setActiveId(row.id); setMessages(row.messages ?? []); setDemoMode(false); setError("");
    try {
      const fresh = await api<Conversation>(`/assistant/conversations/${row.id}`);
      if (activeId === row.id) setMessages(fresh.messages ?? []);
    } catch { /* The list already includes the saved conversation messages. */ }
  }
  async function sendMessage(text = input) {
    const prompt = text.trim();
    if (!prompt || thinking || !user) return;
    setInput(""); setError(""); setThinking(true);
    let conversationId = activeId;
    const controller = new AbortController();
    requestController.current = controller;
    const pendingId = `pending-${crypto.randomUUID()}`;
    let receivedTerminalEvent = false;
    try {
      if (!conversationId) {
        const created = await api<Conversation>("/assistant/conversations", { method: "POST", body: JSON.stringify({ title: prompt.slice(0, 70) }) });
        conversationId = created.id; setActiveId(created.id); setConversations(current => [created, ...current]);
      }
      const userMessage: ChatMessage = { id: crypto.randomUUID(), role: "user", content: prompt, sources: [], created_at: new Date().toISOString() };
      setMessages(current => [...current, userMessage, { id: pendingId, role: "assistant", content: "", sources: [], created_at: new Date().toISOString() }]);
      setThinkingStatus("Đang truy xuất tài liệu liên quan…");
      const response = await authenticatedFetch(`/assistant/conversations/${conversationId}/messages/stream`, {
        method: "POST", body: JSON.stringify({ message: prompt }), signal: controller.signal,
        headers: { Accept: "text/event-stream" },
      });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new ApiError(body.detail ?? "Không gửi được câu hỏi đến Study AI.", response.status);
      }
      if (!response.body) throw new ApiError("Trình duyệt không nhận được luồng trả lời.", 0);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      const handleFrame = (frame: string) => {
        const lines = frame.split("\n");
        const eventName = lines.find(line => line.startsWith("event:"))?.slice(6).trim();
        const rawData = lines.filter(line => line.startsWith("data:")).map(line => line.slice(5).trim()).join("\n");
        if (!eventName || !rawData) return;
        const payload = JSON.parse(rawData);
        if (eventName === "status") {
          if (payload.state === "retrieving") setThinkingStatus("Đang truy xuất tài liệu liên quan…");
          else if (payload.state === "requesting") setThinkingStatus("Đang kết nối nhà cung cấp AI…");
          else if (payload.state === "retrying") setThinkingStatus(`${payload.provider === "gemini" ? "Gemini" : "Groq"} đang thử lại (${payload.attempt}/${payload.max_attempts})…`);
          else if (payload.state === "switching") setThinkingStatus(`Đang chuyển từ ${payload.provider} sang ${payload.fallback_provider}…`);
          else if (payload.state === "generating") setThinkingStatus("Đang tạo câu trả lời…");
        } else if (eventName === "token") {
          setMessages(current => current.map(message => message.id === pendingId
            ? { ...message, content: message.content + String(payload.text ?? "") }
            : message));
          setThinkingStatus("Đang tạo câu trả lời…");
        } else if (eventName === "complete") {
          receivedTerminalEvent = true;
          const result = payload as { message: ChatMessage; response_mode: string; provider: string | null; model: string | null; used_fallback: boolean };
          setMessages(current => current.map(message => message.id === pendingId ? result.message : message));
          setDemoMode(result.response_mode !== "cloud");
          setProviderLabel(result.response_mode === "cloud" && result.provider
            ? `${result.provider}${result.model ? ` · ${result.model}` : ""}${result.used_fallback ? " (dự phòng)" : ""}`
            : result.response_mode === "retrieval_only" ? "Chỉ tra cứu tài liệu" : "Tra cứu dữ liệu tài khoản");
          setConversations(current => current.map(row => row.id === conversationId
            ? { ...row, title: row.title === "Cuộc trò chuyện mới" ? prompt.slice(0, 70) : row.title, updated_at: new Date().toISOString() }
            : row));
        } else if (eventName === "error") {
          receivedTerminalEvent = true;
          setMessages(current => current.filter(message => message.id !== pendingId));
          setError(String(payload.message ?? "Study AI tạm thời không thể trả lời."));
        }
      };
      while (true) {
        const { done, value } = await reader.read();
        buffer = (buffer + decoder.decode(value, { stream: !done })).replace(/\r\n/g, "\n");
        let boundary = buffer.indexOf("\n\n");
        while (boundary >= 0) {
          const frame = buffer.slice(0, boundary);
          buffer = buffer.slice(boundary + 2);
          handleFrame(frame);
          boundary = buffer.indexOf("\n\n");
        }
        if (done) break;
      }
      if (!receivedTerminalEvent) throw new ApiError("Kết nối bị đóng trước khi Study AI hoàn tất câu trả lời.", 0);
    } catch (reason) {
      setMessages(current => current.filter(message => message.id !== pendingId));
      if (controller.signal.aborted) setError("Đã dừng tạo câu trả lời. Nội dung chưa hoàn tất không được lưu.");
      else setError(reason instanceof Error ? reason.message : "Không gửi được tin nhắn.");
    } finally {
      requestController.current = null;
      setThinkingStatus("Đang truy xuất tài liệu liên quan…");
      setThinking(false);
    }
  }
  function stopGeneration() { requestController.current?.abort(); }
  async function renameConversation(row: Conversation) {
    const title = window.prompt("Tên cuộc trò chuyện", row.title);
    if (!title?.trim()) return;
    try { const updated = await api<Conversation>(`/assistant/conversations/${row.id}`, { method: "PATCH", body: JSON.stringify({ title: title.trim() }) }); setConversations(current => current.map(item => item.id === row.id ? { ...item, title: updated.title } : item)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không đổi được tên."); }
    setMenuId("");
  }
  async function deleteConversation(row: Conversation) {
    if (!window.confirm(`Xóa cuộc trò chuyện “${row.title}”?`)) return;
    try { await api(`/assistant/conversations/${row.id}`, { method: "DELETE" }); await loadConversations(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không xóa được cuộc trò chuyện."); }
    setMenuId("");
  }

  if (!user) return <div className="assistant-login"><div className="assistant-login-orb"><Bot size={31} /></div><div className="eyebrow">STUDY AI ASSISTANT</div><h1>Trợ lý đại học,<br />theo ngữ cảnh của bạn.</h1><p>Đăng nhập để lưu lịch sử trò chuyện, tra cứu thông tin cá nhân theo quyền và nhận câu trả lời có nguồn tham khảo.</p><div className="assistant-login-note"><Sparkles size={16} /> Study AI chỉ xem được hồ sơ gắn với tài khoản của bạn.</div><div className="assistant-login-hint">Sử dụng nút <strong>Đăng nhập</strong> ở góc trên bên phải.</div></div>;

  return <div className="assistant-layout">
    <aside className="conversation-sidebar"><div className="conversation-head"><div><div className="eyebrow">TRỢ LÝ ĐẠI HỌC</div><h1>AI Assistant</h1></div><button className="new-chat-button" onClick={newConversation} title="Cuộc trò chuyện mới"><Plus size={17} /></button></div>
      <button className="button button-primary full-width new-chat-main" onClick={newConversation}><MessageSquarePlus size={16} /> Cuộc trò chuyện mới</button>
      <div className="conversation-list-label">GẦN ĐÂY <span>{conversations.length}</span></div>
      {loading ? <Loading label="Đang tải hội thoại…" /> : <div className="conversation-list">{conversations.map(row => <div className={`conversation-row ${activeId === row.id ? "active" : ""}`} key={row.id}><button onClick={() => chooseConversation(row)}><MessageSquarePlus size={15} /><span>{row.title}</span></button><div className="conversation-menu-wrap"><button className="conversation-more" onClick={() => setMenuId(menuId === row.id ? "" : row.id)} aria-label="Tùy chọn hội thoại"><MoreHorizontal size={17} /></button>{menuId === row.id && <div className="conversation-menu"><button onClick={() => renameConversation(row)}><Pencil size={14} /> Đổi tên</button><button className="danger" onClick={() => deleteConversation(row)}><Trash2 size={14} /> Xóa cuộc trò chuyện</button></div>}</div></div>)}</div>}
      <div className="conversation-sidebar-foot"><span className="privacy-shield">✓</span><span><strong>Trò chuyện riêng tư</strong><small>Chỉ bạn truy cập được lịch sử này.</small></span></div>
    </aside>
    <section className="chat-main"><div className="chat-topline"><div className="assistant-identity"><span className="assistant-avatar"><Bot size={19} /></span><span><strong>Study AI Assistant</strong><small><i /> Trợ lý tri thức đại học</small></span></div><div className="chat-topline-actions"><div className="model-indicator"><span className="model-dot" />{providerLabel || (demoMode ? "Chỉ tra cứu tài liệu" : "Study AI")}</div><a className="chat-support-link" href="/support"><MessageCircle size={15} /> Tạo yêu cầu hỗ trợ</a></div></div>
      {error && <div className="chat-error"><ErrorNotice message={error} /><button onClick={() => setError("")} aria-label="Đóng"><X size={15} /></button></div>}
      <div className="chat-scroll" ref={scrollRef}>
      {messages.length === 0 ? <div className="chat-welcome"><div className="welcome-mark"><Bot size={27} /></div><div className="eyebrow">STUDY AI ASSISTANT</div><h2>Xin chào {user.full_name.split(" ").slice(-1)[0]}!<br />Hôm nay mình có thể giúp gì?</h2><p>Hỏi về tuyển sinh, ngành đào tạo, thủ tục sinh viên hoặc yêu cầu hỗ trợ. Câu trả lời dựa trên nguồn tri thức hiện có.</p><div className="suggestion-grid">{suggestions.map(prompt => <button key={prompt} onClick={() => sendMessage(prompt)}><span>✦</span>{prompt}</button>)}</div><div className="chat-data-note"><Sparkles size={14} /> Học phí, chỉ tiêu và thông tin ngành trong bản demo chỉ để minh họa.</div></div> : <div className="message-list">{messages.map(message => <MessageBubble key={message.id} message={message} />)}{thinking && <div className="assistant-message"><span className="message-avatar"><Bot size={16} /></span><div className="thinking-bubble"><span /><span /><span />{thinkingStatus}</div></div>}</div>}
      </div>
      <div className="composer-area"><form className="composer" onSubmit={event => { event.preventDefault(); void sendMessage(); }}><textarea ref={inputRef} rows={1} value={input} onChange={event => setInput(event.target.value)} onKeyDown={event => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void sendMessage(); } }} placeholder="Nhập câu hỏi của bạn…" aria-label="Tin nhắn" /><div className="composer-bottom"><span><Sparkles size={13} /> Trả lời có nguồn tham khảo từ Study</span><button type={thinking ? "button" : "submit"} onClick={thinking ? stopGeneration : undefined} disabled={!thinking && !input.trim()} className="send-button" aria-label={thinking ? "Dừng tạo câu trả lời" : "Gửi câu hỏi"}>{thinking ? <Square size={14} /> : <Send size={16} />}</button></div></form><p>AI có thể trả lời chưa chính xác. Kiểm tra các nguồn tham khảo với thông tin quan trọng.</p></div>
    </section>
  </div>;
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const userMessage = message.role === "user";
  if (!userMessage && message.id.startsWith("pending-") && !message.content) return null;
  return <div className={`chat-message-row ${userMessage ? "user-row" : "assistant-row"}`}>{!userMessage && <span className="message-avatar"><Bot size={16} /></span>}<div className="chat-message-content"><div className={`message-bubble ${userMessage ? "user-bubble" : "assistant-bubble"}`}>{userMessage ? <p>{message.content}</p> : <div className="markdown-body"><ReactMarkdown>{message.content}</ReactMarkdown></div>}</div><div className="message-meta">{new Date(message.created_at).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })}{!userMessage && <span><Check size={12} /> Study AI</span>}</div>{!userMessage && message.sources?.length > 0 && <div className="source-list"><div className="source-heading"><FileText size={14} /> Nguồn tham khảo <span>{message.sources.length}</span></div>{message.sources.map((source, index) => <details className="source-item" key={`${source.title}-${index}`}><summary><span className="source-type">{source.source_type}</span><strong>{source.title}</strong><span className="source-expand">+</span></summary><p>{source.excerpt}</p></details>)}</div>}</div>{userMessage && <span className="message-avatar user-message-avatar"><UserRound size={15} /></span>}</div>;
}
