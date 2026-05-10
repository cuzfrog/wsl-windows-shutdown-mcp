#!/usr/bin/env python3
"""
MCP server that exposes Windows power management tools.
Run this on the Windows host (not inside WSL).

Requirements:
    pip install mcp[cli]

Usage:
    python shutdown_server.py
    MCP_SHUTDOWN_TOKEN=mysecret python shutdown_server.py
"""

import os
import subprocess
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TOKEN = os.environ.get("MCP_SHUTDOWN_TOKEN", "")
PORT  = int(os.environ.get("MCP_SHUTDOWN_PORT", "8000"))

mcp = FastMCP("windows-shutdown", port=PORT)

def _auth(token: str) -> bool:
    """Return True if token auth is disabled or the token matches."""
    if not TOKEN:
        return True          # no token configured → open access
    return token == TOKEN


def _run(cmd: list[str]) -> tuple[bool, str]:
    """Run a command via cmd.exe shell; return (success, message)."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        shell=True,          # needed so Windows can find shutdown.exe on PATH
    )
    ok  = result.returncode == 0
    msg = (result.stdout or result.stderr or "").strip()
    return ok, msg


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def shutdown_windows(
    delay_seconds: int = 0,
    message: str = "",
    token: str = "",
) -> str:
    """
    Shut down the Windows host machine.

    Args:
        delay_seconds: Seconds to wait before shutdown (0 = immediate).
        message:       Optional message shown to logged-in users (max 512 chars).
        token:         Auth token (required if MCP_SHUTDOWN_TOKEN env var is set).
    """
    if not _auth(token):
        return "Error: Invalid or missing auth token."

    cmd = ["shutdown", "/s", "/t", str(delay_seconds)]
    if message:
        cmd += ["/c", message[:512]]

    ok, msg = _run(cmd)
    return f"Shutdown scheduled in {delay_seconds}s." if ok else f"Error: {msg}"

@mcp.tool()
def cancel_shutdown(token: str = "") -> str:
    """
    Cancel a pending Windows shutdown or restart.

    Args:
        token: Auth token (required if MCP_SHUTDOWN_TOKEN env var is set).
    """
    if not _auth(token):
        return "Error: Invalid or missing auth token."

    ok, msg = _run(["shutdown", "/a"])
    return "Shutdown cancelled." if ok else f"Error: {msg}"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"[mcp-shutdown] Starting SSE server on port {PORT}")
    if TOKEN:
        print("[mcp-shutdown] Auth token is SET — clients must supply it.")
    else:
        print("[mcp-shutdown] WARNING: No MCP_SHUTDOWN_TOKEN set — server is open.")
    mcp.run(transport="sse")
