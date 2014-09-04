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
En este modulo se define la funcion easydata_include_link la cual permite crear
enlaces html a los datos de instancias de modelos concretas.
"""

from django import template
from django.utils.html import mark_safe
from django.conf import settings

from easydata.utils import get_model_assigned


register = template.Library()


@register.simple_tag(name='easydata_include_link')
def easydata_include_link(elemento):
    """
    This tamplate tag get an instance element, and return a html a tag with the
    url where is published the information of the instance un RDF format.
    :param elemento: is the instance that you want to generate the link
    :return: HTML with the link to the RDF information of the elem
    """

    #Get the model
    model = get_model_assigned(elemento)

    if not model is None:
        # Get the url of the instance model
        url = model.generate_url(elemento, True)

        # Create the photo html tag
        foto = '<img alt="[RDF data]" src="' + settings.STATIC_URL + \
               'easydata/img/linked_logo.png" />'

        # Create the a tag with the url and the photo
        link = '<a href="' + url + '" target="_blank">' + foto + '</a>'

        return mark_safe(link)
    else:
        return ''
