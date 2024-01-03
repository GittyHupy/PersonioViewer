# Personio API Access via Python

Access attendances and absences of employees and display results in a streamlit app.


### Why not use the personio-py library?
In principle easier to use, but does not deliver all necessary information (in particular the Project name associated with attendance times is not retrieved).
Since we only need a few GET requests, using the requests library is totally sufficient.