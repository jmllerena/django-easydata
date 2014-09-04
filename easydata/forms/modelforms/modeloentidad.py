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
de los modelos con las entidades existentes.
"""

from django.forms import ModelForm
from django import forms
from easydata.models import Modelo, Entidad, NameSpace

__author__ = 'llerena'


class SelectEntities(forms.Select):
    """
    Creacion de widget propio para que incluya en cada uno de los options del
    select, la etiqueta y la descripcion de la entidad concreta
    """
    def render_option(self, selected_choices, option_value, option_label):

        option = u'<option'

        if str(option_value) in selected_choices:
            option += u' selected="selected"'

        option += u' value=' + str(option_value)

        #Get the Entity
        if not option_value is None and option_value != '':
            entity_instance = Entidad.objects.get(pk=option_value)
            try:
                if entity_instance.descripcion is None or \
                   entity_instance.descripcion == '':
                    option += u' title=' + u'"' + entity_instance.etiqueta + \
                              u': ' + u'Without descripcion"'
                else:
                    option += u' title=' + u'"' + entity_instance.etiqueta + \
                              u': ' + \
                              entity_instance.descripcion + u'"'
            except TypeError:
                pass

        option += u'>' + option_label + u'</option>'

        return option


class ModeloEntidadForm(ModelForm):
    """
    Este formulario se encarga de realizar el mapeo de los modelos con las
    entidades de los namespaces
    """
    namespace = forms.ModelChoiceField(queryset=NameSpace.objects.all()
                                                .order_by('namespace'),
                                       empty_label="----------",
                                       required=False)

    entidad = forms.ModelChoiceField(queryset=Entidad.objects.all()
                                              .order_by('nombre'),
                                     empty_label="----------",
                                     required=False,
                                     widget=SelectEntities())

    class Meta:
        """
        Defino el modelo en que se basa y los campos que voy a utilizar
        """
        model = Modelo
        fields = ['entidad']

    def __init__(self, *args, **kwargs):
        super(ModeloEntidadForm, self).__init__(*args, **kwargs)
        name_data = self.data.get(self.prefix + "-namespace", None)
        ent_data = self.data.get(self.prefix + "-entidad", None)

        if not name_data is None:
            try:
                name_data = int(name_data)
                ent_data = int(ent_data)
            except ValueError:
                name_data = None
                ent_data = None

        if name_data is None:
            if not self.instance.entidad is None:
                self.fields['namespace'].initial = \
                                                self.instance.entidad.namespace

                entidades_queryset = Entidad.objects.all()
                entidades_queryset = entidades_queryset.filter(
                                     pk=self.instance.entidad.pk)
                entidades_queryset = entidades_queryset.order_by('nombre')

                self.fields['entidad']._set_queryset(entidades_queryset)
            elif self.instance.entidad is None:
                self.fields['entidad']._set_queryset(Entidad.objects.none())
        else:
            if ent_data is None:
                entidades_queryset = Entidad.objects.none()
            else:
                namespace = NameSpace.objects.get(pk=name_data)

                self.fields['namespace'].initial = namespace

                entidades_queryset = Entidad.objects.all()
                entidades_queryset = entidades_queryset.filter(pk=ent_data)

            self.fields['entidad']._set_queryset(entidades_queryset)

    def save(self, *args, **kwargs):
        super(ModeloEntidadForm, self).save(*args, **kwargs)

        if self.cleaned_data.get('namespace', None) is None or \
           self.cleaned_data.get('entidad', None) is None:
            self.fields['namespace'].initial = None
            self.fields['entidad']._set_queryset(Entidad.objects.none())

    def clean(self):
        cleaned = self.cleaned_data

        ent = cleaned.get('entidad', None)
        name = cleaned.get('namespace', None)

        if not name is None and not ent is None and \
           not ent in name.entidades.all():
            raise forms.ValidationError("The entities don't correspond " +
                                        "with the namespaces.")
        return cleaned
