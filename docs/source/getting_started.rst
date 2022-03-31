###############
Getting Started
###############


Use DDM in Your Django Project
******************************

1. Add "ddm" to INSTALLED_APPS in your settings.py::

    INSTALLED_APPS = [..., 'ddm',]

2. Install ``django-ckeditor`` ::

    pip install

3. Add "ckeditor" to INSTALLED_APPS in your settings.py::

    INSTALLED_APPS = [..., 'ddm', 'ckeditor'].

3. Include the ddm URLconf in your projects urls.py::

    url(r'^ddm/', include('ddm.urls')),

4. Add time zone support mto your settings.py::

    USE_TZ = True

5. Run ``python manage.py migrate`` to create the ddm models in your database.
6. Test if everything works as expected and you are good to go!
