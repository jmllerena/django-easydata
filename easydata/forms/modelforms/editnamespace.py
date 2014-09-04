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
edicion de namespaces.
"""

from django.forms import ModelForm
from django import forms
from easydata.models import NameSpace
from django.utils.translation import ugettext_lazy as _

__author__ = 'llerena'


class EditNamespaceForm(ModelForm):
    """
    Este formulario se utiliza para la creacion de nuevos namespaces
    """
    namespace = forms.CharField(required=True,
                         widget=forms.TextInput(attrs={'class': 'form-control',
                                           'placeholder': 'Namespace name', }))

    short_name = forms.CharField(required=True,
                         widget=forms.TextInput(attrs={'class': 'form-control',
                             'placeholder': 'Short name for the namespace', }))

    url = forms.URLField(required=False,
            widget=forms.TextInput(attrs={'class': 'form-control',
                       'placeholder': 'Enter a valid url with a namespace', }))

    archivo = forms.FileField(label=_("File"),
                              required=False)

    formato = forms.ChoiceField(label=_("Format"),
                                choices=NameSpace.formatos,
                                initial='R',
                        widget=forms.Select(attrs={'class': 'form-control', }))

    class Meta:
        model = NameSpace
        fields = ['namespace', 'short_name']
