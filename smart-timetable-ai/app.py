import streamlit as st
import pandas as pd
from calendar_api import connect_calendar, create_event, get_events
from scheduler import check_conflict, find_free_time
from datetime import datetime, timedelta
from reminder import send_email_reminder
import re

st.title("Smart Timetable Assistant")

service = connect_calendar()

# -----------------------
# USER EMAIL
# -----------------------

user_email = st.text_input("Enter your email to receive reminders")

# -----------------------
# TIME PARSER FUNCTION
# -----------------------

def parse_time(text):

    text = text.lower().strip()

    try:
        if "am" in text or "pm" in text:

            if ":" in text:
                return datetime.strptime(text, "%I:%M%p").time()
            else:
                return datetime.strptime(text, "%I%p").time()

        elif ":" in text:
            return datetime.strptime(text, "%H:%M").time()

        else:
            return datetime.strptime(text, "%H").time()

    except:
        raise ValueError


# -----------------------
# CREATE EVENT
# -----------------------

st.header("Create Event")

title = st.text_input("Event Title")

start_date = st.date_input("Start Date")
start_time_text = st.text_input("Start Time (examples: 9, 9:30, 21, 5pm)", "09:00")

end_date = st.date_input("End Date")
end_time_text = st.text_input("End Time (examples: 10, 10:30, 22, 6pm)", "10:00")

events = get_events(service)

if st.button("Add Event"):

    try:
        start_time = parse_time(start_time_text)
        end_time = parse_time(end_time_text)

        start_dt = datetime.combine(start_date, start_time)
        end_dt = datetime.combine(end_date, end_time)

        if end_dt <= start_dt:
            st.error("End time must be after start time")

        else:
            start = start_dt.isoformat()
            end = end_dt.isoformat()

            conflict = check_conflict(events, start, end)

            if conflict:
                st.error("Time Conflict Detected!")

            else:
                create_event(service, title, start, end)

                if user_email:
                    send_email_reminder(user_email, title)

                st.success("Event Created and Reminder Sent")

    except:
        st.error("Invalid time format. Try: 9, 9:30, 21, 5pm, 5:30pm")


# -----------------------
# UPCOMING EVENTS
# -----------------------

st.header("Upcoming Events")

events = get_events(service)

data = []

for event in events:
    data.append({
        "Title": event.get("summary", "No Title"),
        "Start": event["start"].get("dateTime")
    })

df = pd.DataFrame(data)

st.dataframe(df)

# -----------------------
# CLASS TIMETABLE
# -----------------------

st.header("Class Timetable")

timetable = pd.read_csv("timetable.csv")

st.dataframe(timetable)

# -----------------------
# ASSIGNMENTS
# -----------------------

st.header("Assignments")

assignments = pd.read_csv("assignments.csv")

st.dataframe(assignments)

# -----------------------
# AI SCHEDULING ASSISTANT
# -----------------------

st.header("AI Scheduling Assistant")

query = st.text_input("Ask something like: schedule meeting tomorrow at 5pm")

events = get_events(service)

if query:

    query = query.lower()

    # FIND FREE TIME
    if "free" in query:

        free_slots = find_free_time(events)

        if free_slots:
            for slot in free_slots:
                st.write("Free from", slot[0], "to", slot[1])
        else:
            st.write("No free slots found")

    # SCHEDULE EVENT
    elif "schedule" in query:

        title = "New Event"

        tomorrow = datetime.now() + timedelta(days=1)

        match = re.search(r'(\d+)(am|pm)', query)

        if match:
            hour = int(match.group(1))

            if match.group(2) == "pm" and hour != 12:
                hour += 12
        else:
            hour = 17

        start_time = tomorrow.replace(hour=hour, minute=0, second=0)
        end_time = tomorrow.replace(hour=hour+1, minute=0, second=0)

        create_event(service, title, start_time.isoformat(), end_time.isoformat())

        if user_email:
            send_email_reminder(user_email, title)

        st.success(f"Event scheduled tomorrow at {hour}:00 and reminder sent")

    # SHOW ASSIGNMENTS
    elif "assignment" in query:

        df = pd.read_csv("assignments.csv")

        st.dataframe(df)

    else:
        st.write("Sorry, I didn't understand the request.")