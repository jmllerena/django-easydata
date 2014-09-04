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
namespaces que se podran almacenar en la aplicacion
"""

from django.contrib import admin
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import ugettext as _


class NameSpace(models.Model):
    """
    Este modelo representa a los namespaces u ontologias que se cargaran en la
    aplicacion para realizar los mapeos
    """
    namespace = models.CharField(max_length=40,
                                 unique=True)
    """es el nombre del namespace"""

    short_name = models.CharField(
                 max_length=15,
                 unique=True,
                 validators=[RegexValidator(r'^[a-zA-Z][0-9a-zA-Z]*$',
                             _('Only alphanumeric characters are allowed.'))])
    """
    Es un nombre corto para el namespace que se usara en la publicacion de
    datos
    """

    formatos = (
        ('R', 'RDF/XML'),
        ('N', 'Ntriples'),
    )
    """son los formatos disponibles para la carga de namespaces"""

    url = models.URLField()
    """es la url donde se encuentra el namespace"""

    def __unicode__(self):
        return self.namespace

    def get_url(self):
        """devuelve la url del namespace"""
        return self.url

    def get_type(self):
        """devuelve el nombre corto del namespace"""
        return self.short_name

    class Meta:
        """Metadatos del modelo"""
        app_label = 'easydata'


class NameSpaceAdmin(admin.ModelAdmin):
    """Clase para registar en el admin de Django"""
    list_display = ['namespace', 'url', 'short_name']
    search_fields = ['namespace', 'url', 'short_name']


## Register in django.

admin.site.register(NameSpace, NameSpaceAdmin)
