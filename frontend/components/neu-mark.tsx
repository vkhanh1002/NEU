export const NEU_MARK_URL = "/brand/neu-logo.png";
export const NEU_CAMPUS_IMAGE_URL = "/brand/neu-campus.png";

export function NeuMark({ className = "" }: { className?: string }) {
  return <img className={`neu-mark-image ${className}`} src={NEU_MARK_URL} alt="Biểu tượng NEU" width={612} height={612} />;
}
