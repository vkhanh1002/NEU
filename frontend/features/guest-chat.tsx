"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { Bot, Maximize2, Minimize2, Plus, Send, Trash2, X } from "lucide-react";
import { api } from "@/lib/api";
import { ChatDisplayMessage, ChatMessageDisplay } from "@/features/chat-message";

const SESSION_KEY = "neu_guest_chat_session_v1";
type GuestReply = { content: string; sources: ChatDisplayMessage["sources"]; provider: string; model: string; suggested_questions: string[] };

export function GuestChat({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState<ChatDisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [error, setError] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const stickToBottom = useRef(true);
  useEffect(() => {
    if (!open || sessionId) return;
    let live = true;
    (async () => {
      let token = window.localStorage.getItem(SESSION_KEY) ?? "";
      if (token) {
        try {
          const restored = await api<{ messages: ChatDisplayMessage[] }>("/assistant/guest-session", { headers: { "X-Guest-Session": token } });
          if (live) { setSessionId(token); setMessages(restored.messages); }
          return;
        } catch { window.localStorage.removeItem(SESSION_KEY); token = ""; }
      }
      const created = await api<{ session_id: string }>("/assistant/guest-session", { method: "POST" });
      if (live) { window.localStorage.setItem(SESSION_KEY, created.session_id); setSessionId(created.session_id); }
    })().catch(reason => { if (live) setError(reason instanceof Error ? reason.message : "Không mở được phiên chat."); });
    return () => { live = false; };
  }, [open, sessionId]);
  useEffect(() => { if (stickToBottom.current) scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" }); }, [messages, busy]);

  async function send(text = input) {
    const question = text.trim();
    if (!question || busy || !sessionId) return;
    setBusy(true); setError(""); setSuggestions([]); setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
    stickToBottom.current = true;
    try {
      const result = await api<GuestReply>("/assistant/guest-messages", {
        method: "POST", headers: { "X-Guest-Session": sessionId }, body: JSON.stringify({ message: question }),
      });
      const now = new Date().toISOString();
      setMessages(current => [...current,
        { id: crypto.randomUUID(), role: "user", content: question, sources: [], created_at: now },
        { id: crypto.randomUUID(), role: "assistant", content: result.content, sources: result.sources ?? [], created_at: new Date().toISOString() },
      ]);
      setSuggestions(result.suggested_questions ?? []);
    } catch (reason) { setInput(current => current.trim() ? current : question); setError(reason instanceof Error ? reason.message : "NEU AI chưa thể trả lời. Nội dung câu hỏi vẫn được giữ để bạn gửi lại."); }
    finally { setBusy(false); }
  }
  async function newConversation() {
    setError(""); setSuggestions([]); setMessages([]);
    try {
      if (sessionId) await api("/assistant/guest-session", { method: "DELETE", headers: { "X-Guest-Session": sessionId } }).catch(() => {});
      const created = await api<{ session_id: string }>("/assistant/guest-session", { method: "POST" });
      window.localStorage.setItem(SESSION_KEY, created.session_id); setSessionId(created.session_id);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Không tạo được cuộc trò chuyện mới."); }
  }
  async function clearHistory() {
    if (!sessionId) return;
    try { await api("/assistant/guest-session", { method: "DELETE", headers: { "X-Guest-Session": sessionId } }); setMessages([]); setSuggestions([]); setError(""); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không xóa được lịch sử."); }
  }
  if (!open) return null;
  return <section className={`guest-chat-window ${expanded ? "expanded" : ""}`} aria-label="Trợ lý tư vấn NEU"><header className="guest-chat-header"><span className="assistant-avatar"><Bot size={19} /></span><span className="guest-chat-title"><strong>Trợ lý NEU AI</strong><small>Tư vấn công khai · không cần đăng nhập</small></span><button title="Cuộc trò chuyện mới" aria-label="Cuộc trò chuyện mới" onClick={() => void newConversation()}><Plus size={17} /></button><button title="Xóa lịch sử" aria-label="Xóa lịch sử" onClick={() => void clearHistory()}><Trash2 size={16} /></button><button title={expanded ? "Thu nhỏ" : "Mở rộng"} aria-label={expanded ? "Thu nhỏ" : "Mở rộng"} onClick={() => setExpanded(!expanded)}>{expanded ? <Minimize2 size={16} /> : <Maximize2 size={16} />}</button><button aria-label="Đóng" onClick={onClose}><X size={18} /></button></header>
    <div className="guest-chat-scroll" ref={scrollRef} onScroll={event => { const el = event.currentTarget; stickToBottom.current = el.scrollHeight - el.scrollTop - el.clientHeight < 72; }}>{messages.length ? <div className="message-list">{messages.map(message => <ChatMessageDisplay key={message.id} message={message} />)}{busy && <div className="assistant-message"><span className="message-avatar"><Bot size={16} /></span><div className="thinking-bubble"><span /><span /><span />Đang tìm nguồn và soạn câu trả lời…</div></div>}</div> : <div className="guest-chat-welcome"><span className="welcome-mark"><Bot size={26} /></span><small>NEU AI · TƯ VẤN TUYỂN SINH</small><h2>Xin chào! Bạn muốn tìm hiểu điều gì?</h2><p>Hỏi về ngành học, tuyển sinh hoặc hướng dẫn trong nguồn tài liệu công khai.</p><div className="suggestion-grid">{["Các ngành đào tạo hiện có?", "Hồ sơ đăng ký gồm những gì?", "Tra cứu thông tin tuyển sinh ở đâu?"] .map(question => <button key={question} onClick={() => void send(question)}>{question}</button>)}</div></div>}</div>
    {error && <p className="guest-chat-error" role="alert">{error}</p>}
    {suggestions.length > 0 && <div className="guest-chat-suggestions">{suggestions.map(question => <button key={question} disabled={busy} onClick={() => void send(question)}>{question}</button>)}</div>}
    <form className="guest-chat-composer" onSubmit={(event: FormEvent) => { event.preventDefault(); void send(); }}><textarea ref={textareaRef} value={input} maxLength={1200} rows={1} onChange={event => { setInput(event.target.value); event.currentTarget.style.height = "auto"; event.currentTarget.style.height = `${Math.min(event.currentTarget.scrollHeight, 112)}px`; }} onKeyDown={event => { if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); void send(); } }} placeholder="Nhập câu hỏi của bạn…" aria-label="Tin nhắn" /><button className="button button-primary" disabled={busy || !input.trim()} aria-label="Gửi câu hỏi">{busy ? "Đang trả lời…" : <Send size={17} />}</button></form><small className="guest-chat-enter-hint">Enter để gửi · Shift + Enter để xuống dòng</small>
    <small className="guest-chat-disclaimer">Câu trả lời dùng tài liệu được công khai; hãy xác nhận thông tin quan trọng với NEU.</small>
  </section>;
}
