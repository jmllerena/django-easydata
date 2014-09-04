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
Este modulo contiene el comando easydata_d2rq que se ejecutara desde el
manage.py de Django, el cual se encarga de generar el fichero de configuracion
para d2rq en funcion de la configuracion realizada en la aplicacion
"""

from django.core.management.base import BaseCommand
from rdflib import Graph, Literal
from easydata.models import NameSpace, Modelo, Relacion, Atributo


class Command(BaseCommand):
    """
    Esta clase se encarga de implementar el comando d2rq del manage.py
    """

    args = '<app_name>'
    help = 'Genera la configuracion para d2rq en funcion de la realizada en la\
            aplicacion easydataz'

    def handle(self, *args, **options):
        """
        Este command sirve para generar un fichero d2rq con la configuracion
        realizada en la aplicacion
        """
        g = Graph()

        # Add the common namespaces
        g.bind('map', '#')
        g.bind('db', '')
        g.bind('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        g.bind('rdfs', 'http://www.w3.org/2000/01/rdf-schema#')
        g.bind('xsd', 'http://www.w3.org/2001/XMLSchema#')
        g.bind('d2rq', 'http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#')
        g.bind('jdbc', 'http://d2rq.org/terms/jdbc/')

        # Add the namespaces includes in the easydata application
        for namespace in NameSpace.objects.all():
            g.bind(namespace.short_name, namespace.url)

        # Get all the used namespaces
        namespaces = dict()
        for name in g.namespaces():
            namespaces[name[0]] = name[1]

        #Apartado configuracion BD
        g.add((namespaces['map'] + 'database', namespaces['rdf'] + 'type',
               namespaces['d2rq'] + 'Database'))
        g.add((namespaces['map'] + 'database', namespaces['d2rq'] +
               'jdbcDriver', Literal("")))
        g.add((namespaces['map'] + 'database', namespaces['d2rq'] + 'jdbcDSN',
               Literal("")))
        g.add((namespaces['map'] + 'database', namespaces['d2rq'] + 'username',
               Literal("")))
        g.add((namespaces['map'] + 'database', namespaces['d2rq'] + 'password',
               Literal("")))
        g.add((namespaces['map'] + 'database',
               namespaces['jdbc'] + 'autoReconnect', Literal("")))
        g.add((namespaces['map'] + 'database',
               namespaces['jdbc'] + 'zeroDateTimeBehavior',
               Literal("convertToNull")))

        # Captamos solo aquellos modelos que estan mapeados y son visibles
        modelos = Modelo.objects.all()
        modelos = modelos.filter(visibilidad='V')
        modelos = modelos.exclude(entidad=None)

        # Recorremos cada uno de los modelos
        for modelo in modelos:
            mc = modelo.devolver_modelo()

            if not mc is None:
                # Incluyo las propiedades del modelo al grafo
                g.add((namespaces['map'] + mc._meta.db_table,
                       namespaces['rdf'] + 'type',
                       namespaces['d2rq'] + 'ClassMap'))
                g.add((namespaces['map'] + mc._meta.db_table,
                       namespaces['d2rq'] + 'dataStorage',
                       namespaces['map'] + 'database'))
                g.add((namespaces['map'] + mc._meta.db_table,
                       namespaces['d2rq'] + 'classDefinitionLabel',
                       Literal(mc._meta.db_table)))
                g.add((namespaces['map'] + mc._meta.db_table,
                       namespaces['d2rq'] + 'uriPattern',
                       Literal(modelo.get_d2rq_url())))
                g.add((namespaces['map'] + mc._meta.db_table,
                       namespaces['d2rq'] + 'class',
                       namespaces[modelo.entidad.namespace.short_name] +
                       modelo.entidad.nombre))

                # Buscamos cada uno de sus atributos
                attrs = Atributo.objects.all()
                attrs = attrs.exclude(propiedad=None)
                attrs = attrs.filter(visibilidad='V')
                attrs = attrs.filter(modelo=modelo)

                # Recorremos los atributos para incluirlos en el grafo
                for attr in attrs:
                    ac = attr.get_field_class()

                    if not ac is None:
                        datatype = self.get_datatype(ac.__class__)
                        #Compruebo si estan en la misma tabla
                        if ac.model._meta.db_table == mc._meta.db_table:
                            # Incluyo el atributo en el grafo
                            g.add((namespaces['map'] + mc._meta.db_table +
                                   '_' + ac.get_attname_column()[1],
                                   namespaces['rdf'] + 'type',
                                   namespaces['d2rq'] + 'PropertyBridge'))
                            g.add((namespaces['map'] + mc._meta.db_table +
                                   '_' + ac.get_attname_column()[1],
                                   namespaces['d2rq'] + 'belongsToClassMap',
                                   namespaces['map'] + mc._meta.db_table))
                            g.add((namespaces['map'] + mc._meta.db_table +
                                   '_' + ac.get_attname_column()[1],
                                   namespaces['d2rq'] +
                                   'propertyDefinitionLabel',
                                   Literal(mc._meta.db_table + ' ' +
                                           ac.get_attname_column()[1])))
                            g.add((namespaces['map'] + mc._meta.db_table +
                              '_' + ac.get_attname_column()[1],
                              namespaces['d2rq'] + 'property',
                              namespaces[attr.propiedad.namespace.short_name] +
                              attr.propiedad.nombre))
                            g.add((namespaces['map'] + mc._meta.db_table +
                                   '_' + ac.get_attname_column()[1],
                                   namespaces['d2rq'] + 'column',
                                   Literal(mc._meta.db_table + '.' +
                                           ac.get_attname_column()[1])))
                            if not datatype is None:
                                g.add((namespaces['map'] + mc._meta.db_table +
                                       '_' + ac.get_attname_column()[1],
                                       namespaces['d2rq'] + 'datatype',
                                       namespaces['xsd'] + datatype))
                        else:
                            # Caso de que estuvieran en distintas tablas
                            pl = modelo.get_parent_link(ac.model)

                            if not pl is None:
                                g.add((namespaces['map'] + mc._meta.db_table +
                                       '_' + ac.get_attname_column()[1],
                                       namespaces['rdf'] + 'type',
                                       namespaces['d2rq'] + 'PropertyBridge'))
                                g.add((namespaces['map'] + mc._meta.db_table +
                                       '_' + ac.get_attname_column()[1],
                                       namespaces['d2rq'] +
                                       'belongsToClassMap',
                                       namespaces['map'] + mc._meta.db_table))
                                g.add((namespaces['map'] + mc._meta.db_table +
                                       '_' + ac.get_attname_column()[1],
                                       namespaces['d2rq'] +
                                       'propertyDefinitionLabel',
                                       Literal(mc._meta.db_table + ' ' +
                                               ac.get_attname_column()[1])))
                                g.add((namespaces['map'] + mc._meta.db_table +
                              '_' + ac.get_attname_column()[1],
                              namespaces['d2rq'] + 'property',
                              namespaces[attr.propiedad.namespace.short_name] +
                              attr.propiedad.nombre))
                                g.add((namespaces['map'] + mc._meta.db_table +
                                       '_' + ac.get_attname_column()[1],
                                       namespaces['d2rq'] + 'column',
                                       Literal(pl.rel.to._meta.db_table + '.' +
                                               ac.get_attname_column()[1])))
                                g.add((namespaces['map'] + mc._meta.db_table +
                                   '_' + ac.get_attname_column()[1],
                                   namespaces['d2rq'] + 'join',
                                   Literal(mc._meta.db_table + '.' +
                                           pl.get_attname_column()[1] +
                                           ' => ' + pl.rel.to._meta.db_table
                                           + '.' + pl.rel.field_name)))
                                if not datatype is None:
                                    g.add((namespaces['map'] +
                                           mc._meta.db_table + '_' +
                                           ac.get_attname_column()[1],
                                           namespaces['d2rq'] + 'datatype',
                                           namespaces['xsd'] + datatype))

                # Buscamos cada una de las relaciones del modelo
                rels = Relacion.objects.all()
                #rels = rels.exclude(propiedad=None)
                rels = rels.filter(modelo=modelo)

                # Recorremos las relaciones para incluirlas en el grafo
                for rel in rels:
                    rc = rel.get_field_class()

                    #Compruebo si estan en la misma tabla
                    if not rc is None and \
                       rc.model._meta.db_table == mc._meta.db_table:
                        # Si es del tipo ManyToMany
                        if rel.tipo_relacion == "M":
                            #Si es visible
                            if rel.visibilidad == 'V' and \
                               not rel.propiedad is None and \
                               rel.modelo.visibilidad == 'V' and \
                               rel.modelo_relacionado.visibilidad == 'V':
                                # Primer sentido
                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['rdf'] + "type",
                                   namespaces['d2rq'] + "PropertyBridge"))

                                g.add((namespaces['map'] + mc._meta.db_table +
                               "_" + rc.get_attname_column()[1] + '__ref',
                               namespaces['d2rq'] + "property",
                               namespaces[rel.propiedad.namespace.short_name] +
                               rel.propiedad.nombre))

                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['d2rq'] + "belongsToClassMap",
                                   namespaces['map'] + mc._meta.db_table))

                                g.add((namespaces['map'] + mc._meta.db_table +
                      "_" + rc.get_attname_column()[1] + '__ref',
                      namespaces['d2rq'] + "refersToClassMap",
                      namespaces['map'] +
                      rel.modelo_relacionado.devolver_modelo()._meta.db_table))

                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['d2rq'] + "join",
                                   Literal(mc._meta.db_table + '.' +
                                           rc.m2m_target_field_name() +
                                           " <= " + rc.m2m_db_table() + '.' +
                                           rc.m2m_column_name())))

                                g.add((namespaces['map'] + mc._meta.db_table +
                      "_" + rc.get_attname_column()[1] + '__ref',
                      namespaces['d2rq'] + "join",
                      Literal(rc.m2m_db_table() + '.' +
                      rc.m2m_reverse_name() + " => " +
                      rel.modelo_relacionado.devolver_modelo()._meta.db_table +
                      '.' + self.get_pk_field(rc.rel.to))))

                            # Sentido contrario
                            rel_reverse = Relacion.objects.all()
                            rel_reverse = rel_reverse.exclude(propiedad=None)
                            rel_reverse = rel_reverse.filter(
                                                 modelo=rel.modelo_relacionado)
                            rel_reverse = rel_reverse.filter(
                                                 modelo_relacionado=rel.modelo)
                            rel_reverse = rel_reverse.filter(tipo_relacion="M")
                            rel_reverse = rel_reverse.filter(
                                         nombre=rc.related.get_accessor_name())
                            rel_reverse = rel_reverse.filter(visibilidad='V')
                            rel_reverse = rel_reverse.exclude(
                                                       modelo__visibilidad='P')
                            rel_reverse = rel_reverse.exclude(
                                           modelo_relacionado__visibilidad='P')
                            if rel_reverse.count() == 1:
                                rel_reverse = rel_reverse.get()

                                g.add((namespaces['map'] +
                      rel.modelo_relacionado.devolver_modelo()._meta.db_table +
                      "_" + rc.related.get_accessor_name() + '__ref',
                      namespaces['rdf'] + "type",
                      namespaces['d2rq'] + "PropertyBridge"))

                                g.add((namespaces['map'] +
                      rel.modelo_relacionado.devolver_modelo()._meta.db_table +
                      "_" + rc.related.get_accessor_name() + '__ref',
                      namespaces['d2rq'] + "property",
                      namespaces[rel_reverse.propiedad.namespace.short_name] +
                      rel_reverse.propiedad.nombre))

                                g.add((namespaces['map'] +
                      rel.modelo_relacionado.devolver_modelo()._meta.db_table +
                      "_" + rc.related.get_accessor_name() + '__ref',
                      namespaces['d2rq'] + "belongsToClassMap",
                      namespaces['map'] +
                      rel.modelo_relacionado.devolver_modelo()._meta.db_table))

                                g.add((namespaces['map'] +
                      rel.modelo_relacionado.devolver_modelo()._meta.db_table +
                      "_" + rc.related.get_accessor_name() + '__ref',
                      namespaces['d2rq'] + "refersToClassMap",
                      namespaces['map'] + mc._meta.db_table))

                                g.add((namespaces['map'] +
              rel.modelo_relacionado.devolver_modelo()._meta.db_table +
              "_" + rc.related.get_accessor_name() + '__ref',
              namespaces['d2rq'] + "join",
              Literal(rel.modelo_relacionado.devolver_modelo()._meta.db_table +
                      '.' + self.get_pk_field(rc.rel.to) + " <= " +
                      rc.m2m_db_table() + '.' + rc.m2m_reverse_name())))

                                g.add((namespaces['map'] +
                      rel.modelo_relacionado.devolver_modelo()._meta.db_table +
                      "_" + rc.related.get_accessor_name() + '__ref',
                      namespaces['d2rq'] + "join",
                      Literal(rc.m2m_db_table() + '.' + rc.m2m_column_name() +
                              " => " + mc._meta.db_table + '.' +
                              rc.m2m_target_field_name())))
                        else:
                            #Relaciones O2O y FK
                            if rel.visibilidad == 'V' and \
                               not rel.propiedad is None and \
                               rel.modelo.visibilidad == 'V' and \
                               rel.modelo_relacionado.visibilidad == 'V':

                                # Primer sentido
                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['rdf'] + "type",
                                   namespaces['d2rq'] + "PropertyBridge"))

                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['d2rq'] + "belongsToClassMap",
                                   namespaces['map'] + mc._meta.db_table))

                                g.add((namespaces['map'] + mc._meta.db_table +
                      "_" + rc.get_attname_column()[1] + '__ref',
                      namespaces['d2rq'] + "refersToClassMap",
                      namespaces['map'] +
                      rel.modelo_relacionado.devolver_modelo()._meta.db_table))

                                g.add((namespaces['map'] + mc._meta.db_table +
                                  "_" + rc.get_attname_column()[1] + '__ref',
                                  namespaces['d2rq'] + "join",
                                  Literal(mc._meta.db_table + '.' +
                                          rc.get_attname_column()[1] + " => " +
                                          rc.rel.to._meta.db_table + '.' +
                                          self.get_pk_field(rc.rel.to))))

                                g.add((namespaces['map'] + mc._meta.db_table +
                               "_" + rc.get_attname_column()[1] + '__ref',
                               namespaces['d2rq'] + "property",
                               namespaces[rel.propiedad.namespace.short_name] +
                               rel.propiedad.nombre))

                            #Generamos la consulta en el otro sentido
                            rel_reverse = Relacion.objects.all()
                            rel_reverse = rel_reverse.exclude(propiedad=None)
                            rel_reverse = rel_reverse.filter(
                                                 modelo=rel.modelo_relacionado)
                            rel_reverse = rel_reverse.filter(
                                                 modelo_relacionado=rel.modelo)
                            rel_reverse = rel_reverse.filter(
                                         nombre=rc.related.get_accessor_name())
                            rel_reverse = rel_reverse.filter(visibilidad='V')
                            rel_reverse = rel_reverse.exclude(
                                                       modelo__visibilidad='P')
                            rel_reverse = rel_reverse.exclude(
                                           modelo_relacionado__visibilidad='P')
                            #Si hay una relacion en sentido contrario visible
                            if rel_reverse.count() == 1:
                                rel_reverse = rel_reverse.get()

                                g.add((namespaces['map'] +
                                       rc.rel.to._meta.db_table + "_" +
                                       rc.related_query_name() + '__ref',
                                       namespaces['rdf'] + "type",
                                       namespaces['d2rq'] + "PropertyBridge"))

                                g.add((namespaces['map'] +
                                       rc.rel.to._meta.db_table + "_" +
                                       rc.related_query_name() + '__ref',
                                       namespaces['d2rq'] +
                                       "belongsToClassMap", namespaces['map'] +
                                       rc.rel.to._meta.db_table))

                                g.add((namespaces['map'] +
                       rc.rel.to._meta.db_table + "_" +
                       rc.related_query_name() + '__ref',
                       namespaces['d2rq'] + "property",
                       namespaces[rel_reverse.propiedad.namespace.short_name] +
                       rel_reverse.propiedad.nombre))

                                g.add((namespaces['map'] +
                                   rc.rel.to._meta.db_table + "_" +
                                   rc.related_query_name() + '__ref',
                                   namespaces['d2rq'] + "refersToClassMap",
                                   namespaces['map'] +
                                   mc._meta.db_table))

                                g.add((namespaces['map'] +
                                       rc.rel.to._meta.db_table + "_" +
                                       rc.related_query_name() + '__ref',
                                       namespaces['d2rq'] + "join",
                                       Literal(rc.rel.to._meta.db_table + '.' +
                                               self.get_pk_field(rc.rel.to) +
                                               " <= " + mc._meta.db_table + '.'
                                               + rc.get_attname_column()[1])))
                    elif not rc is None and \
                         rc.model._meta.db_table != mc._meta.db_table:
                        # Si es una relacion M2M
                        pl = modelo.get_parent_link(rc.model)
                        if rel.tipo_relacion == "M":
                            if rel.visibilidad == 'V' and \
                               not rel.propiedad is None and \
                               rel.modelo.visibilidad == 'V' and \
                               rel.modelo_relacionado.visibilidad == 'V' and \
                               not pl is None:
                                # Primer sentido
                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['rdf'] + "type",
                                   namespaces['d2rq'] + "PropertyBridge"))

                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['d2rq'] + "belongsToClassMap",
                                   namespaces['map'] + mc._meta.db_table))

                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['d2rq'] + "refersToClassMap",
                                   namespaces['map'] +
                                   rc.rel.to._meta.db_table))

                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['d2rq'] + "join",
                                   Literal(rc.model._meta.db_table + '.' +
                                           rc.m2m_target_field_name() +
                                           " <= " + rc.m2m_db_table() + '.' +
                                           rc.m2m_column_name())))

                                g.add((namespaces['map'] + mc._meta.db_table +
                                  "_" + rc.get_attname_column()[1] + '__ref',
                                  namespaces['d2rq'] + "join",
                                  Literal(rc.m2m_db_table() + '.' +
                                          rc.m2m_reverse_name() + " => " +
                                          rc.rel.to._meta.db_table + '.' +
                                          self.get_pk_field(rc.rel.to))))

                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['d2rq'] + "join",
                                   Literal(mc._meta.db_table + '.' +
                                           pl.get_attname_column()[1] +
                                           " => " + pl.rel.to._meta.db_table +
                                           '.' + pl.rel.field_name)))

                                g.add((namespaces['map'] + mc._meta.db_table +
                               "_" + rc.get_attname_column()[1] + '__ref',
                               namespaces['d2rq'] + "property",
                               namespaces[rel.propiedad.namespace.short_name] +
                               rel.propiedad.nombre))
                        else:  # Si son relacionas O2O o FK
                            if rel.visibilidad == 'V' and \
                               not rel.propiedad is None and \
                               rel.modelo.visibilidad == 'V' and \
                               rel.modelo_relacionado.visibilidad == 'V' and \
                               not pl is None:
                                # Primer sentido
                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['rdf'] + "type",
                                   namespaces['d2rq'] + "PropertyBridge"))

                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['d2rq'] + "belongsToClassMap",
                                   namespaces['map'] + mc._meta.db_table))

                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['d2rq'] + "refersToClassMap",
                                   namespaces['map'] +
                                   rc.rel.to._meta.db_table))

                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['d2rq'] + "join",
                                   Literal(mc._meta.db_table + '.' +
                                           pl.get_attname_column()[1] +
                                           " <= " + pl.rel.to._meta.db_table +
                                           '.' + pl.rel.field_name)))

                                g.add((namespaces['map'] + mc._meta.db_table +
                                   "_" + rc.get_attname_column()[1] + '__ref',
                                   namespaces['d2rq'] + "join",
                                   Literal(pl.rel.to._meta.db_table + '.' +
                                          rc.get_attname_column()[1] +
                                          " => " + rc.rel.to._meta.db_table +
                                          '.' + self.get_pk_field(rc.rel.to))))

                                g.add((namespaces['map'] + mc._meta.db_table +
                               "_" + rc.get_attname_column()[1] + '__ref',
                               namespaces['d2rq'] + "property",
                               namespaces[rel.propiedad.namespace.short_name] +
                               rel.propiedad.nombre))
                    else:
                        pass  # Caso de que sea None

        # Devuelve el fichero rdf con la configuracion
        print g.serialize(format="turtle")

    def get_datatype(self, atributo):
        """
        Busca el tipo de dato del un determinado field y devuelve su
        representacion en el espacio de nombres xsd
        """
        if not atributo is None:
            if atributo.__name__ in ('AutoField', 'BigIntegerField',
                                     'IntegerField', 'SmallIntegerField'
                                     'PositiveIntegerField',
                                     'PositiveSmallIntegerField'):
                tipo_relacion = "integer"
            elif atributo.__name__ == 'BooleanField':
                tipo_relacion = "boolean"
            elif atributo.__name__ == 'FloatField':
                tipo_relacion = "float"
            elif atributo.__name__ == 'DateTimeField':
                tipo_relacion = "dateTime"
            elif atributo.__name__ == 'DateField':
                tipo_relacion = "date"
            else:
                return self.get_datatype(atributo.__base__)
        else:
            tipo_relacion = None

        return tipo_relacion

    def get_pk_field(self, Modelo):
        """
        Devuelve el nombre del campo que es clave primaria del modelo
        """
        # Capta el nombre de la clave primaria
        nombre_pk = Modelo._meta.pk.name
        # Mira si la clave primaria es un enlace a otro modelo
        field_pk = getattr(Modelo, nombre_pk, None)

        # Si es un enlace a otro modelo, capta el nombre de la columna
        if not field_pk is None and hasattr(field_pk, 'field'):
            field_pk = field_pk.field

            return field_pk.get_attname_column()[1]
        elif not nombre_pk is None:  # Si esta en el mismo modelo
            return nombre_pk
        else:  # Otros casos
            return "undefined"
