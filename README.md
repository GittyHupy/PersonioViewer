# Personio API Access via Python

Access attendances and absences of employees and display results in a streamlit app.

## Usage

### Installation

Optionally create a virtual python environment:  `python -m venv venv` and activate it.

Install the requirements `pip install -r requirements.txt`

Start the venv `.\venv\Scripts\Activate.ps1 
Launch the app `streamlit run app.py` (a browser window should pop up)

### API Access

Enter your Personio API keys in .envEXAMPLE and rename the file to .env




### Sidenote: Why not use the personio-py library?
In principle easier to use, but does not deliver all necessary information (in particular the Project name associated with attendance times is not retrieved).
Since we only need a few GET requests, using the requests library is totally sufficient.