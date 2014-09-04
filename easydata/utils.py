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
En este modulo se definen una serie de funciones auxiliares, que ayudaran en
las tareas de mapeo y publicacion de datos.
"""

from easydata.models import Modelo
from django.db.models import Q
from django.utils.importlib import import_module
from django.contrib.sites.models import Site
from django.conf import settings

#Imports for generating the rdf graph
from rdflib import URIRef, Literal
from rdflib.namespace import RDF

__author__ = 'llerena'


def descubre_propiedades(entidad, simple=True):
    """
    Descubre todas las propiedades de la entidad
    :param entidad: es la entidad de la que se quiere conocer sus propiedades
    :param simple: indica si se quieren conocer propiedades que sean simples
    :return: devuelve un queryset con las propiedades
    """
    from easydata.models import Propiedad

    if entidad is None:
        return Propiedad.objects.none()

    padres = descubre_padres(entidad)
    padres.add(entidad)

    consulta = Q()

    #Iterate over the fathers, the properties must belong to any of the fathers
    for father in padres:
        consulta = consulta | Q(entidades=father)

    #Get all the properties and filter by the fathers
    propiedades = Propiedad.objects.all()
    propiedades = propiedades.filter(consulta)

    #Filter if the property is simple or complex
    if simple:
        propiedades = propiedades.filter(simple=True)
    else:
        propiedades = propiedades.exclude(tipo=None)

    propiedades = propiedades.distinct()

    return propiedades


def descubre_padres(entidad):
    """
    Descubre todas las entidades padre de la entidad indicada
    :param entidad: es la entidad de la que se quiere conocer todas sus
    entidades padre
    :return: devuelve un conjunto con todas las entidades padre
    """
    if entidad.padres.all().count() == 0:
        return set()
    else:
        entidades = set()
        for ent in entidad.padres.all():
            entidades.add(ent)

        for ent in entidad.padres.all():
            entidades = entidades.union(descubre_padres(ent))

        return entidades


def descubre_hijos(entidad):
    """
    Discover the entities that inherits from the provided entity
    """
    if entidad.sons.all().count() == 0:
        return set()
    else:
        entidades = set()

        for ent in entidad.sons.all():
            entidades.add(ent)
            entidades = entidades.union(descubre_hijos(ent))

        return entidades


def inverse_relation(relacion):
    """
    Casi todas las relaciones pueden recorrese en los dos sentidos, por lo que
    se crea una instancia de Relacion para cada uno de estos. Esta funcion dada
    una instancia de Relacion en un sentido, resuelve la instancia de la
    relacion en el sentido inverso.
    """
    from easydata.models import Relacion
    rc = relacion.get_field_class()

    relaciones = Relacion.objects.all()
    relaciones = relaciones.filter(modelo=relacion.modelo_relacionado)
    relaciones = relaciones.filter(modelo_relacionado=relacion.modelo)

    if not rc is None:
        relaciones = relaciones.filter(nombre=rc.related.get_accessor_name())

        if relaciones.count() == 1:
            return relaciones.get()
    else:
        for rel in relaciones:
            rc = rel.get_field_class()

            if not rc is None and \
               rc.related.get_accessor_name() == relacion.nombre:
                return rel

    return None


def get_model_assigned(instancia):
    """
    Devuelve el modelo que tiene asignado una determinada instancia
    :param instancia: es la instancia de la que se desea conocer su modelo
    asignado
    :return: devuelve la instancia de modelo en caso de que tenga, sino None
    """
    #Get the class
    class_model = instancia.__class__

    #Search the model on the database
    model = Modelo.objects.all()
    model = model.filter(nombre=class_model.__name__)
    model = model.filter(aplicacion=class_model._meta.app_label)
    model = model.filter(visibilidad='V')
    model = model.exclude(entidad=None)

    if model.count() == 1:
        return model.get()
    else:
        return None


def get_namespaces(model, visitados=[]):
    """
    Devuelve los namespaces que estan relacionados con el modelo o los modelos
    relacionados con este modelo, cuyas relaciones son visibles.
    :param model: modelo del que se desea conocer los namespaces
    :param visitados: almacena los modelos ya comprobados
    :return: devuelve una lista de namespaces implicados
    """
    names = set()
    if not model.entidad.namespace is None and not model in visitados:
        from easydata.models import Relacion

        visitados.append(model)
        names.add(model.entidad.namespace)

        rels = Relacion.objects.all()
        rels = rels.filter(visibilidad='V')
        rels = rels.filter(modelo=model)
        rels = rels.exclude(modelo_relacionado__entidad__namespace=None)

        for rel in rels:
            names = names.union(get_namespaces(rel.modelo_relacionado,
                                               visitados))

    return names


def generate_unique(model, clave, graph, names):
    """
    Rellena el grafo graph con los datos del modelo.
    :param model: es el modelo del que se va a incluir su informacion en el
    grafo
    :param clave: es la clave primaria de la instancia del modelo
    :param graph: es el grafo donde se va a incluir la informacion
    :param names: son los namespaces utilizados
    :return: devuelve el grafo con la informacion incluida
    """
    from easydata.models import Atributo, Relacion

    #Mapped entitie
    entitie = model.entidad

    #Get the model class
    model_class = model.devolver_modelo()

    #Get the instance of the model
    try:
        model_instance = model_class._default_manager.all()
        model_instance = model_instance.get(pk=clave)
    except Exception:
        return graph

    header = get_header()

    nodo_ppal = URIRef(header() + model.generate_url(model_instance))

    #Add the main node to the Graph
    graph.add((nodo_ppal, RDF.type,
               names[entitie.namespace.url].term(entitie.nombre)))

    #Get all the model's fields

    atributos = Atributo.objects.all()
    atributos = atributos.filter(modelo=model)
    atributos = atributos.filter(visibilidad='V')
    atributos = atributos.exclude(propiedad=None)

    for attr in atributos:
        graph.add((nodo_ppal,
                   names[attr.propiedad.namespace.url]
                   .term(attr.propiedad.nombre),
                   Literal(getattr(model_instance, attr.nombre, "Unknow"))))

    # Relaciones salientes
    relations = Relacion.objects.all()
    relations = relations.filter(modelo=model)
    relations = relations.filter(visibilidad="V")
    relations = relations.exclude(propiedad=None)
    relations = relations.filter(modelo_relacionado__visibilidad="V")

    #For each relation, add this to the graph
    for rel in relations:
        model_related = rel.modelo_relacionado
        mod_rel_instance = getattr(model_instance, rel.nombre, None)

        if not mod_rel_instance is None:
            if rel.tipo_relacion in ('OF', 'M') and \
               hasattr(mod_rel_instance, 'all'):
                for instance in mod_rel_instance.all():
                    graph.add((nodo_ppal,
                               names[rel.propiedad.namespace.url]
                               .term(rel.propiedad.nombre),
                               URIRef(header() +
                                      model_related.generate_url(instance))))
            else:
                graph.add((nodo_ppal,
                           names[rel.propiedad.namespace.url]
                           .term(rel.propiedad.nombre),
                           URIRef(header() +
                                  model_related
                                  .generate_url(mod_rel_instance))))

    #Relaciones entrantes
    relations = Relacion.objects.all()
    relations = relations.filter(modelo_relacionado=model)
    relations = relations.exclude(propiedad=None)
    relations = relations.filter(visibilidad="V")
    relations = relations.filter(modelo__visibilidad="V")

    for rel in relations:
        inverso = rel.inversa

        if not inverso is None and inverso.visibilidad == 'V':
            mod_rel_instance = getattr(model_instance, inverso.nombre, None)

            if not mod_rel_instance is None:
                if inverso.tipo_relacion in ('OF', 'M'):
                    for instance in mod_rel_instance.all():
                        graph.add((URIRef(header() +
                                   rel.modelo.generate_url(instance)),
                                   names[rel.propiedad.namespace.url]
                                   .term(rel.propiedad.nombre),
                                   nodo_ppal))
                else:
                    graph.add((URIRef(header() +
                                      rel.modelo
                                      .generate_url(mod_rel_instance)),
                               names[rel.propiedad.namespace.url]
                               .term(rel.propiedad.nombre),
                               nodo_ppal))


def get_header():
    """
    Return the url header from a request:
        protocol (http|https) + host
    """
    try:
        backend_module = import_module(getattr(settings,
                                               'EASYDATA_URL_HEADER',
                                               None))
        backend = getattr(backend_module, 'url_header')
    except (ImportError, AttributeError):
        backend = get_default_header

    return backend


def get_default_header():
    """
    Default method to obtain the header of the url
    """
    protocol = getattr(settings, 'PROTOCOL', 'http')

    return '%s://%s' % (protocol, Site.objects.get_current().domain)
