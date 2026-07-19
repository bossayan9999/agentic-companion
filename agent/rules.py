"""
Rules engine: not every tool call should fire automatically. This maps each
tool to a risk tier, and the brain checks this before executing anything.

Tiers:
- "auto"    — safe, read-only or reversible. Runs immediately.
- "approve" — mutates external state or costs money/reputation. Queued for
              human approval before it executes.
- "block"   — never runs from this agent, full stop (placeholder for anything
              you explicitly want to disallow regardless of who asks).

Edit RULES to reclassify a tool, or add a new one as tools are added.
"""

RULES: dict[str, str] = {
    # read-only / passive -> auto
    "osint_whois_lookup": "auto",
    "osint_dns_lookup": "auto",
    "osint_subdomain_discovery": "auto",
    # mutating / external side effects -> approve
    "create_calendar_event": "approve",
    "send_email": "approve",
}

DEFAULT_TIER = "approve"  # unknown tools default to requiring approval, not auto-run


def get_tier(tool_name: str) -> str:
    return RULES.get(tool_name, DEFAULT_TIER)
