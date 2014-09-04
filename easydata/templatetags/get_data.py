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
Este modulo contiene todos los template tags que permiten la insercion de los
datos referentes a una intancia concreta de un modelo haciendo uso de formato
microdata.
"""


from easydata.models import Atributo, Relacion
from easydata.utils import get_model_assigned, get_header


def get_instance_data(elemento, field=None):
    """
    Return the info of a concrete model instance
    :param elemento: is the model instance
    :param field: concrete field of the instance to generate the data.
    :return: dict with the instance data.
    """
    #Get the model
    model = get_model_assigned(elemento)

    #Sino tiene ningun modelo asociado, no imprimimos nada
    if model is None:
        #Create the dict to store the data
        datos = dict()
        datos['uri'] = ""
        datos['tipo'] = ""
        datos['tipo_m'] = ""
        datos['atributos'] = list()
        datos['relaciones'] = list()

        return datos
    else:
        header = get_header()

        #Create the dict to store the data
        datos = dict()
        datos['uri'] = header() + model.generate_url(elemento)
        datos['tipo'] = model.entidad.generate_type_short()
        datos['tipo_m'] = model.entidad.generate_type()
        datos['atributos'] = list()
        datos['relaciones'] = list()

        #Get the fields of the model
        atributos = Atributo.objects.all()
        atributos = atributos.filter(modelo=model)
        atributos = atributos.filter(visibilidad='V')
        atributos = atributos.filter(modelo__visibilidad='V')
        atributos = atributos.exclude(propiedad=None)
        if not field is None:
            atributos = atributos.filter(nombre=field)

        #Recorremos cada uno de los atributos, captando sus datos
        for attr in atributos:
            registro = dict()
            registro['property'] = attr.propiedad.get_full_name()
            registro['nombre'] = attr.propiedad.namespace.url + \
                                 attr.propiedad.nombre
            registro['content'] = getattr(elemento, attr.nombre, "")
            datos['atributos'].append(registro)

        #Captamos cada una de las relaciones
        relaciones = Relacion.objects.all()
        relaciones = relaciones.filter(modelo=model)
        relaciones = relaciones.filter(modelo__visibilidad='V')
        relaciones = relaciones.filter(visibilidad='V')
        relaciones = relaciones.exclude(propiedad=None)
        relaciones = relaciones.exclude(modelo_relacionado=None)
        relaciones = relaciones.exclude(modelo_relacionado__visibilidad='P')
        if not field is None:
            relaciones = relaciones.filter(nombre=field)

        # Para cada una de las relaciones
        for rel in relaciones:
            elems = getattr(elemento, rel.nombre, None)
            if not elems is None:
                #Si es multiple, recorremos cada uno de los elementos
                if rel.tipo_relacion in ('OF', 'M') and hasattr(elems, 'all'):
                    for elem in elems.all():
                        registro = dict()
                        model_e = get_model_assigned(elem)
                        registro['resource'] = header() + \
                                               model_e.generate_url(elem)
                        registro['rel'] = rel.propiedad.get_full_name()
                        registro['itemprop'] = rel.propiedad.namespace.url + \
                                               rel.propiedad.nombre
                        datos['relaciones'].append(registro)
                else:
                    registro = dict()
                    model_e = get_model_assigned(elems)
                    registro['resource'] = header() + \
                                           model_e.generate_url(elems)
                    registro['rel'] = rel.propiedad.get_full_name()
                    registro['itemprop'] = rel.propiedad.namespace.url + \
                                           rel.propiedad.nombre
                    datos['relaciones'].append(registro)

        return datos
