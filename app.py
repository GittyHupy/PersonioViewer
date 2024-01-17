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

if 'show_json' not in st.session_state:
    st.session_state['show_json'] = False

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
    attendance_df.to_excel('temp_attendance_file.xlsx', index=True)
    # st.write(attendances)

    weekly_work_hours = employee_json["data"]["attributes"]["weekly_working_hours"]["value"]
    daily_work_hours = employee_json["data"]["attributes"]["work_schedule"]["value"]["attributes"]["monday"]
    # st.write(employee_json)

    st.write("Weekly work hours: ", weekly_work_hours)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Attendances")
        st.write(attendance_df)
        # st.write(absences)
        # Streamlit download button
        with open('temp_attendance_file.xlsx', 'rb') as file:
            st.download_button(label='Download Excel file', 
                            data=file, 
                            file_name='attendances.xlsx', 
                            mime='application/vnd.ms-excel')

    absences_df = create_absence_df(absences)
    absences_df.to_excel('temp_absences_file.xlsx', index=True)

    
    with col2:
        st.subheader("Absences")
        st.write(absences_df)
        # Streamlit download button
        with open('temp_attendance_file.xlsx', 'rb') as file:
            st.download_button(label='Download Excel file', 
                            data=file, 
                            file_name='absences.xlsx', 
                            mime='application/vnd.ms-excel')


    workdays = get_workdays(selected_range[0], selected_range[1])
    # Find missing workdays, excluding those covered in absences_df
    missing_workdays = [day for day in workdays if day not in attendance_df.index and day not in absences_df.index]
    
    actual_workdays = len([day for day in workdays if day not in absences_df.index])
    datetime_obj = timedelta(hours=int(daily_work_hours.split(':')[0]), minutes=int(daily_work_hours.split(':')[1]))
    print(datetime_obj)

    # Create a base datetime object for today
    base_datetime = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    new_time_delta = datetime_obj * actual_workdays
    
    # Calculate total minutes (including days, if any)
    total_minutes = new_time_delta.days * 24 * 60 + new_time_delta.seconds // 60
    # Calculate new hour and minute
    new_hour, new_minute = divmod(total_minutes, 60)
    # Format the output as hours and minutes
    expected_hours = f"{new_hour:02d}:{new_minute:02d}"
        
    actual_hours_decimal = attendance_df['Total'].sum()
    hours = int(actual_hours_decimal)
    minutes = int((actual_hours_decimal - hours) * 60)
    actual_hours = f"{hours}:{minutes}"
    
    st.write("Expected work hours:  ", expected_hours)
    st.write("Actual work hours: ", actual_hours)
    
    st.subheader("Unexplained missing entries:")
    st.write(missing_workdays)
    
    if st.button('Show Raw Data'):
        st.session_state['show_json'] = not st.session_state['show_json']
        
    if st.session_state['show_json']:
        st.subheader("Attendance Query Data:")
        st.json(attendances)
        st.subheader("Absences Query Data:")
        st.json(absences)