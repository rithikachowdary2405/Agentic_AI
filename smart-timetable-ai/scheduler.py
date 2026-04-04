from datetime import datetime, timedelta


def parse_iso(dt):
    if dt:
        dt = dt.replace("Z", "")
        return datetime.fromisoformat(dt).replace(tzinfo=None)
    return None


def check_conflict(events, start, end):

    for event in events:

        existing_start = parse_iso(event["start"].get("dateTime"))
        existing_end = parse_iso(event["end"].get("dateTime"))

        if existing_start and existing_end:

            if start < existing_end and end > existing_start:
                return True

    return False


def find_free_time(events):

    free_slots = []

    now = datetime.now()

    start_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

    end_day = start_time + timedelta(hours=12)

    current = start_time

    while current < end_day:

        slot_end = current + timedelta(hours=1)

        if not check_conflict(events, current, slot_end):

            free_slots.append(
                (current.strftime("%-I %p"), slot_end.strftime("%-I %p"))
)

        current += timedelta(hours=1)

    return free_slots