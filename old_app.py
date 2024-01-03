from personio_py import Personio
import streamlit as st
from datetime import datetime, timedelta
from collections import defaultdict


p = Personio(client_id='papi-9cecb510-8b07-44f6-b3ca-02dabe0615ae', client_secret='papi-NGYwMjc2MGMtODBjYi00N2EyLThmNzItN2VhNGZjNDkzOTRh')


# Default values for the start and end dates
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)


def get_attendances(name, personio_client, selected_range):
    # Get current month's range
    # now = datetime.now()
    # start_date = datetime(now.year, now.month, 1)
    # end_date = datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)
    
    start_date = selected_range[0]
    end_date = selected_range[1]

    # Search for the employee
    employee = personio_client.search_first(name)
    if not employee:
        return "Employee not found."

    # Get employee ID
    employee_id = employee.id_  # Accessing the ID

    # Get attendances
    attendances = personio_client.get_attendances(employee_id, start_date, end_date)
    return attendances


def sum_attendance_time(attendances):
    daily_totals = defaultdict(timedelta)

    for attendance in attendances:
        # Calculate the duration of each attendance entry
        duration = attendance.end_time - attendance.start_time - timedelta(seconds=attendance.break_duration)

        # Sum the duration by date
        daily_totals[attendance.date] += duration

    # Format the total time per day
    formatted_totals = {date: format_duration(duration) for date, duration in daily_totals.items()}
    return formatted_totals

def format_duration(duration):
    # Convert timedelta to total minutes
    total_minutes = int(duration.total_seconds() / 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}h {minutes}min"

# Streamlit interface
st.title("Employee Attendance Checker")

name_input = st.text_input("Enter employee's first or last name")

# Using the date input widget to select a range
selected_range = st.date_input("Select date range",
                               value=(start_date, end_date),
                               min_value=start_date,
                               max_value=end_date)



if name_input and (len(selected_range) == 2):
    attendances = get_attendances(name_input, p, selected_range)
    if isinstance(attendances, str):
        st.error(attendances)
    else:
        daily_attendance_summary = sum_attendance_time(attendances)
        for date, total_time in daily_attendance_summary.items():
            st.write(f"{date}: {total_time}")
        st.write(attendances[0])