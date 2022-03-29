# Data Donation Module (ddm)
Currently under development.

## Install DDM in Your own Project

1. Add "ddm" to your INSTALLED_APPS setting: `INSTALLED_APPS = [..., 'ddm',]`
2. Add "ckeditor" to your INSTALLED_APPS setting: `INSTALLED_APPS = [..., 'ddm', 'ckeditor']`. You might have to install `django-ckeditor` for this to work.
3. Include the ddm URLconf in your projects urls.py: `url(r'^ddm/', include('ddm.urls')),`.
4. Run `python manage.py migrate` to create the ddm models.


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
In this new file, you can optionally replace the placeholders with your local credentials.[^1]
3. Now you should be good to go.


### Commands
Through this setup, the regular django commands are now available:

**Run Development Server**

To start the development server use the following command:
```
(venv) SomePath/ddm> cd test_project
(venv) SomePath/ddm/test_project> manage.py runserver
```
**Create Database Migrations**

To create new migrations based on the changes made to the models, run: *(note that this is only necessary, if you are actively developing, NOT if you are just checking out the project)*
```
(venv) SomePath/ddm/test_project> manage.py makemigrations
```

**Apply migrations**

To apply existing migrations to your local database, run:[^2]
```
(venv) SomePath/ddm/test_project> manage.py migrate
```
**Run Unit Tests**

To run unit tests, use:
```
(venv) SomePath/ddm/test_project> manage.py test ddm
```


## Requirements

### Django Settings

#### Time zone
For ddm to work, time zone support must be enabled in the Django settings: 
`USE_TZ = True`

[^1]: By default, the test project uses SQLite as a database backend. 

[^2]: If you are running a version of Python < 3.9, you might have to manually 
enable the JSON1 extension on SQLite for the migration to work properly. For an 
explanation on how to do this visit https://code.djangoproject.com/wiki/JSON1Extension.

## Vue development
To run our app in development mode, we’ll need to serve both Django’s dev server and the webpack development server. From the vue_frontend directory, run:
```
npm run serve
```
And, in a separate terminal in the Django root directory, run the Django development server, e.g.
```
./manage.py runserver
```
Point your browser to your Django app (e.g. http://localhost:8000) and check out the defined vue pages.

### Vue production deployment
When it’s time to deploy, or when we simply want to omit running our Vue dev server, we can build our Vue project in production mode. Cancel the `npm run serve` process if it's running and instead run `npm run build`. 
The optimized bundles will be built in and placed into our Django static file location, and webpack-stats.json will be updated to reflect this new configuration. The vue builds should end up in the static folder of the django module (ddm/static).