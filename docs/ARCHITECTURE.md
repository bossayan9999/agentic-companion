# Architecture Notes

## Why this shape
- **Tool registry pattern** (agent/tools/base.py) means adding a new connector
  is: write a function, decorate it, done. The brain never needs code changes
  to gain a new capability.
- **Two-tier memory**: vector recall (Chroma) for "what have we talked about"
  fuzzy retrieval, structured facts (SQLite) for durable state like
  preferences and pending reminders. Swap SQLite for Postgres when you scale
  past one process.
- **Tenant-scoped everywhere**: every memory call and fact takes a tenant_id.
  This is what makes the SaaS jump later just an auth-layer problem, not a
  rearchitecture.

## Sandbox (Phase 5, not yet built)
When the agent needs to run arbitrary code (e.g., a script it wrote, or an
OSINT script beyond the built-in passive tools), that execution should happen
in an ephemeral Docker container per task:
- No network access by default; allowlist specific domains per task
- Read-only mount of any input files, writable scratch dir that's discarded
  after the task
- Resource + timeout limits so a runaway task can't consume the host
This mirrors the sandboxing this very environment uses — worth copying that
pattern rather than inventing a new one.

## OSINT scope boundary
Built-in tools (agent/osint/recon.py) only touch public registries/logs:
WHOIS, DNS, certificate transparency. This deliberately excludes anything that
sends probing traffic to a target's live infrastructure. If your use case is
authorized security testing, that's a distinct workflow requiring documented
scope/authorization — it shouldn't share a tool registry with passive
research tools, so it stays out of this scaffold until you need it.

## Next steps to make this run
1. `pip install -r requirements.txt`
2. Set `ANTHROPIC_API_KEY` in your environment
3. `uvicorn api.main:app --reload`
4. POST to `/chat` with `{"tenant_id": "demo", "message": "..."}`
5. Wire scheduler/reminders.py into a startup event once you have a
   notification channel (push/email/websocket) to call
