from datetime import datetime, timedelta
from scheduler import find_free_time
from calendar_api import create_event

def agent_schedule(service, query, events):

    query = query.lower()

    if "free" in query:

        slots = find_free_time(events)

        if slots:
            return slots
        else:
            return []

    if "meeting" in query:

        tomorrow = datetime.now() + timedelta(days=1)

        start = tomorrow.replace(hour=17, minute=0, second=0)
        end = tomorrow.replace(hour=18, minute=0, second=0)

        create_event(
            service,
            "Agent Meeting",
            start.isoformat(),
            end.isoformat()
        )

        return "Event Scheduled"

    return "Query not understood"