import streamlit as st
import pandas as pd
from calendar_api import connect_calendar, create_event, get_events
from scheduler import check_conflict, find_free_time
from datetime import datetime, timedelta
from reminder import send_email_reminder
from streamlit_calendar import calendar
from database import create_tables, save_preferences
from llm_agent import ask_llm
import re
import holidays
import os

st.set_page_config(page_title="Smart Timetable Assistant", layout="wide")

st.title("Smart Timetable Assistant")

menu = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Create Event", "Calendar", "Assignments", "AI Assistant"]
)

service = connect_calendar()
create_tables()

current_year = datetime.now().year
india_holidays = holidays.India(years=[current_year])


# ---------- TIME PARSER ----------
def parse_time_input(time_str):

    time_str = time_str.strip().lower()
    time_str = time_str.replace(".", "")

    formats = [
        "%H:%M",
        "%I:%M%p",
        "%I:%M %p",
        "%I%p",
        "%I %p",
        "%H"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt).time()
        except:
            continue

    raise ValueError("Invalid time format")


semester = st.selectbox("Select Semester", ["Sem 1", "Sem 2"])
user_email = st.text_input("Enter email for reminders")

if user_email:
    save_preferences(user_email, semester)


# ==============================
# DASHBOARD
# ==============================
if menu == "Dashboard":

    st.header("Schedule Dashboard")

    try:
        events = get_events(service)
    except:
        st.error("Calendar API connection failed")
        events = []

    upcoming = []

    for event in events[:5]:
        upcoming.append({
            "Title": event.get("summary", "No Title"),
            "Start": event["start"].get("dateTime", "").replace("T"," ").split("+")[0]
        })

    df = pd.DataFrame(upcoming)

    st.subheader("Upcoming Events")
    st.dataframe(df, use_container_width=True)

    st.subheader("Upcoming Indian Holidays")

    today = datetime.now().date()
    holiday_list = []

    for date, name in india_holidays.items():
        if date >= today:
            holiday_list.append({
                "Date": date,
                "Event": name
            })

    holiday_df = pd.DataFrame(holiday_list[:10])
    st.dataframe(holiday_df, use_container_width=True)


# ==============================
# CREATE EVENT
# ==============================
if menu == "Create Event":

    st.header("Create Event")

    title = st.text_input("Event Title")

    event_type = st.selectbox(
        "Event Type",
        ["Lecture", "Lab", "Tutorial", "Exam", "Personal"]
    )

    start_date = st.date_input("Start Date")
    start_time_text = st.text_input("Start Time (9, 9am, 2:30pm)")

    end_date = st.date_input("End Date")
    end_time_text = st.text_input("End Time (10, 10am, 3pm)")

    is_exam = st.checkbox("Is this an exam?")

    try:
        events = get_events(service)
    except:
        events = []

    if st.button("Add Event"):

        try:

            start_time = parse_time_input(start_time_text)
            end_time = parse_time_input(end_time_text)

            start_dt = datetime.combine(start_date, start_time)
            end_dt = datetime.combine(end_date, end_time)

            if start_dt.date() in india_holidays:
                st.error("Cannot schedule on Indian holiday")
                st.stop()

            if end_dt <= start_dt:
                st.error("End time must be after start time")
                st.stop()

            full_title = f"{event_type} - {title}"

            # FIX: send datetime objects to conflict check
            conflict = check_conflict(events, start_dt, end_dt)

            if conflict:
                st.error("Scheduling conflict detected")
            else:

                create_event(
                    service,
                    full_title,
                    start_dt.isoformat(),
                    end_dt.isoformat()
                )

                if is_exam:
                    study_start = start_dt - timedelta(days=1)

                    create_event(
                        service,
                        f"Study for {title}",
                        study_start.isoformat(),
                        start_dt.isoformat()
                    )

                if user_email:
                    send_email_reminder(user_email, full_title)

                st.success("Event successfully created")

        except Exception as e:
            st.error(f"Error: {e}")


# ==============================
# CALENDAR VIEW
# ==============================
if menu == "Calendar":

    st.header("Calendar View")

    try:
        events = get_events(service)
    except:
        events = []

    calendar_events = []

    for event in events:
        calendar_events.append({
            "title": event.get("summary", "Event"),
            "start": event["start"].get("dateTime", ""),
            "end": event["end"].get("dateTime", "")
        })

    calendar_options = {
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay"
        }
    }

    calendar(events=calendar_events, options=calendar_options)

    df = pd.DataFrame(calendar_events)
    csv = df.to_csv(index=False)

    st.download_button(
        "Export Schedule (CSV)",
        csv,
        "schedule.csv",
        "text/csv"
    )


# ==============================
# ASSIGNMENTS
# ==============================
if menu == "Assignments":

    st.header("Assignment Tracker")

    try:
        assignments = pd.read_csv("assignments.csv")
    except:
        st.error("Assignments file not found")
        assignments = pd.DataFrame()

    today = datetime.now().date()

    for _, row in assignments.iterrows():

        deadline = pd.to_datetime(row["Deadline"]).date()

        if deadline - today <= timedelta(days=2):
            st.error(f"Deadline Soon: {row['Title']}")

            if user_email:
                send_email_reminder(user_email, f"Assignment due: {row['Title']}")

        elif row["Priority"] == "High":
            st.warning(f"High Priority: {row['Title']}")

    st.dataframe(assignments, use_container_width=True)


# ==============================
# AI ASSISTANT
# ==============================
if menu == "AI Assistant":

    st.header("AI Scheduling Assistant")

    query = st.text_input("Example: schedule meeting tomorrow at 5pm")

    try:
        events = get_events(service)
    except:
        events = []

    if query:

        query = query.lower()

        if "free" in query:

            free_slots = find_free_time(events)

            if free_slots:
                for slot in free_slots:
                    st.write("Free from", slot[0], "to", slot[1])
            else:
                st.write("No free slots available")

        elif "schedule" in query:

            tomorrow = datetime.now() + timedelta(days=1)

            match = re.search(r'(\d+)(am|pm)', query)

            if match:
                hour = int(match.group(1))

                if match.group(2) == "pm" and hour != 12:
                    hour += 12
            else:
                hour = 17

            start_time = tomorrow.replace(hour=hour, minute=0, second=0)
            end_time = tomorrow.replace(hour=hour + 1, minute=0, second=0)

            create_event(
                service,
                "AI Event",
                start_time.isoformat(),
                end_time.isoformat()
            )

            if user_email:
                send_email_reminder(user_email, "AI Event")

            st.success(f"Event scheduled at {hour}:00")

        elif "assignment" in query:

            try:
                assignments = pd.read_csv("assignments.csv")
                st.dataframe(assignments)
            except:
                st.write("No assignments available")

        else:
            response = ask_llm(query)
            st.write(response)