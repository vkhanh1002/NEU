import asyncio
import json

import httpx

from app.ai.providers import AIProviderManager, GeminiProvider, GroqProvider, ProviderChunk, ProviderError, _provider_error
from app.core.config import settings


class StubProvider:
    def __init__(self, name, outcomes, configured=True):
        self.name = name
        self.model = f"{name}-test-model"
        self.outcomes = list(outcomes)
        self.configured = configured
        self.calls = 0

    async def stream(self, *_args):
        self.calls += 1
        result = self.outcomes.pop(0)
        if isinstance(result, Exception):
            raise result
        yield ProviderChunk(text=result, model=self.model, input_tokens=17, output_tokens=4)


def provider_error(name="groq", status=503, code="UNAVAILABLE", kind="temporarily_unavailable", retry_after=None):
    return ProviderError(name, status, code, error_kind=kind, retry_after=retry_after)


def manager_with(groq, gemini):
    manager = AIProviderManager()
    manager.providers = {"groq": groq, "gemini": gemini}
    return manager


def test_groq_primary_stream_success(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "groq")
    groq = StubProvider("groq", ["answer"])
    gemini = StubProvider("gemini", [], configured=False)
    events = asyncio.run(_collect(manager_with(groq, gemini)))
    assert "".join(event.text for event in events if event.event == "token") == "answer"
    done = next(event for event in events if event.event == "complete")
    assert (done.provider, done.model, done.used_fallback) == ("groq", "groq-test-model", False)
    assert done.metrics["input_tokens"] == 17 and done.metrics["output_tokens"] == 4
    assert groq.calls == 1


async def _collect(manager, **kwargs):
    return [event async for event in manager.stream("sys", [], "q", **kwargs)]


def test_groq_503_retries_once_then_succeeds(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "groq")
    async def no_sleep(_delay): pass
    monkeypatch.setattr("app.ai.providers.asyncio.sleep", no_sleep)
    groq = StubProvider("groq", [provider_error(), "answer"])
    states = []
    events = asyncio.run(_collect(manager_with(groq, StubProvider("gemini", [], configured=False)), on_status=states.append))
    assert groq.calls == 2
    assert [event.text for event in events if event.event == "token"] == ["answer"]
    assert any(state["state"] == "retrying" and state["attempt"] == 2 for state in states)


def test_groq_503_twice_falls_back_to_gemini(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "groq")
    async def no_sleep(_delay): pass
    monkeypatch.setattr("app.ai.providers.asyncio.sleep", no_sleep)
    groq = StubProvider("groq", [provider_error(), provider_error()])
    gemini = StubProvider("gemini", ["Gemini answer"])
    states = []
    events = asyncio.run(_collect(manager_with(groq, gemini), on_status=states.append))
    done = next(event for event in events if event.event == "complete")
    assert groq.calls == 2 and gemini.calls == 1
    assert (done.provider, done.used_fallback) == ("gemini", True)
    assert any(state["state"] == "switching" and state["fallback_provider"] == "gemini" for state in states)
    assert done.metrics["retry_count"] == 1 and done.metrics["fallback_count"] == 1


def test_both_providers_fail_with_bounded_attempts(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "groq")
    async def no_sleep(_delay): pass
    monkeypatch.setattr("app.ai.providers.asyncio.sleep", no_sleep)
    groq = StubProvider("groq", [provider_error(), provider_error()])
    gemini = StubProvider("gemini", [provider_error("gemini" )])
    try:
        asyncio.run(_collect(manager_with(groq, gemini)))
        assert False, "Expected both providers to fail"
    except ProviderError as exc:
        assert exc.provider == "gemini"
        assert exc.metrics["retry_count"] == 1
        assert exc.metrics["fallback_count"] == 1
    assert groq.calls == 2 and gemini.calls == 1


def test_auth_and_input_errors_do_not_retry_or_fallback(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "groq")
    for status in (400, 401, 403, 404):
        groq = StubProvider("groq", [provider_error(status=status, code="CONFIG_OR_INPUT_ERROR")])
        gemini = StubProvider("gemini", ["must not be called"])
        try:
            asyncio.run(_collect(manager_with(groq, gemini)))
            assert False, f"Expected status {status} failure"
        except ProviderError as exc:
            assert exc.status_code == status
        assert groq.calls == 1 and gemini.calls == 0


def test_quota_429_skips_retry_and_uses_fallback(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "groq")
    limited = ProviderError("groq", 429, "QUOTA_EXCEEDED", error_kind="quota_exhausted")
    groq = StubProvider("groq", [limited])
    gemini = StubProvider("gemini", ["fallback answer"])
    events = asyncio.run(_collect(manager_with(groq, gemini)))
    done = next(event for event in events if event.event == "complete")
    assert groq.calls == 1 and gemini.calls == 1
    assert done.provider == "gemini" and done.used_fallback


def test_temporary_rate_limit_retries_only_when_retry_after_fits_budget(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "groq")
    delays = []
    async def record_sleep(delay): delays.append(delay)
    monkeypatch.setattr("app.ai.providers.asyncio.sleep", record_sleep)
    groq = StubProvider("groq", [ProviderError("groq", 429, "RATE_LIMITED", error_kind="rate_limited", retry_after=0), "ok"])
    asyncio.run(_collect(manager_with(groq, StubProvider("gemini", [], configured=False)), budget_seconds=2))
    assert groq.calls == 2 and delays == [0]


def test_provider_error_classifies_quota_and_reads_retry_after():
    quota = httpx.Response(429, json={"error": {"status": "RESOURCE_EXHAUSTED", "message": "Daily quota exceeded"}})
    assert _provider_error("gemini", quota).error_kind == "quota_exhausted"
    limited = httpx.Response(429, headers={"retry-after": "2"}, json={"error": {"status": "RATE_LIMITED"}})
    assert _provider_error("groq", limited).retry_after == 2


def test_no_fallback_after_partial_stream_output(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "groq")
    class PartialProvider(StubProvider):
        async def stream(self, *_args):
            self.calls += 1
            yield ProviderChunk(text="partial", model=self.model)
            raise provider_error()
    groq = PartialProvider("groq", [])
    gemini = StubProvider("gemini", ["fallback must not be spliced"])
    try:
        asyncio.run(_collect(manager_with(groq, gemini)))
        assert False, "Expected partial generation failure"
    except ProviderError as exc:
        assert exc.partial_output is True
    assert groq.calls == 1 and gemini.calls == 0


def test_gemini_adapter_streams_only_answer_text_and_hides_key(monkeypatch):
    captured = {}
    body = b'data: {"candidates":[{"content":{"parts":[{"text":"Xin "},{"text":"chao"}]}}]}\n\n'
    async def handler(request):
        captured["url"] = str(request.url)
        captured["key_header"] = request.headers.get("x-goog-api-key")
        captured["payload"] = json.loads(request.content)
        return httpx.Response(200, content=body)
    transport = httpx.MockTransport(handler)
    real_client = httpx.AsyncClient
    class ClientFactory:
        def __init__(self, **kwargs): self.client = real_client(transport=transport, **kwargs)
        async def __aenter__(self): return await self.client.__aenter__()
        async def __aexit__(self, *args): return await self.client.__aexit__(*args)
    monkeypatch.setattr("app.ai.providers.httpx.AsyncClient", ClientFactory)
    monkeypatch.setattr(settings, "gemini_api_key", "test-secret-never-logged")
    monkeypatch.setattr(settings, "gemini_model", "gemini-3.8-flash")
    async def collect():
        return [chunk async for chunk in GeminiProvider().stream("sys", [], "q", 450, 8)]
    chunks = asyncio.run(collect())
    assert "".join(chunk.text for chunk in chunks) == "Xin chao"
    assert captured["url"].endswith(":streamGenerateContent?alt=sse")
    assert captured["key_header"] == "test-secret-never-logged"
    assert "test-secret-never-logged" not in captured["url"]
    assert captured["payload"]["generationConfig"]["maxOutputTokens"] == 450
    assert captured["payload"]["generationConfig"]["thinkingConfig"]["includeThoughts"] is False


def test_groq_adapter_validates_20b_and_sends_supported_streaming_options(monkeypatch):
    captured = {"requests": []}
    async def handler(request):
        captured["requests"].append(request)
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": [{"id": "openai/gpt-oss-20b"}]})
        captured["payload"] = json.loads(request.content)
        content = (b'data: {"choices":[{"delta":{"content":"OK"}}]}\n\n'
                   b'data: {"choices":[],"usage":{"prompt_tokens":11,"completion_tokens":1}}\n\n'
                   b'data: [DONE]\n\n')
        return httpx.Response(200, content=content)
    real_client = httpx.AsyncClient
    transport = httpx.MockTransport(handler)
    class ClientFactory:
        def __init__(self, **kwargs): self.client = real_client(transport=transport, **kwargs)
        async def __aenter__(self): return await self.client.__aenter__()
        async def __aexit__(self, *args): return await self.client.__aexit__(*args)
    monkeypatch.setattr("app.ai.providers.httpx.AsyncClient", ClientFactory)
    monkeypatch.setattr(settings, "groq_api_key", "test-groq-key")
    monkeypatch.setattr(settings, "groq_model", "openai/gpt-oss-20b")
    monkeypatch.setattr(GroqProvider, "_models", [])
    monkeypatch.setattr(GroqProvider, "_models_loaded_at", 0.0)
    async def collect(): return [chunk async for chunk in GroqProvider().stream("sys", [], "q", 450, 8)]
    chunks = asyncio.run(collect())
    assert "".join(chunk.text for chunk in chunks) == "OK"
    assert any(chunk.input_tokens == 11 and chunk.output_tokens == 1 for chunk in chunks)
    payload = captured["payload"]
    assert payload["model"] == "openai/gpt-oss-20b"
    assert payload["stream"] is True and payload["reasoning_effort"] == "low"
    assert payload["include_reasoning"] is False and payload["max_completion_tokens"] == 450


def test_configured_groq_model_must_be_available_and_no_120b_silent_switch(monkeypatch):
    monkeypatch.setattr(settings, "groq_api_key", "test-key")
    monkeypatch.setattr(settings, "groq_model", "openai/gpt-oss-20b")
    monkeypatch.setattr(GroqProvider, "_models", ["openai/gpt-oss-120b"])
    monkeypatch.setattr(GroqProvider, "_models_loaded_at", 10**12)
    try:
        asyncio.run(GroqProvider()._select_model(2))
        assert False, "20B should be required by this configuration"
    except ProviderError as exc:
        assert exc.code == "configured_model_unavailable"


def test_twenty_study_topics_complete_with_mocked_provider(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "groq")
    questions = [
        "Hồ sơ đăng ký xét tuyển cần những giấy tờ nào?", "Các phương thức tuyển sinh hiện có là gì?",
        "Tôi xem lịch tuyển sinh ở đâu?", "Trường có những ngành đào tạo nào?", "Ngành công nghệ thông tin học gì?",
        "Làm sao chọn ngành phù hợp với sở thích?", "Học phí được tính theo năm hay tín chỉ?", "Có học bổng cho sinh viên không?",
        "GPA là gì và được tính như thế nào?", "Một học kỳ thường đăng ký bao nhiêu tín chỉ?",
        "Điều kiện để đăng ký học lại là gì?", "Quy chế cảnh báo học vụ hoạt động ra sao?",
        "Tôi cập nhật hồ sơ sinh viên ở đâu?", "Thủ tục xin giấy xác nhận sinh viên gồm bước nào?",
        "Làm sao xin bảng điểm?", "Tôi đổi thông tin liên hệ ở đâu?", "Cách gửi yêu cầu hỗ trợ cho trường?",
        "Tôi theo dõi trạng thái yêu cầu hỗ trợ thế nào?", "Làm thế nào tải tài liệu lên kho tri thức?",
        "Study AI lấy câu trả lời từ nguồn nào?",
    ]
    provider = StubProvider("groq", [f"mock answer {index}" for index in range(len(questions))])
    manager = manager_with(provider, StubProvider("gemini", [], configured=False))
    async def run_all():
        answers = []
        for question in questions:
            answers.append(await manager.generate("system", [], question))
        return answers
    results = asyncio.run(run_all())
    assert len(results) == 20 and provider.calls == 20
    assert all(result.provider == "groq" and result.text.startswith("mock answer") for result in results)

