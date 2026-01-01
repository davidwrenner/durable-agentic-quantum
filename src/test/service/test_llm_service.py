import pytest
from src.app.services import llm_service


def test_init_api_key_missing(monkeypatch) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "")

    with pytest.raises(AssertionError):
        _ = llm_service.LLMService()


def test_init_api_key_present(monkeypatch) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "key")
    model = "model"
    temp = 1
    mock = True

    service = llm_service.LLMService(model, temp, mock)

    assert service.model == model
    assert service.model_temperature == temp
    assert service.mock == mock


async def test_choose_tool_mock(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "key")
    prompt = "prompt"
    available_tools = []

    function_calls = await llm_service.LLMService(mock=True).choose_tool(
        prompt, available_tools
    )

    assert function_calls
    assert len(function_calls) == 1
    assert function_calls[0].name == "bell_state"


async def test_validate_mock(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "key")
    output = "output"
    prompt = "prompt"

    is_valid = await llm_service.LLMService(mock=True).validate(output, prompt)

    assert is_valid
