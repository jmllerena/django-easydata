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
En este modulo se almacena el formulario que se utiliza para realizar la
configuracion de visibilidad de los fields.
"""

from django.forms import ModelForm
from easydata.models import Field

__author__ = 'llerena'


class VisibilityFieldForm(ModelForm):
    """
    Este formulario se utiliza para realizar la configuracion de la visibilidad
    de los fields de la aplicacion.
    """
    class Meta:
        """
        Defino el modelo en que se basa y los campos que voy a utilizar
        """
        model = Field
        fields = ['visibilidad']

    def __init__(self, *args, **kwargs):
        super(VisibilityFieldForm, self).__init__(*args, **kwargs)
        self.fields['visibilidad'].label = self.instance.nombre
