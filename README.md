# Data Donation Module (ddm)
Currently under development.

## Development Guidelines
### Local Project for Development and Testing
The repository includes a django test project that can be used for local development and testing.

### Setup

1. **Install required packages** \
Activate your local virtual environment and install the following requirements
(the requirements still need to be defined - files are currently empty):
```
(venv) SomePath/ddm> pip install -r requirements.txt
(venv) SomePath/ddm> pip install -r test_project/requirements.txt
```
2. To setup the django project, first make a copy of *test_project/test_config.json.example* and rename it to *test_project/test_config.json*. \
In this new file, replace the placeholders with your local credentials.[^1]
3. Now you should be good to go.


### Commands
Through this setup, the regular django commands are now available:

- **Run Development Server** \
To start the development server use the following command:
```
(venv) SomePath/ddm> cd test_project
(venv) SomePath/ddm/test_project> manage.py runserver
```
- **Create Database Migrations** \
To create new migrations based on the changes made to the models, run: *(note that this is only necessary, if you are actively developing, NOT if you are just checking out the project)*
```
(venv) SomePath/ddm/test_project> manage.py makemigrations
```

- **Apply migrations** \
To apply existing migrations to your local database, run:
```
(venv) SomePath/ddm/test_project> manage.py migrate
```
- **Run Unit Tests** \
To run unit tests, use:
```
(venv) SomePath/ddm/test_project> manage.py test
```


## Requirements

### Django Settings

#### Time zone
For ddm to work, time zone support must be enabled in the Django settings: 
`USE_TZ = True`


[^1]: For an overview on how to setup a local database for Django, see (the tutorial on digital ocean) [https://www.digitalocean.com/community/tutorials/how-to-create-a-django-app-and-connect-it-to-a-database#step-1-%E2%80%94-creating-the-database].
