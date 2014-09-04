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
En este modulo se almacenan las vistas que se encargan de la publicacion de
datos, ya sea para la publicacion de los datos de una instancia en concreto, de
todas las instancias de un modelo y de todas las instancias de los modelos
mapeados con una determinada entidad
"""

from easydata.models import Modelo, Entidad, NameSpace
from easydata.utils import generate_unique, descubre_hijos

from rdflib import Graph, Namespace

from django.http import HttpResponse
from django.conf import settings
from django.contrib.admin.util import unquote

__author__ = 'llerena'


def publish_model(request, aplicacion, tipo, modelo, clave, format):
    """
    Publish the information of all instances of a concrete model in the format
    given
    :param request:the request of the view
    :param format:the format to publish the data
    :param aplicacion: the name of the application where is located the model
    :param tipo: is the name of the entitie mapped
    :param modelo: the name of the model
    :return: return a file in xml, ttl or nt format, with the information
    """
    #Create the graph to generate the rdf
    graph = Graph()
    limit = getattr(settings, 'EASYDATA_PUBLISH_LIMIT', 50)

    #Create dictionary for namespaces
    namespaces = dict()

    #Bind the namespaces with their names
    for name in NameSpace.objects.all():
        if name.url != "http://www.w3.org/1999/02/22-rdf-syntax-ns#":
            graph.bind(name.short_name, name.url)
        namespaces[name.url] = Namespace(name.url)

    #Get all the models related with this entities
    mod = Modelo.objects.all()
    mod = mod.filter(visibilidad='V')
    mod = mod.exclude(entidad=None)
    mod = mod.filter(entidad__nombre=tipo)
    mod = mod.filter(aplicacion=aplicacion)
    mod = mod.filter(nombre=modelo)

    if mod.count() == 1:
        mod = mod.get()
        #Get the model class
        model_class = mod.devolver_modelo()

        if not model_class is None:
            #Get all the instances
            model_instances = model_class._default_manager.all()
            if not clave is None:
                model_instances = model_instances.filter(pk=unquote(clave))
            
            model_instances = model_instances[:limit]
            for instance in model_instances:
                #Generate the graph with the model instance info
                generate_unique(mod, instance.pk, graph, namespaces)

    if format == 'nt':
        return HttpResponse(graph.serialize(format="nt"),
                            mimetype='text/plain')
    elif format == 'ttl':
        return HttpResponse(graph.serialize(format="turtle"),
                            mimetype='text/turtle')
    else:
        return HttpResponse(graph.serialize(format="xml"),
                            mimetype='application/rdf+xml')


def publish_type(request, format, names, tipo):
    """
    Publish the information of all instances which their models are mapped with
    the entity given
    :param request: the request of the view
    :param format: the format to publish the data (xml, nt or ttl)
    :param names: is the namespace short name
    :param tipo: the name of the entity
    :return: return a file in xml, ttl or nt format, with the information
    """
    entities = Entidad.objects.all()
    entities = entities.filter(nombre=tipo)
    entities = entities.filter(namespace__short_name=names)

    #Create the graph to generate the rdf
    graph = Graph()
    
    #Captamos el limite de instancias maximas a publicar
    limit = getattr(settings, 'EASYDATA_PUBLISH_LIMIT', 50)

    #Create dictionary for namespaces
    namespaces = dict()

    #Bind the namespaces with their names
    for name in NameSpace.objects.all():
        if name.url != "http://www.w3.org/1999/02/22-rdf-syntax-ns#":
            graph.bind(name.short_name, name.url)
        namespaces[name.url] = Namespace(name.url)

    for ent in entities:
        #Get all the ancients of the entitie
        hijos = descubre_hijos(ent)
        hijos.add(ent)

        #Get all the models related with this entities
        mods = Modelo.objects.all()
        mods = mods.filter(visibilidad='V')
        mods = mods.filter(entidad__in=hijos)

        for mod in mods:
            #Get the model class
            model_class = mod.devolver_modelo()

            if not model_class is None:
                #Get all the instances
                model_instances = model_class._default_manager.all()
                
                #Miro si se ha sobrepasado el limite de instancias a publicar
                if model_instances.count() <= limit:
                    limit = limit - model_instances.count()
                else:
                    model_instances = model_instances[:limit]
                    limit = 0
                
                for instance in model_instances:
                    #Generate the graph with the model instance info
                    generate_unique(mod, instance.pk, graph, namespaces)

    if format == 'nt':
        return HttpResponse(graph.serialize(format="nt"),
                            mimetype='text/plain')
    elif format == 'ttl':
        return HttpResponse(graph.serialize(format="turtle"),
                            mimetype='text/turtle')
    else:
        return HttpResponse(graph.serialize(format="xml"),
                            mimetype='application/rdf+xml')
