# COMP440 Project

**For group 51**: Melissa Little, Gerard Gandionco, Gisela Calva

### Phase 1

[Video link](https://youtu.be/Ngrj8D0G6ng)

### Phase 2

[Video Link](https://youtu.be/oVpZJD6aZtY)

### Phase 3

TO BE DEMOED WITH GRADER

#### Contributions
Everyone contributed adequately to the project on both front and back ends.

**Melissa**
Helped connect server code to the frontend pages with Flask's jinja2 templating system. Helped with the SQL queries. Demonstrated the project workings in the video recording.

**Gerard**
Primarily worked with the URL endpoints with Flask views as well as created sessions for keeping the user logged in and able to create listings/reviews. Helped with the SQL queries.


**Gisela**
Helped connect the database to the server backend with mySQL connector executions. Helped with the SQL queries. Ensured things were working well with end-user testing.

#### How to install and run
1) Have the latest version of [Python](https://www.python.org/) installed in your system. Then `pip install -U Flask` to install [Flask](https://flask.palletsprojects.com/en/3.0.x/), a micro webframework. Preferrably you do this in an isolated environment e.g. [virtual environments](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/).

2) Have mySQL installed in your system. Create a connection, head inside, and run the `phase2_schema.sql` found in his source code's repository to initialize the database and its starting tables. The users table must be present in order for you to register for a user account.

3) By default, the code inside `views.py` assumes that you are connected via localhost as the root user, with no password, and that the database's name is "comp440_project." Feel free to match them up however you want such as changing the connection details on line 13.

4) In the project directory on the command line, where `views.py` is at, enter `flask --app views run`. The server should now be running and you should be given the URL to the localhost page. It should say `* Running on http://127.0.0.1:5000` or some variant.

5) The web application is now yours to explore.