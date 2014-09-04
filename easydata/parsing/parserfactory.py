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
En este modulo se almacena el factory que se encargara en funcion del formato
del fichero que se desea parsear para cargar un nuevo namespace, de devolver la
instancia del parseador adecuado inicializado
"""

from easydata.parsing.rdf_parser import ParserN3, ParserXML

__author__ = 'llerena'


def parser_factory(archivo, formato, namespace):
    """
    Esta funcion hace de Factory, de tal forma que a partir del formato del
    fichero, devolvera el parseador asociado
    :param archivo: archivo que se va a parsear
    :param formato: formato en el que se encuentra el archivo
    :param namespace: namespace donde se van a incluir las entidades y
        propiedades parseadas
    :return: devuelve un objecto de la clase Parseador inicializado.
    """
    if formato == 'R':  # Formato RDF/XML
        return ParserXML(archivo, namespace)
    elif formato == 'N':  # Formato RDF/Ntriples
        return ParserN3(archivo, namespace)
    else:
        raise Exception("Not implemented parser for this type")
