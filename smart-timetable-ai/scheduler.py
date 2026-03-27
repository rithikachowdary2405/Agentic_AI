from datetime import datetime, timedelta


def parse_iso(dt):
    if dt:
        dt = dt.replace("Z", "")
        return datetime.fromisoformat(dt).replace(tzinfo=None)
    return None


def check_conflict(events, start, end):

    start_time = parse_iso(start)
    end_time = parse_iso(end)

    for event in events:

        existing_start = parse_iso(event["start"].get("dateTime"))
        existing_end = parse_iso(event["end"].get("dateTime"))

        if existing_start and existing_end:

            if start_time < existing_end and end_time > existing_start:
                return True

    return False


def find_free_time(events):

    free_slots = []

    now = datetime.now()
    end_day = now + timedelta(hours=12)

    current = now

    while current < end_day:

        slot_end = current + timedelta(hours=1)
        conflict = False

        for event in events:

            existing_start = parse_iso(event["start"].get("dateTime"))
            existing_end = parse_iso(event["end"].get("dateTime"))

            if existing_start and existing_end:

                if current < existing_end and slot_end > existing_start:
                    conflict = True
                    break

        if not conflict:
            free_slots.append(
                (current.strftime("%H:%M"), slot_end.strftime("%H:%M"))
            )

        current += timedelta(hours=1)

    return free_slots