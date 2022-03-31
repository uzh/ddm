##############
For Developers
##############

This pages is addressed at developers contributing to the ddm package.

Development Guidelines
**********************

Local Project for Development and Testing
=========================================
The repository includes a django test project that can be used for local development and testing.

Setup
-----
| **1. Install required packages**
Activate your local virtual environment and install the following requirements (the requirements still need to be defined - files are currently empty)::

    (venv) SomePath/ddm> pip install -r requirements.txt
    (venv) SomePath/ddm> pip install -r test_project/requirements.txt

| **2. Test Project Configuration**

A basic standard configuration for the test project is specified in
*test_project/test_config.json*. Adjust the information in this file if you
want to use a custom setup or use another database. By default, the test project
uses SQLite as a database backend.

If you do make changes to this file, please do NOT commit these changes to the
shared repository.

Now you should be good to go.


Commands
--------
Through the setup described above, the regular django commands are now available:

**Run Development Server**

To start the development server use the following commands::

    (venv) SomePath/ddm> cd test_project
    (venv) SomePath/ddm/test_project> manage.py runserver

**Create Database Migrations**

To create new migrations based on the changes made to the models, run::

    (venv) SomePath/ddm/test_project> manage.py makemigrations

.. note:: this is only necessary, if you are actively developing, NOT if you are just checking out the project)


**Apply migrations**

To apply existing migrations to your local database, run:[1]_ ::

    (venv) SomePath/ddm/test_project> manage.py migrate

**Run Unit Tests**

To run unit tests, use::

    (venv) SomePath/ddm/test_project> manage.py test ddm

Vue Integration
===============

Development
-----------

To run the app in development mode, you will need to serve both Django’s dev server and the webpack development server. From the vue_frontend directory, run::

    npm run serve

And, in a separate terminal in the Django root directory, run the Django development server, e.g.::

    ./manage.py runserver

Point your browser to your Django app (e.g. http://localhost:8000) and check out the defined vue pages.

Production Deployment
---------------------

When it is time to deploy, or when you simply want to omit running the Vue dev server,
you can build the Vue project in production mode.
Cancel the ``npm run serve`` process if it is running and instead run ``npm run build``.
The optimized bundles will be built in and placed into the Django static file location,
and webpack-stats.json will be updated to reflect this new configuration.
The vue builds should end up in the static folder of the django module (ddm/static).


.. rubric:: Notes

.. [1] If you are running a version of Python < 3.9, you might have to manually enable the JSON1 extension on SQLite for the migration to work properly. For an explanation on how to do this visit https://code.djangoproject.com/wiki/JSON1Extension.

