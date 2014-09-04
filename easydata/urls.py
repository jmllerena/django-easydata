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
En este fichero se encuentran todas las urls definidas en la aplicacion
EasyData junto con las vistas que tienen asociadas.
"""

from django.conf.urls.defaults import *


urlpatterns = patterns('easydata.views',
    # Plantillas de EasyData
    (r'^$', 'information.welcome'),
    (r'^information/help/models/$', 'information.info_models'),
    (r'^information/help/entities/$', 'information.info_entities'),
    (r'^information/help/templatetags/$', 'information.info_templatetags'),
    (r'^logout/$', 'sesiones.disconnect'),
    (r'^namespace/listado/$', 'namespace.listado_namespaces'),
    (r'^namespace/nuevo/$', 'namespace.vista_carga_namespace'),
    (r'^namespace/editar/(?P<id>\d+)/$', 'namespace.editar_namespace'),
    (r'^namespace/eliminar/(?P<id>\d+)/$', 'namespace.eliminar_namespace'),
    (r'^modelos/visibility/(?P<aplicacion>[a-zA-Z_][0-9a-zA-Z_]*)/$',
     'modelo.configure_visibility_models'),
    (r'^modelos/visibility/$', 'modelo.select_visibility_app'),
    (r'^namespace/map/models/$', 'map.mapea_modelo'),
    (r'^namespace/map/graphic/$', 'map.create_configuration_graph'),
    (r'^namespace/entidades/$', 'map.devuelve_entidades'),
    (r'^namespace/propiedades/namespace/$',
     'map.devuelve_propiedades_namespace'),
    (r'^namespace/propiedades/default/$', 'map.devuelve_propiedades_default'),
    (r'^namespace/map/(?P<id>\d+)/properties/$', 'map.mapea_fields'),
    #Url para publicar los datos de una instancia concreta
    (r'^publish/instance/(?P<aplicacion>[a-zA-Z_][0-9a-zA-Z_]*)/' +
     '(?P<tipo>[0-9a-zA-Z]+)-(?P<modelo>[a-zA-Z_][0-9a-zA-Z_]*)/' +
     '(?P<clave>.*).(?P<format>(xml|nt|ttl))$', 'publish.publish_model'),
    #Url para publicar todas las instancias de un modelo
    (r'^publish/model/(?P<aplicacion>[a-zA-Z_][0-9a-zA-Z_]*)/' +
     '(?P<tipo>[0-9a-zA-Z]*)-(?P<modelo>[a-zA-Z_][0-9a-zA-Z_]*).' +
     '(?P<format>(xml|nt|ttl))$', 'publish.publish_model', {'clave': None}),
    #Url para publicar los datos de un tipo
    (r'^publish/type/(?P<names>[a-zA-Z][0-9a-zA-Z]*)/(?P<tipo>[0-9a-zA-Z]*).' +
     '(?P<format>(xml|nt|ttl))$', 'publish.publish_type'),
)
