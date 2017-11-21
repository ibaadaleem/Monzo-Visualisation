# Monzo-Visualisation
Monzo Visualisation Webapp

Built in Python 3.6

### Requirements
* Django
* Pandas
* Plotly
* Colour

### Setup Database
Navigate to the main directory containing "manage.py"

To create the database run

python manage.py migrate

To create tables run

python manage.py makemigrations visualisation

python manage.py sqlmigrate visualisation 0001

python manage.py migrate

### Running the application

python manage.py runserver

Then enter http://127.0.0.1:8000/ into your web browser!


### Other

Example upload can be found in main directory under "MonzoExampleData.csv"

Upload only takes csv files
