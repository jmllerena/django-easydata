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
En este modulo se almacena la clase Parseador, de la cual deberan de heredar
todos los parseadores que se deseen implementar. Proporciona la interfaz que
deberan de implementar todos los parseadores
"""

__author__ = 'llerena'


class Parser(object):
    """
    Esta es una clase abstracta de la que heredaran los pareseadores que se
    deseen implementar para captar las entidades y propiedades de un
    determinado namespace.
    """
    grafo = None
    """almacena el grafo con los datos al leer el fichero"""
    list_entities = None
    """almacena el listado de propiedades que se han captado"""
    list_properties = None
    """almacena las propiedades que se han captado"""
    list_relations = None
    #list_hierarchy = None
    namespace = None
    """
    almacena el namespace al que se va a asociar las entidades y propiedades
    captadas
    """

    def __init__(self):
        """
        Constructor
        """
        self.grafo = None
        self.list_entities = None
        self.list_properties = None
        self.list_relations = None
        self.list_hierarchy = None

    def parse(self):
        """
        Metodo abstracto: este metodo se encarga de parsear los datos y
        completar las listas de propiedades y relaciones
        """
        raise NotImplementedError

    def register(self):
        """
        Save the instances of entities and properties in the DB
        """
        for register in self.list_entities:
            register.register()

        for register in self.list_entities:
            register.register_fathers()

        for register in self.list_properties:
            register.register()
            register.register_relations()

    def update(self):
        """
        Update the current registers
        """
        for register in self.list_entities:
            register.update_registers()

        for register in self.list_entities:
            register.update_fathers()

        for register in self.list_properties:
            register.update_registers()
            register.update_relations()

    def validate(self):
        """
        Metodo abstracto que se encarga de validar los datos captados en caso
        de que existiese algun tipo de validacion
        """
        raise NotImplementedError
