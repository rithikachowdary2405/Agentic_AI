def check_conflict(events, new_start, new_end):

    for event in events:

        start = event['start'].get('dateTime')
        end = event['end'].get('dateTime')

        if start and end:
            if new_start < end and new_end > start:
                return True

    return False


def find_free_time(events):

    free_slots = []

    for i in range(len(events)-1):

        end_current = events[i]['end'].get('dateTime')
        start_next = events[i+1]['start'].get('dateTime')

        if end_current and start_next:
            free_slots.append((end_current, start_next))

    return free_slots