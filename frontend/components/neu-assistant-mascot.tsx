import { NEU_MARK_URL } from "@/components/neu-mark";

export function NeuAssistantMascot({ mood = "reply", size = 30 }: { mood?: "greeting" | "thinking" | "reply"; size?: number }) {
  return <span className={`neu-assistant-mascot mascot-${mood}`} style={{ width: size, height: size }} role="img" aria-label="Robot trợ lý NEU">
    <span className="neu-robot-head"><img src={NEU_MARK_URL} alt="" /></span>
    <svg className="neu-robot-body" viewBox="0 0 64 34" aria-hidden="true">
      <path d="M12 13c0-4 3-7 7-7h26c4 0 7 3 7 7v13c0 4-3 7-7 7H19c-4 0-7-3-7-7V13Z" fill="#fff" stroke="#165987" strokeWidth="3" />
      <circle cx="24" cy="18" r="2" fill="#165987" /><circle cx="40" cy="18" r="2" fill="#165987" />
      <path d="M27 24c3 3 7 3 10 0" fill="none" stroke="#55a77c" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M32 6V2m-4 0h8" fill="none" stroke="#165987" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M7 14v9m50-9v9" stroke="#55a77c" strokeWidth="3" strokeLinecap="round" />
    </svg>
  </span>;
}
