import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.api import assistant
from app.models import GuestChatMessage, GuestChatSession


def request_with_session(token: str | None = None) -> Request:
    headers = [(b"x-guest-session", token.encode())] if token else []
    return Request({
        "type": "http", "method": "POST", "scheme": "http", "path": "/api/v1/assistant/guest-messages",
        "query_string": b"", "headers": headers, "client": ("127.0.0.1", 40000), "server": ("test", 80),
    })


def test_guest_chat_session_history_is_persistent_and_isolated(database):
    first = assistant.create_guest_session(request_with_session())
    second = assistant.create_guest_session(request_with_session())
    assert first["session_id"] != second["session_id"]
    req = request_with_session(first["session_id"])
    session_hash = assistant._guest_session_hash(req)
    database.add(GuestChatSession(token_hash=session_hash))
    database.add_all([
        GuestChatMessage(session_hash=session_hash, role="user", content="Tôi muốn tìm hiểu tuyển sinh", sources=[]),
        GuestChatMessage(session_hash=session_hash, role="assistant", content="Câu trả lời có căn cứ.", sources=[{"title": "Hướng dẫn công khai"}]),
    ])
    database.commit()
    restored = assistant.read_guest_session(req, database)
    assert len(restored["messages"]) == 2
    assert restored["messages"][-1]["sources"][0]["title"] == "Hướng dẫn công khai"
    with pytest.raises(HTTPException) as isolated:
        assistant.read_guest_session(request_with_session(second["session_id"]), database)
    assert isolated.value.status_code == 404
    assistant.clear_guest_session(req, database)
    assert assistant.read_guest_session(req, database)["messages"] == []
