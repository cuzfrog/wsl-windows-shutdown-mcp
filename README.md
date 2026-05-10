# wsl-mcp-shutdown

A tiny [MCP](https://modelcontextprotocol.io/) server that runs on your **Windows host** and lets an AI agent running inside **WSL** shut down, restart, cancel a shutdown, or lock your machine.

```
WSL agent (Claude / any MCP client)
        │  HTTP + SSE  (localhost:8000)
        ▼
  shutdown_server.py  (runs on Windows)
        │  subprocess
        ▼
  Windows shutdown.exe / rundll32.exe
```

---

## Requirements

| Requirement | Notes |
|---|---|
| **Windows 10 / 11** | Host machine |
| **Python 3.9 or newer** | Must be on `PATH` in `cmd.exe` — verify with `python --version` |
| **WSL 2** | With an MCP-compatible agent (e.g. Claude Code) |

> **Python must already be installed.** Download it from <https://www.python.org/downloads/> and make sure *"Add Python to PATH"* is checked during setup. The installer handles everything else.

---

## Installation (Windows)

1. **Clone or download this repo onto your Windows filesystem** (not inside WSL):

   ```cmd
   git clone https://github.com/your-username/wsl-mcp-shutdown.git
   cd wsl-mcp-shutdown
   ```

   Or download and extract the ZIP from GitHub.

2. **Run the installer** in a plain `cmd.exe` window (no Administrator needed):

   ```cmd
   install.bat
   ```

   The installer will:
   - Create a Python virtual environment (`.venv`) in the repo folder
   - Install the `mcp[cli]` package into it
   - Generate a `start_mcp.bat` launcher with editable settings
   - Copy `start_mcp.bat` to your Windows **Startup** folder so the server launches automatically on login

3. *(Recommended)* **Set an auth token** — open `start_mcp.bat` in Notepad and set:

   ```bat
   set "MCP_SHUTDOWN_TOKEN=your-secret-here"
   ```

   Save the file. Any client calling the server must pass this token as the `token` argument to each tool. Leave it blank to disable auth (only safe on a private machine).

4. **Start the server now** (it will also start automatically after your next login):

   ```cmd
   start_mcp.bat
   ```

   You should see:
   ```
   [mcp-shutdown] Starting SSE server on port 8000
   ```

---

## Configure Your WSL Agent

Add the server to your MCP client config. For **Claude Code** (`~/.claude/claude_mcp_config.json`):

```json
{
  "mcpServers": {
    "windows-shutdown": {
      "type": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

### WSL 2 — if `localhost` doesn't work

WSL 2 has `localhost` forwarding enabled by default on modern Windows builds. If it doesn't work, find your Windows host IP from inside WSL:

```bash
cat /etc/resolv.conf | grep nameserver | awk '{print $2}'
```

Then use that IP (e.g. `http://172.22.16.1:8000/sse`) in your config.

### Quick connectivity test (from WSL bash)

```bash
curl -N http://localhost:8000/sse
# Should print an SSE stream header — Ctrl+C to exit
```

---

## Available Tools

| Tool | What it does |
|---|---|
| `shutdown_windows` | Shuts down Windows (optional delay & message) |
| `cancel_shutdown` | Cancels a pending shutdown or restart |

All tools accept an optional `token` argument (required if `MCP_SHUTDOWN_TOKEN` is set).

---

## Changing the Port

Open `start_mcp.bat` and change:

```bat
set "MCP_SHUTDOWN_PORT=8000"
```

Then update the port in your MCP client config to match.

---

## Auto-start Behaviour

The installer places `start_mcp.bat` in:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
```

This means the server starts automatically **when you log in to Windows**. The window appears briefly in the taskbar; it stays running in the background.

To disable auto-start, delete the shortcut from that Startup folder, or run:

```cmd
uninstall.bat
```

---

## Uninstall

```cmd
uninstall.bat
```

This removes the Startup shortcut and the `.venv` folder. The repo directory itself is left intact.

---

## Security Notes

- The server binds to all interfaces (`0.0.0.0`) by default. It is **strongly recommended** to set `MCP_SHUTDOWN_TOKEN`.
- For extra isolation, configure Windows Firewall to block port 8000 from external networks (allow only `127.0.0.1`).
- The tools call the standard Windows `shutdown.exe` — no third-party binaries, no elevated privileges required for scheduling.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `python not found` | Re-install Python with "Add to PATH" checked; open a fresh `cmd.exe` |
| `pip install failed` | Check your internet connection; run `install.bat` again |
| Agent can't connect | Check the server window is open; try the `curl` test above; check Windows Firewall |
| `Error: Invalid or missing auth token` | Add `"token": "your-secret"` to your tool call arguments |
| Port already in use | Change `MCP_SHUTDOWN_PORT` in `start_mcp.bat` and update MCP config |
