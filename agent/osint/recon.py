"""
Passive OSINT module.

Scope, deliberately: this wraps *public, passive* lookups only —
WHOIS, DNS records, and certificate-transparency-log subdomain discovery.
All of these query public registries/logs, not the target system itself,
and are standard due-diligence/brand-monitoring/recon-phase tools.

What is NOT here on purpose: port scanning, vulnerability scanning, credential
stuffing, exploitation, or anything that sends traffic designed to probe a
system you don't own or have written authorization to test. If you need that
for authorized pentesting, scope it separately with signed rules of engagement
and I can help structure that workflow.
"""
from __future__ import annotations
import whois
import dns.resolver
import httpx
from agent.tools.base import registry


@registry.register(
    name="osint_whois_lookup",
    description="Look up public WHOIS registration data for a domain.",
    parameters={
        "type": "object",
        "properties": {"domain": {"type": "string"}},
        "required": ["domain"],
    },
)
def whois_lookup(domain: str) -> dict:
    w = whois.whois(domain)
    return {
        "domain": domain,
        "registrar": w.registrar,
        "creation_date": str(w.creation_date),
        "expiration_date": str(w.expiration_date),
        "name_servers": w.name_servers,
    }


@registry.register(
    name="osint_dns_lookup",
    description="Resolve public DNS records (A, MX, TXT, NS) for a domain.",
    parameters={
        "type": "object",
        "properties": {
            "domain": {"type": "string"},
            "record_type": {"type": "string", "description": "A, MX, TXT, or NS", "default": "A"},
        },
        "required": ["domain"],
    },
)
def dns_lookup(domain: str, record_type: str = "A") -> dict:
    try:
        answers = dns.resolver.resolve(domain, record_type)
        return {"domain": domain, "record_type": record_type, "records": [r.to_text() for r in answers]}
    except Exception as e:
        return {"domain": domain, "record_type": record_type, "error": str(e)}


@registry.register(
    name="osint_subdomain_discovery",
    description="Discover subdomains via public certificate transparency logs (crt.sh).",
    parameters={
        "type": "object",
        "properties": {"domain": {"type": "string"}},
        "required": ["domain"],
    },
)
def subdomain_discovery(domain: str) -> dict:
    resp = httpx.get(f"https://crt.sh/?q=%25.{domain}&output=json", timeout=15)
    if resp.status_code != 200:
        return {"domain": domain, "error": f"crt.sh returned {resp.status_code}"}
    entries = resp.json()
    subdomains = sorted({e["name_value"] for e in entries})
    return {"domain": domain, "subdomains": subdomains}
