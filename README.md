django-easydata
===============

EasyData is an app to publish your Django model's data using the available ontologies, with a graphical interface to configure.

Quick start
-----------

  1. Add "easydata" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
    ...
      'easydata',
    )

  2. Include the easydata urls in your project urls.py like this::

    url(r'^easydata/', include('easydata.urls')),

  3. Run 'python manage.py syncdb' to create the easydata models.

  4. Run the script 'python manage.py loadmodels' to resolve the models and fields of your project.

  5. Run your test server and visit http://127.0.0.1:8000/easydata/ to access to the application.
