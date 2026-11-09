import ReactMarkdown from "react-markdown";
import { Check, FileText, UserRound } from "lucide-react";
import { NeuAssistantMascot } from "@/components/neu-assistant-mascot";

export type ChatDisplayMessage = { id: string; role: string; content: string; sources: { title: string; excerpt: string; source_type?: string }[]; created_at: string };

export function ChatMessageDisplay({ message }: { message: ChatDisplayMessage }) {
  const userMessage = message.role === "user";
  return <div className={`chat-message-row ${userMessage ? "user-row" : "assistant-row"}`}>{!userMessage && <span className="message-avatar"><NeuAssistantMascot size={22} /></span>}<div className="chat-message-content"><div className={`message-bubble ${userMessage ? "user-bubble" : "assistant-bubble"}`}>{userMessage ? <p>{message.content}</p> : <div className="markdown-body"><ReactMarkdown>{message.content}</ReactMarkdown></div>}</div><div className="message-meta">{new Date(message.created_at).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })}{!userMessage && <span><Check size={12} /> NEU AI</span>}</div>{!userMessage && message.sources?.length > 0 && <div className="source-list"><div className="source-heading"><FileText size={14} /> Nguồn tham khảo <span>{message.sources.length}</span></div>{message.sources.map((source, index) => <details className="source-item" key={`${source.title}-${index}`}><summary><span className="source-type">{source.source_type ?? "Tài liệu"}</span><strong>{source.title}</strong><span className="source-expand">+</span></summary><p>{source.excerpt}</p></details>)}</div>}</div>{userMessage && <span className="message-avatar user-message-avatar"><UserRound size={15} /></span>}</div>;
}
