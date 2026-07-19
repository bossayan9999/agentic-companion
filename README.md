# Agentic AI Companion

A self-learning, memory-persistent AI agent that:
- Remembers what you're doing across sessions
- Connects to tools you choose (calendar, email, APIs, custom scripts)
- Proactively reminds you of tasks
- Runs autonomously with a "brain" (planner/orchestrator) + pluggable "skills"
- Executes risky/exploratory work in a sandboxed container
- Includes an OSINT research module for passive, public-source intelligence gathering
- Is architected multi-tenant from day one (SaaS-ready)

## Stack
- **Backend**: Python 3.11, FastAPI
- **Brain**: LLM orchestrator with tool-calling loop (agent/brain.py)
- **Memory**: ChromaDB (vector) + SQLite/Postgres (structured facts, state)
- **Scheduler**: APScheduler for reminders/proactive nudges
- **Sandbox**: Docker container per task execution (not yet wired — see docs/ARCHITECTURE.md)
- **Auth/SaaS**: stubbed multi-tenant scaffolding in saas/

## Phased build order (recommended)
1. **Phase 1 — Brain + Memory** (this scaffold): core loop that can converse, call tools, and persist memory
2. **Phase 2 — Tool connectors**: calendar/email/webhooks registered into the tool registry
3. **Phase 3 — Scheduler/reminders**: background watcher that nudges based on memory state
4. **Phase 4 — OSINT module**: passive recon tools (WHOIS, DNS, cert transparency, breach-check APIs)
5. **Phase 5 — Sandbox**: Dockerized execution environment for agent-run code/scripts
6. **Phase 6 — SaaS shell**: auth, billing, per-tenant memory isolation, dashboard

## Important note on OSINT scope
The OSINT module in this scaffold wraps only **passive, public-source** lookups (WHOIS,
DNS records, certificate transparency logs, public breach-check APIs like HaveIBeenPwned).
It does not include active exploitation, scanning of systems you don't own/have permission
to test, or malware-adjacent tooling. If your use case is authorized penetration testing,
that scope needs explicit rules of engagement — happy to help structure that separately
once you have written authorization.

## Multi-model access (OpenRouter)
One API key, access to virtually any model, no separate accounts per provider.
- Get a key: https://openrouter.ai/keys
- Browse models + live pricing: https://openrouter.ai/models
- Docs: https://openrouter.ai/docs

Set `OPENROUTER_API_KEY` in your environment, then pass `model` in your `/chat`
request (see api/main.py). Built-in aliases (agent/providers/registry.py):
`claude`, `gpt4o`, `gemini`, `llama`, `deepseek`, `grok` — or use any OpenRouter
slug directly.

## Rules-based skills + approval
Every tool is classified in agent/rules.py as `auto` (runs immediately),
`approve` (queued, waits for your sign-off), or `block` (never runs). Unknown
new tools default to `approve` — safe by default. Check pending approvals at
`GET /approvals/{tenant_id}` and decide at `POST /approvals/{id}/decide`.

## Setup
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```
