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
Este modelo se encarga de almacenar la informacion relativa a las diferentes
entidades que existen en un determinado namespace
"""

from django.contrib import admin
from django.db import models
from django.core.urlresolvers import reverse
from easydata.models import NameSpace


class Entidad(models.Model):
    """
    Este modelo se encarga de registrar la informacion referente a las
    distintas entidades que componen a un namespace
    """
    nombre = models.CharField(max_length=200)
    """es el nombre de la entidad"""
    namespace = models.ForeignKey(NameSpace,
                                  related_name='entidades',
                                  on_delete=models.CASCADE)
    """es el namespace con el que esta asociado"""

    padres = models.ManyToManyField('Entidad',
                                    verbose_name=u"Entidad",
                                    related_name=u"sons",
                                    help_text=u"Seleccione entidades padre.",
                                    blank=True,
                                    null=True)
    """son los padres de los que hereda propiedades"""

    descripcion = models.CharField(max_length=500, null=True, blank=True)
    """es una descripcion que tiene asociada la entidad"""
    etiqueta = models.CharField(max_length=100, null=True, blank=True)
    """es la etiqueta que lo identifica """

    def __unicode__(self):
        """
        Devuelve la representacion unicode de la instancia del modelo
        """
        return self.nombre + u" (" + unicode(self.namespace) + u")"

    def generate_type(self):
        """
        devuelve la url que representa a la entidad
        :return:devuelve un string con la url que representa a la entidad
        """
        return self.namespace.url + self.nombre

    def generate_type_short(self):
        """
        Devuelve la cadena con el formato namespace:entidad
        :return: devuelve la entidad junto con el nombre del namespace
        """
        return self.namespace.get_type() + ":" + self.nombre

    def get_publish_url(self):
        """
        Devuelve una url de ejemplo donde se podria encontrar la informacion de
        esta entidad
        :return: devuelve string con url de ejemplo de la entidad
        """
        return u'easydata/publish/type/' + self.namespace.short_name + u'/' + \
               self.nombre + u'.(xml|nt|ttl)'

    class Meta:
        """Metadatos del modelo"""
        app_label = 'easydata'


class EntidadAdmin(admin.ModelAdmin):
    """Clase para registar en el admin de Django"""
    list_display = ['nombre', 'etiqueta', 'descripcion']
    search_fields = ['nombre', 'etiqueta', 'descripcion']


## Register in django.

admin.site.register(Entidad, EntidadAdmin)
