import pandas as pd
from datetime import datetime, timedelta
from workalendar.europe import Switzerland


def create_attendance_df(attendances):
    # Check if the attendances list is empty
    if not attendances:
        # Define the columns
        columns = ["Date", "Project", "AttendanceTime"]
        # Create an empty DataFrame with these columns
        df_summary = pd.DataFrame(columns=columns)
    else:
        # Your existing code to process the attendances and create the DataFrame
        data = []
        for record in attendances:
            project_info = record["attributes"]["project"]
            project_name = (
                "Sonstiges"
                if project_info is None
                else project_info["attributes"]["name"]
            )
            date = record["attributes"]["date"]
            start_time = datetime.strptime(record["attributes"]["start_time"], "%H:%M")
            end_time = datetime.strptime(record["attributes"]["end_time"], "%H:%M")
            attendance_time = (
                end_time - start_time
            ).total_seconds() / 3600  # Convert to hours

            data.append(
                {
                    "Date": date,
                    "Project": project_name,
                    "AttendanceTime": attendance_time,
                }
            )

        df = pd.DataFrame(data)
        df_summary = df.pivot_table(
            index="Date",
            columns="Project",
            values="AttendanceTime",
            aggfunc="sum",
            fill_value=0,
        )
        
        # Convert index to date objects
        df_summary.index = pd.to_datetime(df_summary.index).date
        
        df_summary["Total"] = df_summary.sum(axis=1)

    return df_summary


def create_absence_df(absences):
    # Check if the absences list is empty
    if not absences:
        # Define the columns
        columns = ['Date', 'Abwesenheitsgrund']
        # Create an empty DataFrame with these columns
        df = pd.DataFrame(columns=columns)
    else:
        # Existing code to process the absences
        data = []
        for record in absences:
            timeoff_type = record["attributes"]["time_off_type"]["attributes"]["name"]
            start_date = datetime.fromisoformat(record["attributes"]["start_date"]).date()  # Only use the date part
            end_date = datetime.fromisoformat(record["attributes"]["end_date"]).date()  # Only use the date part

            # Calculate the number of days
            delta = (end_date - start_date).days + 1

            # Create a row for each day
            for i in range(delta):
                current_date = (start_date + timedelta(days=i))
                data.append({"Date": current_date, "Abwesenheitsgrund": timeoff_type})

        df = pd.DataFrame(data)
        # Set 'Date' as the index
        df = df.set_index('Date')

    return df


def get_workdays(start_date, end_date):
    cal = Switzerland()
    workdays = []

    current_date = start_date
    while current_date <= end_date:
        if cal.is_working_day(current_date):
            workdays.append(current_date)
        current_date += timedelta(days=1)

    return workdays