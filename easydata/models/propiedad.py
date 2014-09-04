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
propiedades que existen en un determinado namespace
"""


from django.contrib import admin
from django.db import models
from easydata.models import NameSpace


class Propiedad(models.Model):
    """
    Este modelo representa a las distintas propiedades de las que esta
    compuesto un determinado namespace
    """
    nombre = models.CharField(max_length=200)
    """es el nombre de la propiedad"""
    simple = models.BooleanField(default=True)
    """indica si la propiedad es simple (tipo de datos simple)"""
    namespace = models.ForeignKey(NameSpace,
                                  related_name='propiedades',
                                  on_delete=models.CASCADE)
    """indica el namespace al que pertenece la propiedad"""
    tipo = models.ManyToManyField("Entidad",
                                  verbose_name=u"Relacionados",
                                  related_name=u"relaciones",
                                  help_text=u"Seleccione relaciones.",
                                  null=True)
    """son los posibles tipos a los que puede hacer referencia la propiedad"""

    entidades = models.ManyToManyField("Entidad",
                                       verbose_name=u"Entidades",
                                       related_name="propiedades",
                                       help_text=u"Seleccione entidades.",
                                       blank=True,
                                       null=True)
    """entidades a las que pertenece dicha propiedad"""

    descripcion = models.CharField(max_length=500)
    """descripcion asociada que tenga la propiedad"""
    etiqueta = models.CharField(max_length=100)
    """etiqueta identificativa que tenga la propiedad"""

    def __unicode__(self):
        return self.nombre

    def get_full_name(self):
        """
        devuelve el nombre delnamespace junto con el nombre de la propiedad en
        el formato namespace:propiedad
        """
        return self.namespace.get_type() + ":" + self.nombre

    class Meta:
        """Metadatos del modelo"""
        app_label = 'easydata'


class PropiedadAdmin(admin.ModelAdmin):
    """Clase para registar en el admin de Django"""
    list_display = ['nombre', 'simple', 'descripcion', 'etiqueta']
    search_fields = ['nombre', 'simple', 'descripcion', 'etiqueta']


## Register in django.
admin.site.register(Propiedad, PropiedadAdmin)
