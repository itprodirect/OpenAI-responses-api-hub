"""Optional adapter from Responses function handlers to a trusted local MCP server."""

from __future__ import annotations

import re
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .schemas import CalculatePremiumChangeArgs, ListUpcomingRenewalsArgs

_MODULE_PATTERN = re.compile(r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*$")
_PYTHON_NAMES = {"python", "python.exe", "python3", "python3.exe"}


class MCPAdapterError(RuntimeError):
    """Base error for the optional local stdio adapter."""


class MCPAdapterUnavailable(MCPAdapterError):
    """Raised when the configured optional server cannot be started."""


class MCPAdapterMalformedResult(MCPAdapterError):
    """Raised when the server does not return expected structured content."""


@dataclass(frozen=True)
class MCPServerConfig:
    """Validated command configuration for one trusted Python module server."""

    python_executable: str = sys.executable
    module: str = "harborlight_mcp"

    def command(self) -> list[str]:
        executable = Path(self.python_executable).expanduser()
        if not executable.is_absolute() or not executable.is_file():
            raise MCPAdapterUnavailable(
                "The configured MCP Python executable must be an existing absolute file."
            )
        if executable.name.lower() not in _PYTHON_NAMES:
            raise MCPAdapterUnavailable(
                "The MCP executable must be a Python interpreter named python or python3."
            )
        if not _MODULE_PATTERN.fullmatch(self.module):
            raise ValueError("The MCP module must be a dotted Python module name.")
        return [str(executable.resolve()), "-m", self.module]


def _load_mcp_components() -> tuple[Any, Any, Any]:
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as exc:
        raise MCPAdapterUnavailable(
            "The optional MCP extra is not installed. Install the project with [mcp]."
        ) from exc
    return ClientSession, StdioServerParameters, stdio_client


async def call_mcp_tool(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    config: MCPServerConfig | None = None,
) -> dict[str, Any]:
    """Call a trusted local stdio MCP tool and require structured object output."""

    active_config = MCPServerConfig() if config is None else config
    command = active_config.command()
    ClientSession, StdioServerParameters, stdio_client = _load_mcp_components()
    server = StdioServerParameters(command=command[0], args=command[1:])
    try:
        async with stdio_client(server) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
    except (FileNotFoundError, ModuleNotFoundError, OSError) as exc:
        raise MCPAdapterUnavailable(
            "The optional Harborlight MCP server could not be started. "
            "Install/configure a trusted server module or run the core demo without MCP."
        ) from exc

    if getattr(result, "isError", False):
        detail = " ".join(
            str(getattr(item, "text", "")) for item in getattr(result, "content", []) or []
        ).strip()
        raise MCPAdapterError(f"MCP tool {tool_name!r} returned an error: {detail or 'unknown'}")
    structured = getattr(result, "structuredContent", None)
    if not isinstance(structured, dict):
        raise MCPAdapterMalformedResult(
            f"MCP tool {tool_name!r} did not return structured object content."
        )
    return structured


def build_mcp_registry(
    config: MCPServerConfig,
    *,
    run_async: Callable[[Any], Any],
) -> dict[str, Callable[[dict[str, Any]], dict[str, Any]]]:
    """Create synchronous Responses handlers backed by the async MCP client."""

    def renewals(arguments: dict[str, Any]) -> dict[str, Any]:
        validated = ListUpcomingRenewalsArgs.model_validate(arguments)
        return run_async(
            call_mcp_tool(
                "list_upcoming_renewals",
                {"days": validated.days},
                config=config,
            )
        )

    def premium(arguments: dict[str, Any]) -> dict[str, Any]:
        validated = CalculatePremiumChangeArgs.model_validate(arguments)
        return run_async(
            call_mcp_tool(
                "calculate_premium_change",
                {
                    "current_cents": validated.current_cents,
                    "renewal_cents": validated.renewal_cents,
                },
                config=config,
            )
        )

    return {
        "list_upcoming_renewals": renewals,
        "calculate_premium_change": premium,
    }