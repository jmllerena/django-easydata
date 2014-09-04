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
Este modelo se encarga de almacenar la informacion relativa a los diferentes
fields, tanto atributos como relaciones, que existen en un modelo
"""

from django.contrib import admin
from django.db import models
from easydata.models import Modelo
from easydata.utils import descubre_padres


class Field(models.Model):
    """
    Este modelo se encarga de registrar la informacion referente a los
    distintos field que componen un modelo
    """
    nombre = models.CharField(max_length=200)
    """es el nombre del field"""

    #Tipos de visibilidad que puede tener un determinado field
    TIPOS_VISIBILIDAD = (
        ('V', 'Visible'),
        ('P', 'Privado'),
    )
    """tipos de visibilidad que puede tener un field"""

    visibilidad = models.CharField(max_length=1,
                                   choices=TIPOS_VISIBILIDAD,
                                   default='V')
    """almacena la visibilidad que posee"""

    modelo = models.ForeignKey(Modelo,  # Default null and blank are False
                               related_name='fields',
                               on_delete=models.CASCADE)
    """modelo al que pertenece"""

    propiedad = models.ForeignKey("Propiedad",
                                  related_name="fields",
                                  null=True,
                                  blank=True,
                                  on_delete=models.SET_NULL)
    """propiedad con la que esta mapeado"""

    def get_field_class(self):
        """
        Devuelve la clase django del field
        """
        mod_class = self.modelo.devolver_modelo()

        # Get all the fields
        try:
            fields = mod_class._meta.fields
        except Exception:
            return None

        for many in mod_class._meta.many_to_many:
            if not many in fields:
                fields.append(many)

        for field in fields:
            if field.name == self.nombre:
                return field

        return None

    def __unicode__(self):
        return self.nombre

    class Meta:
        """Metadatos del modelo"""
        app_label = 'easydata'
        unique_together = ('nombre', 'modelo',)


class Atributo(Field):
    """
    Este modelo se encarga de registrar la informacion referente a los
    distintos atributos que componen un modelo
    """
    tipo_field = models.CharField(max_length=200)

    def __unicode__(self):
        return self.nombre + u" - " + self.tipo_field

    class Meta:
        """Metadatos del modelo"""
        app_label = 'easydata'


class Relacion(Field):
    """
    Este modelo se encarga de registrar la informacion referente a las
    distintas relaciones que componen un modelo
    """
    TIPOS_RELACION = (
        ('O', 'OneToOneField'),
        ('M', 'ManyToManyField'),
        ('FO', 'ForeignKey'),
        ('OF', 'FromForeignKey'),
    )
    """tipos de relaciones que se pueden dar"""

    tipo_relacion = models.CharField(max_length=2,
                                     choices=TIPOS_RELACION,
                                     default='f')
    """tipo de relacion del que se trata"""

    modelo_relacionado = models.ForeignKey(Modelo,
                                           related_name='relaciones',
                                           on_delete=models.CASCADE)
    """modelo con el que se relaciona"""

    inversa = models.OneToOneField('Relacion', null=True)
    """relacion a la inversa"""

    def __unicode__(self):
        sal = self.nombre + u"(" + self.modelo.nombre + u") - "
        sal += self.tipo_relacion + u"(" + self.modelo_relacionado.nombre
        sal += u")"
        return sal

    def save(self, *args, **kwargs):
        super(Relacion, self).save()
        if not self.inversa is None and self.inversa.inversa != self:
            self.inversa.inversa = self
            self.inversa.save()

    class Meta:
        """Metadatos del modelo"""
        app_label = 'easydata'


class FieldAdmin(admin.ModelAdmin):
    """Clase para registar en el admin de Django"""
    list_display = ['nombre', 'visibilidad', 'modelo']
    search_fields = ['nombre', 'visibilidad', 'modelo']


class AtributoAdmin(admin.ModelAdmin):
    """Clase para registar en el admin de Django"""
    list_display = ['nombre', 'visibilidad', 'modelo', 'tipo_field']
    search_fields = ['nombre', 'visibilidad', 'modelo', 'tipo_field']


class RelacionAdmin(admin.ModelAdmin):
    """Clase para registar en el admin de Django"""
    list_display = ['nombre', 'visibilidad', 'modelo', 'tipo_relacion']
    search_fields = ['nombre', 'visibilidad', 'modelo', 'tipo_relacion']


## Register in django.
admin.site.register(Field, FieldAdmin)
admin.site.register(Atributo, AtributoAdmin)
admin.site.register(Relacion, RelacionAdmin)
