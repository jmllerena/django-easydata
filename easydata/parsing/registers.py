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
En este modulo se definen los distintos tipos de Registros que se van a
utilizar, que son registros para las entidades y registros para las
propiedades. Estos se encargaran de almacenar los datos de cada uno, validar
los mismos y almacenarlos en la base de datos.
"""

from easydata.models import Entidad, Propiedad

__author__ = 'llerena'


class RegisterEntity(object):
    """
    Este registro se usa para almacenar las entidades de las que estara
    compuesto un determinado namespace. Este registro se encargara de
    administrar la correcta creacion de la entidad, asi como de crear sus
    relaciones entre ellos.
    """
    name = None
    """almacena el nombre de la entidad"""
    description = None
    """almacena la descripcion asociada a la entidad"""
    label = None
    """almacena la etiqueta asociada a la entidad"""
    namespace = None
    """almacena el namespace al que pertenece la entidad"""
    fathers = None
    """almacena las entidades padre de las que hereda la entidad"""
    entity = None
    """almacena la instancia de entidad una vez creada"""
    url = None
    """almacena la url asociada a la entidad"""

    def __init__(self, name, description, label, namespace, fathers, url=""):
        """
        Constructor de la clase RegisterEntity que almacena los datos de una
        determinada entidad
        :param name: Nombre de la entidad
        :param description: Descripcion asociada a la entidad
        :param label: etiqueta asociada a la entidad
        :param namespace: namespace al que pertenece
        :param fathers: padres del que hereda sus propiedades
        :param url: url donde se encuentra su especificacion
        """
        self.name = name
        if not description is None:
            self.description = description[0:500]
        if not label is None:
            self.label = label[0:100]
        self.namespace = namespace
        self.fathers = fathers
        self.url = url

        if namespace.url == "" or namespace.url is None:
            namespace.url = self.url
            namespace.save()

    def register(self):
        """
        Salva en la base de datos la entidad que almacena el registro
        """
        try:
            ent = Entidad.objects.all()
            ent = ent.filter(nombre=self.name)
            ent = ent.filter(namespace__url=self.url)
            self.entity = ent.get()

            #Si continua, es que el elemento existe y no se debe de modificar
        except Entidad.DoesNotExist:
            #Create de entity object
            if self.url == self.namespace.url and self.name != "":
                self.entity = Entidad(nombre=self.name,
                                      descripcion=self.description,
                                      etiqueta=self.label,
                                      namespace=self.namespace)
                #Save on DB
                self.entity.save()

    def register_fathers(self):
        """
        Agrega las relaciones de la entidad con su padre, si posee
        """
        if not self.entity is None:
            for father in self.fathers:
                try:
                    father_entity = Entidad.objects.all()
                    father_entity = father_entity.filter(nombre=father['name'])
                    father_entity = father_entity.filter(
                                                  namespace__url=father['url'])
                    father_entity = father_entity.get()
                    self.entity.padres.add(father_entity)
                    self.entity.save()
                except Entidad.DoesNotExist:
                    # Si son del mismo namespace
                    if self.namespace.url == father['url'] and \
                       father['name'] != "":
                        father_entity = Entidad(nombre=father['name'],
                                                namespace=self.namespace)
                        father_entity.save()
                        self.entity.padres.add(father_entity)
                        self.entity.save()

    def update_registers(self):
        """
        This method is used when the namespace exists, and you only want to
        update the fields, or create the fields that do not exist before
        """
        try:
            ent = Entidad.objects.all()
            ent = ent.filter(nombre=self.name)
            ent = ent.filter(namespace__url=self.url)
            self.entity = ent.get()

            #Si continua, es que el elemento existe y debemos actualizarlo
            self.entity.etiqueta = self.label
            self.entity.descripcion = self.description
            #Save on DB
            self.entity.save()
        except Entidad.DoesNotExist:
            #Create de entity object
            if self.url == self.namespace.url:
                self.entity = Entidad(nombre=self.name,
                                      descripcion=self.description,
                                      etiqueta=self.label,
                                      namespace=self.namespace)
                #Save on DB
                self.entity.save()

    def update_fathers(self):
        """
        This methos is only used when the namespace exists, and you only want
        to update the relations between the entities
        """
        if not self.entity is None:
            for father in self.fathers:
                try:
                    father_entity = Entidad.objects.all()
                    father_entity = father_entity.filter(nombre=father['name'])
                    father_entity = father_entity.filter(
                                                  namespace__url=father['url'])
                    father_entity = father_entity.get()

                    if not father_entity in self.entity.padres.all():
                        self.entity.padres.add(father_entity)
                        self.entity.save()
                except Entidad.DoesNotExist:
                    # Si son del mismo namespace
                    if father['url'] == self.namespace.url and \
                       father['name'] != "":
                        father_entity = Entidad(nombre=father['name'],
                                                namespace=self.namespace)
                        father_entity.save()
                        self.entity.padres.add(father_entity)
                        self.entity.save()


class RegisterProperty(object):
    """
    Este es un registro para almacenar las propiedades de las entidades. Este
    registro se encarga de almacenar una determinada propiedad, sus relaciones,
    tipo y demas caracteristicas, para posteriormente salvar las mismas en la
    base de datos.
    """
    name = None
    """nombre de la propidad"""
    description = None
    """descripcion asociada a la propiedad"""
    label = None
    """etiqueta asociada a la propiedad"""
    relations = None
    """almacena las entidades con las que esta relacionada"""
    namespace = None
    """almacena el namespace al que pertenece"""
    property = None
    """almacena la instancia de la propiedad una vez creada"""
    types = None
    """tipos a los que hace referencia la propiedad"""
    simple = None
    """almacena si es una propiedad de tipo simple"""
    url = None
    """almacena la url asociada a la propiedad"""

    def __init__(self, name, description, label, namespace,
                 relations, types, url="", tipos_base=[]):
        """
        Constructor de la clase RegisterProperty que almacena los datos de una
        determinada propiedad
        :param name: Nombre de la propiedad
        :param description: Descripcion asociada a la propiedad
        :param label: etiqueta asociada a la propiedad
        :param namespace: namespace al que pertenece
        :param relations: entidades con la que esta relacionadas
        :param types: tipos de datos a los que hace referencia
        """
        self.name = name
        if not description is None:
            self.description = description[0:500]
        if not label is None:
            self.label = label[0:100]
        self.namespace = namespace
        self.relations = relations

        #Check the types of the property
        self.simple = False

        for tipo in types:
            if tipo['url'] == "http://www.w3.org/2000/01/rdf-schema#" or \
               (len(tipos_base) != 0 and tipo['name'] in tipos_base):
                self.simple = True
        if len(types) == 0:
            self.simple = True

        self.types = types
        self.url = url

        if namespace.url == "" or namespace.url is None:
            namespace.url = self.url
            namespace.save()

    def register(self):
        """
        Salva en la base de datos la propiedad que almacena el registro
        """
        #Get de property object
        try:
            propiedades = Propiedad.objects.all()
            propiedades = propiedades.filter(nombre=self.name)
            propiedades = propiedades.filter(namespace__url=self.url)
            propiedades = propiedades.distinct()
            self.property = propiedades.get()

            #Si llegamos aqui es que existe y no se debe de hacer nada
        except Propiedad.DoesNotExist:
            if self.namespace.url == self.url:
                self.property = Propiedad(namespace=self.namespace,
                                          nombre=self.name,
                                          descripcion=self.description,
                                          etiqueta=self.label,
                                          simple=self.simple)

        if not self.property is None:
            #Save on DB
            self.property.save()

            for tipo in self.types:
                if tipo['url'] != "http://www.w3.org/2000/01/rdf-schema#":

                    entidades = Entidad.objects.all()
                    entidades = entidades.filter(nombre=tipo['name'])
                    entidades = entidades.filter(namespace__url=tipo['url'])
                    try:
                        entidades = entidades.get()

                        self.property.tipo.add(entidades)
                    except Entidad.DoesNotExist:
                        # Si son del mismo namespace
                        if self.url == tipo['url'] and tipo['name'] != "":
                            entidades = Entidad(nombre=tipo['name'],
                                                namespace=self.namespace)
                            entidades.save()
                            self.property.tipo.add(entidades)

            self.property.save()

            if self.property.tipo.all().count() == 0:
                self.property.simple = True
                self.property.save()

    def register_relations(self):
        """
        Agrega las relaciones de la propiedad con las distintas entidades
        """
        if not self.property is None:
            for rel in self.relations:
                try:
                    ent = Entidad.objects.all()
                    ent = ent.filter(nombre=rel['name'])
                    ent = ent.filter(namespace__url=rel['url'])
                    ent = ent.get()

                    self.property.entidades.add(ent)
                except Entidad.DoesNotExist:
                    # Si son del mismo namespace
                    if self.url == rel['url'] and not rel['name'] is None and \
                       rel['name'] != "":
                        ent = Entidad(nombre=rel['name'],
                                      namespace=self.namespace)
                        ent.save()
                        self.property.entidades.add(ent)

            self.property.save()

    def update_registers(self):
        """
        This method is used when the namespace exists, and you only want to
        update the fields, or create the fields that do not exist before
        """
        #Get de property object
        try:
            propiedades = Propiedad.objects.all()
            propiedades = propiedades.filter(nombre=self.name)
            propiedades = propiedades.filter(namespace__url=self.url)
            propiedades = propiedades.distinct()
            self.property = propiedades.get()

            #Si llegamos aqui es que existe y se debe de actualizar
            if not self.description is None and self.description != '':
                self.property.descripcion = self.description
            if not self.label is None and self.label != '':
                self.property.etiqueta = self.label
            self.property.simple = self.simple
            self.property.save()
        except Propiedad.DoesNotExist:
            if self.url == self.namespace.url:
                self.property = Propiedad(namespace=self.namespace,
                                          nombre=self.name,
                                          descripcion=self.description,
                                          etiqueta=self.label,
                                          simple=self.simple)
                #Save on DB
                self.property.save()

        if not self.property is None:
            for tipo in self.types:
                if tipo['url'] != "http://www.w3.org/2000/01/rdf-schema#":
                    entidades = Entidad.objects.all()
                    entidades = entidades.filter(nombre=tipo['name'])
                    entidades = entidades.filter(namespace__url=tipo['url'])
                    try:
                        entidades = entidades.get()

                        if not entidades in self.property.tipo.all():
                            self.property.tipo.add(entidades)
                    except Entidad.DoesNotExist:
                        # Si son del mismo namespace
                        if self.namespace.url == tipo['url'] and \
                           tipo['name'] != "":
                            entidades = Entidad(nombre=tipo['name'],
                                                namespace=self.namespace)
                            entidades.save()
                            self.property.tipo.add(entidades)

            self.property.save()

            if self.property.tipo.all().count() == 0:
                self.property.simple = True
                self.property.save()

    def update_relations(self):
        """
        Agrega las relaciones de la propiedad con las distintas entidades
        """
        if not self.property is None:
            for rel in self.relations:
                try:
                    ent = Entidad.objects.all()
                    ent = ent.filter(nombre=rel['name'])
                    ent = ent.filter(namespace__url=rel['url'])
                    ent = ent.get()

                    if not ent in self.property.entidades.all():
                        self.property.entidades.add(ent)
                except Entidad.DoesNotExist:
                    # Si son del mismo namespace
                    if self.namespace.url == rel['url'] and \
                       not rel['name'] is None and rel['name'] != "":
                        ent = Entidad(nombre=rel['name'],
                                      namespace=self.namespace)
                        ent.save()
                        self.property.entidades.add(ent)

            self.property.save()
