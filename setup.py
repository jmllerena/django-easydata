import os
from setuptools import setup
from setuptools import find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-easydata',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='GNU License',
    description='A Django app to publish your project data using ontologies.',
    long_description=README,
    author='Jose Manuel Llerena',
    author_email='jose.llerecarmo@alum.uca.es',
    keywords = ['ontology', 'rdf', 'rdfa', 'semantic web', 'django', 'microdata'],
    package_dir={'easydata': 'easydata'},
    package_data={'easydata': ['templates/*.html',
                               'templates/easydata/*.html',
                               'templates/easydata/informacion/*.html',
                               'templates/easydata/map/*.html',
                               'templates/easydata/modelo/*.html',
                               'templates/easydata/namespace/*.html',
                               'templates/easydata/templatetags/*.html',
                               'static/easydata/css/*.css',
                               'static/easydata/img/*.png',
                               'static/easydata/img/ui-theme/*.png',
                               'static/easydata/img/ui-theme/*.gif',
                               'static/easydata/js/*.js',
                               ]
    },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        "Django >= 1.4",
        "rdflib == 4.0.1",
        "pydot",
    ],
)
