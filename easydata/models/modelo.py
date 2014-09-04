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
modelos que pueden existir en la aplicacion Django
"""

from django.contrib import admin
from django.db import models
from django.db.models import get_model
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.admin.util import quote


class Modelo(models.Model):
    """Este modelo representa a cada uno de los modelos del proyecto Django"""

    nombre = models.CharField(max_length=200)
    """es el nombre del modelo"""
    aplicacion = models.CharField(max_length=200)
    """es el nombre de la aplicacion donde se encuentra el modelo"""

    TIPOS_VISIBILIDAD = (
        ('V', _('Visible')),
        ('P', _('Private')),
    )
    """tipos de visibilidad que posee el modelo"""
    visibilidad = models.CharField(max_length=1,
                                   choices=TIPOS_VISIBILIDAD,
                                   default='P')
    """visibilidad que tiene el modelo"""

    entidad = models.ForeignKey("Entidad",
                                related_name='modelos',
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL)
    """entidad con la que esta mapeado el modelo"""

    def __unicode__(self):
        return self.nombre

    def devolver_modelo(self):
        """ Devuele la clase a la que representa el modelo """
        return get_model(app_label=self.aplicacion, model_name=self.nombre)

    def get_parent_link(self, modelo):
        """en caso de herencias, busca el field que apunta al modelo padre"""
        from easydata.models import Relacion

        rels = Relacion.objects.all()
        rels = rels.filter(modelo=self)

        for rel in rels:
            rel_class = rel.get_field_class()

            if not rel_class is None and rel_class.rel.parent_link and \
               rel_class.rel.to == modelo:
                return rel_class

        return None

    def generate_url(self, instance, default=False):
        """
        devuelve la url con la publicacion de datos para una determinada
        instancia
        :param instance: es la instancia de la que se desea obtener la url
        :return: devuelve la url de la instancia
        """
        if default or not hasattr(instance, 'easydata_generate_url'):
            if self.entidad is None:
                return ""
            else:
                return reverse('easydata.views.publish.publish_model',
                               args=[self.aplicacion, self.entidad.nombre,
                                     self.nombre, quote(instance.pk),
                                     'xml'])
        else:
            return getattr(instance, 'easydata_generate_url')()

    def generate_url_without_instance(self):
        """
        devuelve la url para la publicacion de todos los datos del modelo
        :return: devuelve la url para el modelo
        """
        return mark_safe(u"easydata/publish/instance/" + self.aplicacion +
                         u"/" + self.entidad.nombre + "-" + self.nombre +
                         "/<b>pk</b>.(xml|nt|ttl)")

    def generate_full_url(self):
        """
        Devuelve una url de ejemplo donde podrian consultar los datos del
        modelo
        :return: devuelve url de ejemplo
        """
        if not self.entidad is None:
            return u"easydata/publish/model/" + self.aplicacion + \
                   u"/" + self.entidad.nombre + '-' + self.nombre + \
                   u".(xml|nt|ttl)"
        else:
            return u""

    def get_d2rq_url(self):
        """
        Devuelve url con la informacion de una instancia, en formato d2rq
        :return: devuelve cadena con url para d2rq
        """
        clase = self.devolver_modelo()
        url = getattr(clase, 'easydata_url_d2rq', None)

        if url is None:
            url = "easydata/publish/instance/" + self.aplicacion + "/" + \
                  self.entidad.nombre + "-" + self.nombre + "/@@%s.%s@@/"

            field_pk = getattr(clase, clase._meta.pk.name, None)

            if field_pk is None:
                url = url % (clase._meta.db_table, clase._meta.pk.name)
            else:
                identificador = clase._meta.pk.name + '_'
                identificador += field_pk.field.rel.to._meta.pk.name
                url = url % (clase._meta.db_table, identificador)

        return url

    class Meta:
        """Metadatos del modelo"""
        app_label = 'easydata'
        unique_together = ('nombre', 'aplicacion',)


class ModeloAdmin(admin.ModelAdmin):
    """Clase para registar en el admin de Django"""
    list_display = ['nombre', 'aplicacion']
    search_fields = ['nombre', 'aplicacion']


## Register in django.

admin.site.register(Modelo, ModeloAdmin)
