# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
#    EasyData/Django: an app to publish your django projects data using
#                     vocabularies.
#    Copyright (C) 2013  Jose Manuel Llerena Carmona
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

"""
Este modulo almacena las vistas tanto de bienvenida, como las vistas donde se
ofrece ayuda a los usuarios, indicandoles ejemplos de uso de la aplicacion
tanto para urls y plantillas
"""

from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from django.template import RequestContext
from django.contrib.auth import logout
from django.conf import settings
from django.utils.html import escape
from django.utils.translation import ugettext as _

from easydata.models import Modelo, Atributo, Relacion, Entidad
from easydata.templatetags.easydata_rdfa import generate_html_rdfa
from easydata.templatetags.easydata_microdata import generate_html_microdata
from easydata.decorators.decorators import easydata_super_member


from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login


__author__ = 'llerena'


def welcome(request):
    """
    This view render the welcome view
    """
    #Renderizo la plantilla
    return render_to_response('easydata/information/welcome.html', {},
                              context_instance=RequestContext(request))


@easydata_super_member
def info_models(request):
    """
    This view render a template with information about the models of the
    project
    """
    listado = list()

    modelos = Modelo.objects.all()
    modelos = modelos.filter(visibilidad='V')
    modelos = modelos.exclude(entidad=None)

    example_model = None
    elem = None
    url = None

    for mod in modelos:
        # Get the models
        registro = dict()
        registro['modelo'] = mod

        # Get all the attributes
        atributos = Atributo.objects.all()
        atributos = atributos.filter(visibilidad='V')
        atributos = atributos.filter(modelo=mod)
        atributos = atributos.exclude(propiedad=None)
        registro['atributos'] = atributos.count()

        # Get all the relations
        relaciones = Relacion.objects.all()
        relaciones = relaciones.filter(visibilidad='V')
        relaciones = relaciones.filter(modelo=mod)
        relaciones = relaciones.exclude(propiedad=None)
        registro['relaciones'] = relaciones.count()

        listado.append(registro)

        # Get an example
        if elem is None:
            mod_class = mod.devolver_modelo()

            query = mod_class._default_manager.all()

            if example_model is None and query.count() != 0:
                elem = query[0]
                example_model = mod
                url = example_model.generate_url(elem, True)

    return render_to_response('easydata/information/modelos.html',
                              {'modelos': listado,
                               'example_model': example_model,
                               'elem': elem,
                               'url': url, },
                              context_instance=RequestContext(request))


@easydata_super_member
def info_entities(request):
    """
    This view render a template with information about the entities loaded in
    the application
    """
    example_entity = None

    entidades = Entidad.objects.all()
    entidades = entidades.exclude(modelos=None)
    entidades = entidades.filter(modelos__visibilidad='V')
    entidades = entidades.distinct()

    if entidades.count() != 0:
        example_entity = entidades[0]

    return render_to_response('easydata/information/entidades.html',
                              {'entidades': entidades,
                               'example_entity': example_entity, },
                              context_instance=RequestContext(request))


@easydata_super_member
def info_templatetags(request):
    """
    This view render a template with information about the template tags
    availables in the application
    """

    field = None
    example_model = None

    modelos = Modelo.objects.all()
    modelos = modelos.filter(visibilidad='V')
    modelos = modelos.exclude(entidad=None)

    for mod in modelos:
        fields = mod.fields.all()
        fields = fields.filter(visibilidad='V')
        fields = fields.exclude(propiedad=None)

        if fields.count() != 0:
            field = fields[0]
            example_model = mod
            break

    apps_dirs = list()

    # Generate the code examples
    rdfa_code = None
    microdata_code = None
    instancia = None

    if not example_model is None:
        model_class = example_model.devolver_modelo()

        if model_class._default_manager.all().count() != 0:
            instancia = model_class._default_manager.all()[0]

        if instancia:
            rdfa_code = generate_html_rdfa(instancia, "div", "div",
                                           True, None)
            rdfa_code = escape(rdfa_code)
            microdata_code = generate_html_microdata(instancia, "div",
                                                     "div", True, None)
            microdata_code = escape(microdata_code)

    for app in settings.INSTALLED_APPS:
        try:
            module = __import__(app)
            if not module.__path__[0] in apps_dirs:
                apps_dirs.append(module.__path__[0])
        except ImportError:
            pass

    return render_to_response('easydata/information/templates.html',
                              {'example_model': example_model,
                               'field': field,
                               'list_dirs': settings.TEMPLATE_DIRS,
                               'apps_dirs': apps_dirs,
                               'rdfa_code': rdfa_code,
                               'microdata_code': microdata_code, },
                              context_instance=RequestContext(request))


def disconnect(request):
    """
    Esta vista se encarga de cerrar la sesion
    """
    if request.user.is_authenticated():
        # Logout the user
        logout(request)

        # Create logout message
        messages.info(request, _('You have been logged out'))
    else:
        # Create logout message
        messages.info(request, _("You aren't logged in"))

    # Redirect to the welcome view
    return redirect('easydata.views.information.welcome')


def login(request):
    """
    Esta vista se encarga de iniciar la sesion
    """
    if request.POST:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return redirect('easydata.views.information.welcome')
    else:
        form = AuthenticationForm(request)

    request.session.set_test_cookie()

    return render_to_response('easydata/information/login.html',
                              {'form': form, },
                              context_instance=RequestContext(request))
