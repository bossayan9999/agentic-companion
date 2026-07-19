"""
Example connector. Swap the body of `create_reminder_event` for a real
Google Calendar / Outlook API call once you've got OAuth wired up.
Copy this file's shape for every new connector (email, Slack, Notion, etc.)
"""
from agent.tools.base import registry


@registry.register(
    name="create_calendar_event",
    description="Create a calendar event for the user.",
    parameters={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "start_time": {"type": "string", "description": "ISO 8601 datetime"},
            "notes": {"type": "string"},
        },
        "required": ["title", "start_time"],
    },
)
def create_calendar_event(title: str, start_time: str, notes: str = ""):
    # TODO: replace with real Google Calendar / Outlook API call
    return {"status": "stubbed", "title": title, "start_time": start_time, "notes": notes}
