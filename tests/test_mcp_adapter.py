"""Mocked tests for the optional stdio MCP adapter."""

import asyncio
import sys
from types import SimpleNamespace
from typing import Any

import pytest

from harborlight_responses import mcp_adapter
from harborlight_responses.mcp_adapter import (
    MCPAdapterMalformedResult,
    MCPAdapterUnavailable,
    MCPServerConfig,
    call_mcp_tool,
)


def test_command_construction_uses_argument_list() -> None:
    config = MCPServerConfig(python_executable=sys.executable, module="harborlight_mcp")
    command = config.command()
    assert command == [
        str(__import__("pathlib").Path(sys.executable).resolve()),
        "-m",
        "harborlight_mcp",
    ]


def test_command_rejects_missing_executable() -> None:
    config = MCPServerConfig(
        python_executable=str(__import__("pathlib").Path("missing-python.exe").resolve()),
        module="harborlight_mcp",
    )
    with pytest.raises(MCPAdapterUnavailable, match="existing absolute file"):
        config.command()


class AsyncContext:
    def __init__(self, value: Any) -> None:
        self.value = value

    async def __aenter__(self) -> Any:
        return self.value

    async def __aexit__(self, *args: object) -> None:
        return None


def fake_components(result: Any):
    class ServerParameters:
        def __init__(self, *, command: str, args: list[str]) -> None:
            self.command = command
            self.args = args

    class Session:
        def __init__(self, read: object, write: object) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def initialize(self) -> None:
            return None

        async def call_tool(self, name: str, *, arguments: dict[str, Any]) -> Any:
            return result

    def stdio_client(server: Any) -> AsyncContext:
        assert server.args == ["-m", "harborlight_mcp"]
        return AsyncContext((object(), object()))

    return Session, ServerParameters, stdio_client


def test_successful_mocked_tool_call(monkeypatch: pytest.MonkeyPatch) -> None:
    result = SimpleNamespace(isError=False, structuredContent={"fictional": True})
    monkeypatch.setattr(mcp_adapter, "_load_mcp_components", lambda: fake_components(result))
    output = asyncio.run(
        call_mcp_tool(
            "list_upcoming_renewals",
            {"days": 30},
            config=MCPServerConfig(sys.executable, "harborlight_mcp"),
        )
    )
    assert output == {"fictional": True}


def test_malformed_output(monkeypatch: pytest.MonkeyPatch) -> None:
    result = SimpleNamespace(isError=False, structuredContent=["not", "an", "object"])
    monkeypatch.setattr(mcp_adapter, "_load_mcp_components", lambda: fake_components(result))
    with pytest.raises(MCPAdapterMalformedResult, match="structured object"):
        asyncio.run(
            call_mcp_tool(
                "list_upcoming_renewals",
                {"days": 30},
                config=MCPServerConfig(sys.executable, "harborlight_mcp"),
            )
        )


def test_missing_server_behavior(monkeypatch: pytest.MonkeyPatch) -> None:
    class MissingContext:
        async def __aenter__(self):
            raise FileNotFoundError("controlled missing server")

        async def __aexit__(self, *args: object) -> None:
            return None

    class ServerParameters:
        def __init__(self, *, command: str, args: list[str]) -> None:
            pass

    def missing_client(server: object) -> MissingContext:
        return MissingContext()

    monkeypatch.setattr(
        mcp_adapter,
        "_load_mcp_components",
        lambda: (object, ServerParameters, missing_client),
    )
    with pytest.raises(MCPAdapterUnavailable, match="could not be started"):
        asyncio.run(
            call_mcp_tool(
                "list_upcoming_renewals",
                {"days": 30},
                config=MCPServerConfig(sys.executable, "harborlight_mcp"),
            )
        )


def test_source_contains_no_shell_execution() -> None:
    source = __import__("inspect").getsource(mcp_adapter)
    assert "shell" + "=True" not in source
    assert "subprocess" not in source
