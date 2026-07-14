"""Advanced adapter pattern: Responses function tools backed by a local stdio MCP server.

This is not native remote Responses MCP. The model sees ordinary Responses
function tools; Python executes them by opening an MCP client session, and then
Python returns each result as function_call_output.
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from openai import OpenAI

from harborlight_responses.config import require_api_key, resolve_model
from harborlight_responses.mcp_adapter import (
    MCPAdapterError,
    MCPServerConfig,
    build_mcp_registry,
)
from harborlight_responses.tool_loop import run_tool_loop


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument(
        "--python-executable",
        default=sys.executable,
        help="Absolute path to a trusted python/python3 interpreter.",
    )
    result.add_argument(
        "--module",
        default="harborlight_mcp",
        help="Trusted dotted module name for the local stdio MCP server.",
    )
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        require_api_key()
        config = MCPServerConfig(
            python_executable=args.python_executable,
            module=args.module,
        )
        registry = build_mcp_registry(config, run_async=asyncio.run)
        selection = resolve_model()
        result = run_tool_loop(
            OpenAI(),
            model=selection.model,
            input=(
                "Which fictional Harborlight policies renew in 30 days, and what is "
                "the proposed premium change for Fictional Beacon Books?"
            ),
            instructions=(
                "Use the two function tools for all facts. Return a concise fictional "
                "renewal briefing after the tool results are provided."
            ),
            registry=registry,
        )
    except MCPAdapterError as exc:
        print(f"Optional MCP adapter unavailable: {exc}")
        return 2

    print("Adapter pattern completed. Final generated answer:")
    print(result.response.output_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())