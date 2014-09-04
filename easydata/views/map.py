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
En este modulo se almacenan las vistas que estan relacionadas con el mapeo de
los modelos y de los fields. Ademas tambien almacena aquellas vistas que estan
relacionadas con el mapeo, como son las de generacion de graficos y de fichero
de configuracion D2Rq
"""

from django.utils import simplejson
from django.db import transaction
from django.forms.models import modelformset_factory
from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.translation import ugettext as _

from pydot import InvocationException, graph_from_dot_data
from rdflib import Graph, Literal

from easydata.forms import ModeloEntidadForm, FieldPropiedadForm, D2RqForm
from easydata.models import NameSpace, Modelo, Propiedad, Atributo
from easydata.models import Relacion, Field
from easydata.utils import descubre_propiedades, descubre_padres
from easydata.decorators.decorators import easydata_super_member

__author__ = 'llerena'


@easydata_super_member
@transaction.commit_on_success
def mapea_modelo(request):
    """
    This views is used to map the existing models, with the entities of the
    namespaces
    """
    modelo_formset = modelformset_factory(Modelo,
                                          form=ModeloEntidadForm,
                                          extra=0)
    mods = Modelo.objects.all()
    mods = mods.order_by('aplicacion', 'nombre')

    # If exists a POST on the request
    if request.POST:
        formset_modent = modelo_formset(request.POST, queryset=mods)

        # If the form validates
        if formset_modent.is_valid():
            for form in formset_modent:
                #Get the instance of the model to compare the entities
                mod = Modelo.objects.get(pk=form.instance.id)

                #Check if the entity has changed, to delete
                #his field's relations
                if mod.entidad != form.instance.entidad:
                    form.save()

                    fields = form.instance.fields.all()

                    for field in fields:
                        field.propiedad = None
                        field.save()

                    relations = Relacion.objects.all()
                    relations = relations.filter(
                                modelo_relacionado=form.instance)
                    relations = relations.exclude(propiedad=None)

                    for rel in relations:
                        rel.propiedad = None
                        rel.save()
            messages.info(request, _('The changes were saved'))
        else:
            messages.info(request, _('There were errors on the form'))
    else:
        formset_modent = modelo_formset(queryset=mods)

    registro = dict()

    for form in formset_modent:
        try:
            registro[form.instance.aplicacion].append(form)
        except KeyError:
            registro[form.instance.aplicacion] = list()
            registro[form.instance.aplicacion].append(form)

    vacio = False
    if len(registro) == 0:
        vacio = True

    #Renderizo la plantilla con el formulario
    return render_to_response('easydata/map/mapeaModelo.html',
                              {'management': formset_modent.management_form,
                               'registro_forms': sorted(registro.items()),
                               'vacio': vacio, },
                              context_instance=RequestContext(request))


@easydata_super_member
def devuelve_entidades(request):
    """
    Used with ajax, return a list of entities of a given namespace
    """
    resultado = dict()

    #Si existen datos en request.GET
    if request.method == u'GET':
        get_data = request.GET
        if u'namespace' in get_data:  # Capta el dato namespace
            name = get_data[u'namespace']

            #capta la instancia de NameSpace
            namespace_instance = NameSpace.objects.get(pk=name)

            #Capta las instancias de Schemas del NameSpace
            entities = namespace_instance.entidades.all()
            entities = entities.order_by('nombre')

            resultado['return'] = True
            resultado['lista'] = list()

            #Create a list with the entities
            for ent in entities:
                if ent.descripcion is None or ent.descripcion == '':
                    subregistro = (unicode(ent.id),
                                   unicode(ent.nombre),
                                   unicode(ent.etiqueta) + u': ' +
                                   u'Without description')
                else:
                    subregistro = (unicode(ent.id),
                                   unicode(ent.nombre),
                                   unicode(ent.etiqueta) + u': ' +
                                   unicode(ent.descripcion))
                resultado['lista'].append(subregistro)

    #Return using json the list of entities
    json = simplejson.dumps(resultado)
    return HttpResponse(json, mimetype='application/json')


@easydata_super_member
def devuelve_propiedades_namespace(request):
    """
    Used with ajax, return a list of properties of a given namespace
    """
    resultado = dict()

    #Si existen datos en request.GET
    if request.method == u'GET':
        get_data = request.GET
        if u'namespace' in get_data:  # Capta el dato namespace
            name = get_data[u'namespace']

            #capta la instancia de NameSpace
            namespace_instance = NameSpace.objects.get(pk=name)

            #Get the properties instances
            properties = namespace_instance.propiedades.all()

            resultado['return'] = True
            resultado['lista'] = list()

            properties = properties.order_by('nombre')

            #Add the properties to the list
            for prop in properties:
                # Check if have or not description
                if prop.descripcion is None or prop.descripcion == '':
                    subregistro = (unicode(prop.id),
                                   unicode(prop),
                                   unicode(prop.etiqueta) + u': ' +
                                   u'Without description')
                else:
                    subregistro = (unicode(prop.id),
                                   unicode(prop),
                                   prop.etiqueta + ': ' +
                                   prop.descripcion)
                resultado['lista'].append(subregistro)

    #Return using json the list with the properties
    json = simplejson.dumps(resultado)
    return HttpResponse(json, mimetype='application/json')


@easydata_super_member
def devuelve_propiedades_default(request):
    """
    Used with ajax, return the list of properties for a concrete field
    """
    resultado = dict()

    # If exist data in request.GET
    if request.method == u'GET':
        get_data = request.GET
        if u'field' in get_data:  # Get the field
            field = get_data[u'field']

            # Check if is a attribute or a relation
            if Atributo.objects.filter(pk=field).count() > 0:
                field = Atributo.objects.get(pk=field)
                queryset = descubre_propiedades(field.modelo.entidad)
            else:
                field = Relacion.objects.get(pk=field)

                queryset = descubre_propiedades(field.modelo.entidad, False)

                padres = descubre_padres(field.modelo_relacionado.entidad)
                padres.add(field.modelo_relacionado.entidad)
                queryset = queryset.filter(tipo__in=padres)

                if queryset.count() == 0:
                    queryset = Propiedad.objects.none()

            #Create a list with the properties availables
            resultado['return'] = True
            resultado['lista'] = list()

            queryset = queryset.order_by('nombre')

            for elem in queryset:
                # check if has description
                if elem.descripcion is None or elem.descripcion == '':
                    subregistro = (str(elem.id),
                                   unicode(elem),
                                   elem.etiqueta + ': ' +
                                   'Without description')
                else:
                    subregistro = (str(elem.id),
                                   unicode(elem),
                                   elem.etiqueta + ': ' +
                                   elem.descripcion)
                resultado['lista'].append(subregistro)

    # Return the list of properties using json
    json = simplejson.dumps(resultado)
    return HttpResponse(json, mimetype='application/json')


@easydata_super_member
def mapea_fields(request, id):
    """
    This view is used to map the fields of a concrete model, with the
    properties of the namespaces loaded into the application
    """
    try:
        mod_instance = Modelo.objects.get(pk=id)
    except Modelo.DoesNotExist:
        messages.info(request, _("The Model doesn't exists."))
        return redirect('easydata.views.map.mapea_modelo')

    if mod_instance.entidad is None:
        messages.info(request, _("The Model is not mapped."))
        return redirect('easydata.views.map.mapea_modelo')

    #Get all the attribute fields
    atributos = Atributo.objects.all()
    atributos = atributos.filter(modelo=mod_instance)
    atributos = atributos.order_by('nombre')

    #Get the relation fields that have a possible propertie to select and the
    #the model that makes reference are mapped
    relaciones = Relacion.objects.all()
    relaciones = relaciones.filter(modelo=mod_instance)
    relaciones = relaciones.exclude(modelo_relacionado__entidad=None)
    relaciones = relaciones.order_by('nombre')
    relaciones = relaciones.distinct()

    #Create the factory model formset
    propiedad_formset = modelformset_factory(Field,
                                             form=FieldPropiedadForm, extra=0)

    # If exist data on request.POST
    if request.POST:
        # Create the forms with the POST data
        form_atributos = propiedad_formset(request.POST,
                                           queryset=atributos,
                                           prefix="atri")
        form_relaciones = propiedad_formset(request.POST,
                                            queryset=relaciones,
                                            prefix="rel")

        if form_atributos.is_valid() and form_relaciones.is_valid():
            form_atributos.save()
            form_relaciones.save()

            messages.info(request, _("The fields were mapped successfully"))
        else:
            messages.info(request, _("There were errors on the form"))

    else:
        form_atributos = propiedad_formset(queryset=atributos, prefix="atri")
        form_relaciones = propiedad_formset(queryset=relaciones, prefix="rel")

    #Renderizo la plantilla con el formulario
    return render_to_response('easydata/map/mapeaFields.html',
                              {'formulario_atributos': form_atributos,
                               'formulario_relaciones': form_relaciones,
                               'mod': mod_instance, },
                              context_instance=RequestContext(request))


@easydata_super_member
def create_configuration_graph(request):
    """
    This view is used to create a graphviz graph with the models's
    configuration
    """

    fichero = u"""
digraph name {
  fontname = "Helvetica"
  fontsize = 8

  node [
    fontname = "Helvetica"
    fontsize = 8
    shape = "plaintext"
  ]
  edge [
    fontname = "Helvetica"
    fontsize = 8
  ]
  """

    model_var_open = u"""
    %s [label=<
    <TABLE BGCOLOR="palegoldenrod" BORDER="0" CELLBORDER="0" CELLSPACING="0">
     <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="olivedrab4"
     ><FONT FACE="Helvetica Bold" COLOR="white"
     >%s</FONT></TD></TR>
    """

    model_var_close = u"""
    </TABLE>
    >]"""

    atributo_var = u"""
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT FACE="Helvetica Bold">%s</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT FACE="Helvetica Bold">%s</FONT
        ></TD></TR>
    """

    atributo_var_privado = u"""
        <TR><TD ALIGN="LEFT" BORDER="0"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">%s</FONT
        ></TD>
        <TD ALIGN="LEFT"
        ><FONT COLOR="#7B7B7B" FACE="Helvetica Bold">%s</FONT
        ></TD></TR>
    """

    relacion_var = u"""
    %s -> %s
    [label="%s"] [arrowhead=normal, arrowtail=dot];
    """

    modelos = Modelo.objects.all()
    modelos = modelos.exclude(entidad=None)

    for modelo in modelos:
        fichero += model_var_open % (modelo.aplicacion + '_' + modelo.nombre,
                                     modelo.nombre + ' (' +
                                     modelo.entidad.nombre + ' - ' +
                                     modelo.entidad.namespace.namespace + ')')

        atributos = Atributo.objects.all()
        atributos = atributos.filter(modelo=modelo)
        atributos = atributos.exclude(propiedad=None)

        for atributo in atributos:
            if atributo.visibilidad == 'V':
                fichero += atributo_var % (atributo.nombre,
                                           atributo.propiedad.nombre + ' (' +
                                           atributo.propiedad.namespace
                                           .namespace
                                           + ')')
            else:
                fichero += atributo_var_privado % (atributo.nombre,
                                                   atributo.propiedad
                                                   .nombre + ' (' +
                                                   atributo.propiedad.namespace
                                                   .namespace + ')')

        relaciones = Relacion.objects.all()
        relaciones = relaciones.exclude(propiedad=None)

        fichero += model_var_close

    relaciones = Relacion.objects.all()
    relaciones = relaciones.exclude(propiedad=None)
    relaciones = relaciones.exclude(modelo__entidad=None)
    relaciones = relaciones.exclude(modelo_relacionado__entidad=None)

    for relacion in relaciones:
        mod = relacion.modelo
        mod_rel = relacion.modelo_relacionado

        fichero += relacion_var % (mod.aplicacion + '_' + mod.nombre,
                                   mod_rel.aplicacion + '_' + mod_rel.nombre,
                                   relacion.nombre + ' (' +
                                   relacion.propiedad.nombre + ' - ' +
                                   relacion.propiedad.namespace.namespace +
                                   ')')

    fichero += '}'

    # Create the graph with pydot
    grafico = graph_from_dot_data(fichero.encode('ascii'))
    try:
        foto = grafico.create(grafico.prog, 'png')
        response = HttpResponse(foto, mimetype='image/png')
        response['Content-Disposition'] = 'attachment; filename="graph.png"'
    except InvocationException:
        response = HttpResponse(fichero, mimetype='text/plain')
        response['Content-Disposition'] = 'attachment; filename="graph.dot"'

    return response
