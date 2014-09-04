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
En este modulo se almacenan las vistas que gestionan los namespaces, tanto como
el listado, alta de nuevo namespaces, editar un namespace existente y la
eliminacion de los namespaces
"""

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages
from django.db import transaction
from django.utils.translation import ugettext as _

from easydata.models import NameSpace
from easydata.forms import NewNamespaceForm, EditNamespaceForm
from easydata.parsing.parserfactory import parser_factory
from easydata.decorators.decorators import easydata_super_member

import urllib2

__author__ = 'llerena'


@easydata_super_member
def listado_namespaces(request):
    """
    This view show all the namespaces loaded into the application
    :param request: the request of the view
    :return: render the view
    """

    #Obtengo la lista de paises existentes en la base de datos
    lista_names = NameSpace.objects.all()
    lista_names = lista_names.extra(select={'lower_name': 'lower(namespace)'})
    lista_names = lista_names.order_by('lower_name')
    #listaNames = listaNames.order_by('namespace')

    #Renderizo la plantilla con el listado de paises
    return render_to_response('easydata/namespace/list.html',
                              {'datos': lista_names, },
                              context_instance=RequestContext(request))


@easydata_super_member
@transaction.commit_on_success
def vista_carga_namespace(request):
    """
    This view shows a form to load a new namespace into the application.
    :param request: the request of the view
    :return: render the form
    """

    #Si hay datos en el POST, valido el formulario y creo el nuevo namespace
    if request.POST:
        form = NewNamespaceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            try:
                if form.cleaned_data["url"] != '':
                    fich = form.cleaned_data["url"]
                else:
                    fich = form.cleaned_data["archivo"]

                parser = parser_factory(fich, form.cleaned_data["formato"],
                                        form.instance)

                parser.parse()
                parser.register()

                mensaje1 = _("The namespace was created successfully.")
                mensaje2 = _("The namespace has ")
                mensaje2 += str(form.instance.entidades.all().count())
                mensaje2 += _(" entities and ")
                mensaje2 += str(form.instance.propiedades.all().count())
                mensaje2 += _(" properties")

                messages.info(request, mensaje1)
                messages.info(request, mensaje2)

                return redirect('easydata.views.namespace.listado_namespaces')
            except Exception:
                form.instance.delete()
                messages.info(request, _("There was an error, and the \
namespace couldn't be created"))
        else:
            messages.info(request, _("There are errors in the form, please \
check it and send the form to create the namespace"))
    else:
        form = NewNamespaceForm()

    #Renderizo la plantilla con el formulario
    return render_to_response('easydata/namespace/new.html',
                              {'form': form, },
                              context_instance=RequestContext(request))


@easydata_super_member
def editar_namespace(request, id):
    """
    This view shows a form to edit the info of a namespace, and reload the
    entities and properties
    :param request: the request of the view
    :param id: the primary key of the namespace
    :return: render the form
    """
    try:
        name = NameSpace.objects.get(id=id)
    except Exception:
        return redirect('easydata.views.namespace.listado_namespaces')

    #Obtengo la lista de paises existentes en la base de datos
    if request.POST:
        form = EditNamespaceForm(request.POST, request.FILES, instance=name)

        if form.is_valid():
            form.save()
            try:
                fich = None
                if form.cleaned_data["url"] != '':
                    fich = form.cleaned_data["url"]
                elif form.cleaned_data["archivo"]:
                    fich = form.cleaned_data["archivo"]

                if not fich is None:
                    parser = parser_factory(fich, form.cleaned_data["formato"],
                                            form.instance)

                    parser.parse()
                    parser.update()

                mensaje1 = _("The namespace was updated successfully.")
                mensaje2 = _("The namespace has ")
                mensaje2 += str(form.instance.entidades.all().count())
                mensaje2 += _(" entities and ")
                mensaje2 += str(form.instance.propiedades.all().count())
                mensaje2 += _(" properties")

                messages.info(request, mensaje1)
                messages.info(request, mensaje2)
                return redirect('easydata.views.namespace.listado_namespaces')
            except Exception:
                messages.info(request, _("There was an error, and the \
namespace couldn't be updated"))
        else:
            messages.info(request, _("There are errors in the form, please \
check it and send the form to update the namespace"))

    else:
        form = EditNamespaceForm(instance=name)

    #Renderizo la plantilla con el formulario
    return render_to_response('easydata/namespace/edit.html',
                              {'form': form, },
                              context_instance=RequestContext(request))


@easydata_super_member
def eliminar_namespace(request, id):
    """
    This view delete a concreta namespace, and all the entities and properties,
    and the relations between the models and fields
    :param request: the request of the view
    :param id: the primary key of the namespace
    :return: None
    """
    try:
        name = NameSpace.objects.get(id=id)
    except Exception:
        return redirect('easydata.views.namespace.listado_namespaces')

    # Obtengo todas las entidades y propiedades del
    # namespace para eliminarlas tambien
    entities = name.entidades.all()
    props = name.propiedades.all()

    #Elimino todo
    props.delete()
    entities.delete()
    name.delete()

    #Create the message
    messages.info(request, _('The namespace was deleted'))

    #Redirijo al listado de namespaces
    return redirect('easydata.views.namespace.listado_namespaces')
