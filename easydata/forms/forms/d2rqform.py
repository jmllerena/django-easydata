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
Este modulo implementa el formulario para captar ficheros d2rq y modificarlos
mismos con la configuracion de la aplicacion
"""

from django import forms

__author__ = 'llerena'


class D2RqForm(forms.Form):
    """
    Este formulario se utiliza para captar un fichero del tipo D2Rq de tal
    forma que se modifique esta añadiendosele el etiquetado configurado en la
    aplicacion
    """
    archivo = forms.FileField(required=True)
