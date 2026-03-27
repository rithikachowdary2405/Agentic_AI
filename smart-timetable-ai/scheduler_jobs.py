import schedule
import time
from calendar_api import get_events
from reminder import send_email_reminder
from datetime import datetime


def check_upcoming(service, email):

    try:
        events = get_events(service)
    except:
        return

    now = datetime.now()

    for event in events:

        start = event["start"].get("dateTime")

        if start:

            event_time = datetime.fromisoformat(start.replace("Z",""))

            diff = (event_time - now).total_seconds() / 60

            if 0 < diff < 30:

                send_email_reminder(
                    email,
                    event.get("summary", "Event")
                )


def start_scheduler(service, email):

    schedule.every(10).minutes.do(
        check_upcoming,
        service,
        email
    )

    while True:

        schedule.run_pending()
        time.sleep(1)