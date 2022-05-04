###############
Getting Started
###############


Use DDM in Your Django Project
******************************

1. Install the necessary dependencies::

    pip install django-ckeditor pycryptodome django-ckeditor django-polymorphic django-webpack-loader

2. Add the necessary entries to INSTALLED_APPS in your settings.py::

    INSTALLED_APPS = [..., 'ddm', 'ckeditor', 'webpack_loader']

3. Add the following configuration for webpack-loader to your settings.py::

    WEBPACK_LOADER = {
        'DEFAULT': {
            'CACHE': True,
            'BUNDLE_DIR_NAME': 'ddm/vue/',
            'STATS_FILE': os.path.join(STATIC_ROOT, 'ddm/vue/webpack-stats.json'),
            'POLL_INTERVAL': 0.1,
            'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
        }
    }

4. Include the ddm URLconf in your projects urls.py::

    url(r'^ddm/', include('ddm.urls')),

5. Add time zone support mto your settings.py::

    USE_TZ = True

6. Run ``python manage.py migrate`` to create the ddm models in your database.
7. Test if everything works as expected and you are good to go!
