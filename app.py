import streamlit as st
from datetime import datetime, timedelta
from query_functions import (
    authenticate,
    get_employees,
    get_attendances,
    get_single_employee_details,
    get_absences,
)
from processing_functions import (
    create_attendance_df,
    create_absence_df,
    get_workdays,
)


# Set allowed range of date picker
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)


@st.cache_data()
def cached_authenticate():
    return authenticate()


@st.cache_data
def cached_get_employees(token):
    return get_employees(token)


# Run the authenticate and get_employees functions only once
token = cached_authenticate()
names, ids = cached_get_employees(token)

# --- Input widgets ---

# Create a dropdown menu with names
selected_name = st.selectbox("Select an employee", names)


# Using the date input widget to select a range
selected_range = st.date_input(
    "Select date range",
    value=(start_date, end_date),
    min_value=start_date,
    max_value=end_date,
)

st.divider()

# Find the corresponding ID
if selected_name and (len(selected_range) == 2):
    selected_id = ids[names.index(selected_name)]
    # st.write("Selected ID:", selected_id)

    attendances = get_attendances(token, selected_id, selected_range)
    employee_json = get_single_employee_details(token, selected_id)
    absences = get_absences(token, selected_id, selected_range)
    attendance_df = create_attendance_df(attendances)

    work_hours = employee_json["data"]["attributes"]["weekly_working_hours"]["value"]
    # st.write(employee_json)

    st.write("Weekly work hours: ", work_hours)
    
    col1, col2 = st.columns(2)
    with col1:
        st.header("Attendances")
        st.write(attendance_df)
        # st.write(absences)

    absences_df = create_absence_df(absences)
    
    with col2:
        st.header("Absences")
        st.write(absences_df)


    workdays = get_workdays(selected_range[0], selected_range[1])
    # Find missing workdays, excluding those covered in absences_df
    missing_workdays = [day for day in workdays if day not in attendance_df.index and day not in absences_df.index]
    

    actual_workdays = [day for day in workdays if day not in absences_df.index]
    expected_hours = int(work_hours) / 5 * len(actual_workdays)
    actual_hours = attendance_df['Total'].sum()
    st.write("Expected work hours: ", expected_hours)
    st.write("Actual work hours: ", actual_hours)
    
    st.write(missing_workdays)