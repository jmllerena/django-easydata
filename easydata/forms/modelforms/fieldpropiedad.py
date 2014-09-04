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
En este modulo se almacena el formulario que se utiliza para realizar el mapeo
de los fields con las propiedades existentes.
"""

from django.forms import ModelForm
from django import forms
from django.utils.html import escape
from easydata.models import Field, Propiedad, Atributo, NameSpace
from easydata.utils import descubre_propiedades, descubre_padres

__author__ = 'llerena'


class SelectProperties(forms.Select):
    """
    Creacion de widget propio para que incluya en cada uno de los options del
    select, la etiqueta y la descripcion de la propiedad concreta
    """
    def render_option(self, selected_choices, option_value, option_label):

        option = u'<option'

        if str(option_value) in selected_choices:
            option += u' selected="selected"'

        option += u' value=' + str(option_value)

        #Get the Property
        if not option_value is None and option_value != '':
            property_instance = Propiedad.objects.get(pk=option_value)
            try:
                if property_instance.descripcion is None or \
                   property_instance.descripcion == '':
                    option += u' title=' + u'"' + \
                              escape(property_instance.etiqueta) + \
                              u': ' + u'Without descripcion"'
                else:
                    option += u' title=' + u'"' + \
                              escape(property_instance.etiqueta) + \
                              u': ' + escape(property_instance.descripcion) + \
                              u'"'
            except TypeError:
                pass

        option += u'>' + option_label + u'</option>'

        return option


class FieldPropiedadForm(ModelForm):
    """
    Este formulario se encarga de realizar el mapeo de los fields con las
    propiedades de los namespaces
    """
    namespace = forms.ModelChoiceField(queryset=NameSpace.objects.all()
                                                 .order_by('namespace'),
                                       empty_label="----------",
                                       required=False)

    propiedad = forms.ModelChoiceField(queryset=Propiedad.objects.all()
                                                .order_by('nombre'),
                                       empty_label="----------",
                                       required=False,
                                       widget=SelectProperties())

    class Meta:
        """
        Defino el modelo en que se basa y los campos que voy a utilizar
        """
        model = Field
        fields = ['propiedad']

    def __init__(self, *args, **kwargs):
        super(FieldPropiedadForm, self).__init__(*args, **kwargs)

        ent = self.instance.modelo.entidad

        if not ent is None:
            self.fields['namespace'].empty_label = ent.namespace.namespace + \
                                                   u" : " + ent.nombre

        self.fields['propiedad'].label = self.instance.nombre
        name_data = self.data.get(self.prefix + "-namespace", None)
        prop_data = self.data.get(self.prefix + "-propiedad", None)

        if not name_data is None:
            try:
                name_data = int(name_data)
            except ValueError:
                name_data = None

        if not prop_data is None:
            try:
                prop_data = int(prop_data)
            except ValueError:
                prop_data = None

        if isinstance(self.instance, Atributo):
            if name_data is None:
                queryset = descubre_propiedades(self.instance.modelo.entidad)

                if prop_data is None and \
                   not self.instance.propiedad is None and \
                   not self.instance.propiedad in queryset:
                    name = self.instance.propiedad.namespace
                    self.fields['namespace'].initial = \
                                              self.instance.propiedad.namespace
                    queryset = name.propiedades.all()
                    queryset = queryset.filter(pk=self.instance.propiedad.pk)

            else:
                namespace = NameSpace.objects.get(pk=name_data)
                queryset = namespace.propiedades.all()
                if not prop_data is None:
                    queryset = queryset.filter(pk=prop_data)
        else:  # Caso de ser una relacion
            tipo_modelo_rel = self.instance.modelo_relacionado.entidad
            if name_data is None:
                queryset = descubre_propiedades(self.instance.modelo.entidad,
                                                False)

                padres = descubre_padres(tipo_modelo_rel)
                padres.add(tipo_modelo_rel)
                queryset = queryset.filter(tipo__in=padres)
                queryset = queryset.order_by('nombre')

                if queryset.count() == 0:
                    queryset = Propiedad.objects.none()

                if prop_data is None and \
                   not self.instance.propiedad is None and \
                   not self.instance.propiedad in queryset:
                    name = self.instance.propiedad.namespace
                    self.fields['namespace'].initial = \
                                              self.instance.propiedad.namespace
                    queryset = name.propiedades.all()
                    queryset = queryset.filter(pk=self.instance.propiedad.pk)
            else:
                namespace = NameSpace.objects.get(pk=name_data)

                self.fields['namespace'].initial = namespace
                queryset = namespace.propiedades.all()
                if not prop_data is None:
                    queryset = queryset.filter(pk=prop_data)

        queryset = queryset.order_by('nombre')

        self.fields['propiedad'].queryset = queryset

    def save(self, *args, **kwargs):
        """
        Sobreescribo el metodo save para que al salvar la instancia, se cargue
        el field de propiedad con el queryset adecuado
        """
        super(FieldPropiedadForm, self).save(*args, **kwargs)

        if self.instance.propiedad is None:
            if isinstance(self.instance, Atributo):
                queryset = descubre_propiedades(self.instance.modelo.entidad)
                queryset = queryset.order_by('nombre')
                self.fields['propiedad']._set_queryset(queryset)
            else:
                tipo_modelo_rel = self.instance.modelo_relacionado.entidad
                queryset = descubre_propiedades(self.instance.modelo.entidad,
                                                False)

                padres = descubre_padres(tipo_modelo_rel)
                padres.add(tipo_modelo_rel)
                queryset = queryset.filter(tipo__in=padres)
                queryset = queryset.order_by('nombre')

                if queryset.count() == 0:
                    queryset = Propiedad.objects.none()
                self.fields['propiedad']._set_queryset(queryset)
