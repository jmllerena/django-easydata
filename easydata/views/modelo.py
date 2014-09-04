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
En este modulo se almacena las vistas que se encargan de realizar la
configuracion de la visibilidad de los modelos y fields
"""

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.db import transaction
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext as _

from easydata.models import Modelo, Field
from easydata.forms import VisibilityModelsForm, VisibilityFieldForm
from easydata.decorators.decorators import easydata_super_member

__author__ = 'llerena'


@easydata_super_member
@transaction.commit_on_success
def configure_visibility_models(request, aplicacion):
    """
    Esta vista se encarga de realizar la configuración de visibilidad de los
    modelos y fields de los mismos
    """

    modelos = Modelo.objects.all()
    modelos = modelos.filter(aplicacion=aplicacion)

    modelo_formset = modelformset_factory(Modelo, form=VisibilityModelsForm,
                                          extra=0)
    field_formset = modelformset_factory(Field, form=VisibilityFieldForm,
                                         extra=0)

    if request.POST:
        valido = True
        formset_modelos = modelo_formset(
                          request.POST,
                          queryset=modelos.order_by('aplicacion', 'nombre'),
                          prefix="models")
        listado = list()
        for form in formset_modelos:
            diccionario = dict()

            diccionario['form_modelo'] = form

            fields = Field.objects.all()
            fields = fields.filter(modelo=form.instance)
            fields = fields.order_by('nombre')

            formset_fields = field_formset(request.POST, queryset=fields,
                                           prefix=(form.instance.nombre +
                                                   form.instance.aplicacion))
            diccionario['form_field'] = formset_fields

            listado.append(diccionario)

        for elem in listado:
            if not elem['form_modelo'].is_valid() or \
               not elem['form_field'].is_valid():
                valido = False

        if valido:
            for elem in listado:
                elem['form_modelo'].save()
                elem['form_field'].save()

            messages.info(request, _('The changes were saved'))
        else:
            messages.info(request, _('There were errors on the form'))
    else:
        formset_modelos = modelo_formset(
                          queryset=modelos.order_by('aplicacion', 'nombre'),
                          prefix="models")
        listado = list()
        for form in formset_modelos:
            diccionario = dict()

            diccionario['form_modelo'] = form

            fields = Field.objects.all()
            fields = fields.filter(modelo=form.instance)
            fields = fields.order_by('nombre')

            formset_fields = field_formset(queryset=fields,
                                           prefix=(form.instance.nombre +
                                                   form.instance.aplicacion))
            diccionario['form_field'] = formset_fields

            listado.append(diccionario)

    vacio = len(listado) == 0

    return render_to_response('easydata/modelo/visibility.html',
                              {'listado': listado,
                               'management': formset_modelos.management_form,
                               'vacio': vacio},
                              context_instance=RequestContext(request))


@easydata_super_member
@transaction.commit_on_success
def select_visibility_app(request):
    """
    Esta vista se encarga de realizar la configuración de visibilidad de los
    modelos y fields de los mismos
    """

    modelos = Modelo.objects.all()
    modelos = modelos.order_by('aplicacion')

    aplicaciones = dict()

    for modelo in modelos:
        try:
            aplicaciones[modelo.aplicacion] += 1
        except KeyError:
            aplicaciones[modelo.aplicacion] = 1

    return render_to_response('easydata/modelo/select_app.html',
                              {'apps': sorted(aplicaciones.items()), },
                              context_instance=RequestContext(request))
