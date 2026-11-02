import asyncio
import json
import logging
from app.core.database import SessionLocal
from app.ai.rag import classify_intent, retrieve_context, generate_answer

logger = logging.getLogger(__name__)


async def run_evaluation():
    db = SessionLocal()
    with open("/app/app/ai/evaluation_benchmark.json", "r", encoding="utf-8") as f:
        cases = json.load(f)

    print(f"=== BẮT ĐẦU CHẠY KIỂM THỬ BỘ ĐÁNH GIÁ ({len(cases)} BÀI TEST CHUẨN) ===")
    passed = 0
    failed = 0

    for c in cases:
        q = c["question"]
        intent = classify_intent(q)
        sources = await retrieve_context(db, q, audience="chung", limit=5)
        
        try:
            res = await generate_answer(q, sources, [], intent=intent)
            content = res.content.lower()

            # Check expected keywords
            missing = [kw for kw in c["expected_keywords"] if kw.lower() not in content]
            # Check prohibited keywords
            prohibited_hit = [kw for kw in c["prohibited_keywords"] if kw.lower() in content]

            if not missing and not prohibited_hit:
                print(f"[PASS] #{c['id']} [{c['category']}]: '{q[:40]}...'")
                passed += 1
            else:
                print(f"[FAIL] #{c['id']} [{c['category']}]: '{q[:40]}...'")
                if missing:
                    print(f"       -> Thiếu từ khóa: {missing}")
                if prohibited_hit:
                    print(f"       -> Xuất hiện từ cấm: {prohibited_hit}")
                failed += 1
        except Exception as exc:
            print(f"[ERROR] #{c['id']}: {exc}")
            failed += 1

    total = len(cases)
    accuracy = round(passed / total * 100, 1)
    print("\n================ KẾT QUẢ ĐÁNH GIÁ ================")
    print(f"Tổng số ca kiểm thử: {total}")
    print(f"Số ca ĐẠT (PASS):   {passed}")
    print(f"Số ca KHÔNG ĐẠT:     {failed}")
    print(f"ĐỘ CHÍNH XÁC (ACC):  {accuracy}%")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(run_evaluation())
