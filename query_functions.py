import requests


def authenticate():
    # TODO: put keys in .env file!!

    url = "https://api.personio.de/v1/auth"
    payload = {
        "client_id": "papi-9cecb510-8b07-44f6-b3ca-02dabe0615ae",
        "client_secret": "papi-NGYwMjc2MGMtODBjYi00N2EyLThmNzItN2VhNGZjNDkzOTRh",
    }

    response = requests.post(url, json=payload)
    response_data = response.json()

    if response.status_code == 200:
        auth_token = (
            response_data["data"]["token"]
            if "data" in response_data and "token" in response_data["data"]
            else None
        )
        if auth_token:
            print("Auth token:", auth_token)
        else:
            print("Token not found in the response.")
    else:
        print("Failed to authenticate:", response.text)
    return auth_token


def get_employees(auth_token):
    url = "https://api.personio.de/v1/company/employees"
    headers = {
        "Authorization": "Bearer " + auth_token  # Replace with your actual auth token
    }

    response = requests.get(url, headers=headers)
    response_data = response.json()

    if response.status_code == 200:
        print("Success")  # Prints the JSON response
    else:
        print("Error:", response.status_code, response.text)

    # For now we're only interested in the full names and ids of active employees. Lets create two lists:
    names = []
    ids = []

    if response_data.get("success") and "data" in response_data:
        for employee in response_data["data"]:
            # Check if the employee status is active
            if employee["attributes"]["status"]["value"] == "active":
                # Concatenate first name and last name
                name = (
                    employee["attributes"]["first_name"]["value"]
                    + " "
                    + employee["attributes"]["last_name"]["value"]
                )
                names.append(name)

                # Get the ID
                id = employee["attributes"]["id"]["value"]
                ids.append(id)

    # print("Names:", names)
    # print("IDs:", ids)
    return names, ids


def get_attendances(auth_token, id, selected_range):
    url = "https://api.personio.de/v1/company/attendances"
    headers = {
        "Authorization": "Bearer " + auth_token,  # Replace with your actual auth token
        "accept": "application/json"
    }
    params = {
        # "start_date": "2023-11-01",
        # "end_date": "2023-11-30",
        "start_date": selected_range[0],
        "end_date": selected_range[1],
        "employees": [id],
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        attendances = response.json()["data"]
        # print(attendances)
    else:
        print("Error:", response.status_code, response.text)
    return attendances


def get_single_employee_details(auth_token, employee_id):
    url = f"https://api.personio.de/v1/company/employees/{employee_id}"
    headers = {
        "Authorization": "Bearer " + auth_token  # Replace with your actual auth token
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)


def get_absences(auth_token, employee_id, selected_range):
    url = f"https://api.personio.de/v1/company/time-offs?start_date={selected_range[0]}&end_date={selected_range[1]}&employees[]={employee_id}"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + auth_token  # Replace with your actual auth token
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        absences = response.json()["data"]
        return absences
    else:
        print("Error:", response.status_code, response.text)
