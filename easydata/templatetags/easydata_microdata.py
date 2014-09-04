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
Este modulo contiene todos los template tags que permiten la insercion de los
datos referentes a una intancia concreta de un modelo haciendo uso de formato
microdata.
"""

from django import template
from django.utils.html import escape, mark_safe

from easydata.models import Field
from easydata.utils import get_model_assigned
from easydata.templatetags.get_data import get_instance_data

register = template.Library()


@register.simple_tag(name='microdata_div_meta')
def microdata_div_meta(token):
    """
    Generate the html with microdata using div and meta blocks
    :param token: is the instance to generate the microdata
    :return: HTML with the microdata tags and the instance's info
    """
    return generate_html_microdata(token, 'div', 'meta', True)


@register.simple_tag(name='microdata_div_span')
def microdata_div_span(token):
    """
    Generate the html with microdata using div and span blocks
    :param token: is the instance to generate the microdata
    :return: HTML with the microdata tags and the instance's info
    """
    return generate_html_microdata(token, 'div', 'span', False)


@register.simple_tag(name='microdata_ul')
def microdata_ul(token):
    """
    Generate the html with microdata using ul and li blocks
    :param token: is the instance to generate the microdata
    :return: HTML with the microdata tags and the instance's info
    """
    """
    Generate the html with microdata using ul and li blocks
    """
    return generate_html_microdata(token, 'ul', 'li', False)


@register.simple_tag(name='microdata_meta_field')
def microdata_meta_field(token, field):
    """
    Generate the html of a concrete field with microdata and using div and meta
    blocks
    :param token: is the instance to generate the microdata
    :param field: is the concrete field to generate the info
    :return: HTML with the microdata tags and the instance's info
    """
    return generate_html_microdata(token, 'div', 'meta', True, field)


@register.simple_tag(name='microdata_span_field')
def microdata_span_field(token, field):
    """
    Generate the html of a concrete field with microdata and using div and span
    blocks
    :param token: is the instance to generate the microdata
    :param field: is the concrete field to generate the info
    :return: HTML with the microdata tags and the instance's info
    """
    return generate_html_microdata(token, 'div', 'span', False, field)


@register.simple_tag(name='microdata_li_field')
def microdata_li_field(token, field):
    """
    Generate the html of a concrete field with microdata and using ul and li
    blocks
    :param token: is the instance to generate the microdata
    :param field: is the concrete field to generate the info
    :return: HTML with the microdata tags and the instance's info
    """
    return generate_html_microdata(token, 'ul', 'li', False, field)


def generate_html_microdata(instance, tag1, tag2, content, field=None):
    """
    Generate the html using the tags given
    :param instance: is the instance to generate the microdata
    :param tag1: the first tag to use
    :param tag2: the second tag to use
    :param field: is the concrete field to generate the info, if exists.
    :return: HTML with the microdata tags
    """
    datos = get_instance_data(instance, field)

    if not field is None:
        resultado = ''
    else:
        resultado = '<%s itemscope itemtype="%s" itemid="%s">\n' % (tag1,
                                                               datos['tipo_m'],
                                                               datos['uri'])

    for attr in datos['atributos']:
        if content:
            resultado += '<%s itemprop="%s" content="%s" ></%s>\n' % (
                         tag2,
                         escape(attr['nombre']),
                         escape(attr['content']),
                         tag2)
        else:
            resultado += '<%s itemprop="%s">%s</%s>\n' % (
                         tag2,
                         escape(attr['nombre']),
                         escape(attr['content']),
                         tag2)

    for rel in datos['relaciones']:
        resultado += '<link itemprop="%s" href="%s" />\n' % (
                     rel['itemprop'],
                     rel['resource'])

    if field is None:
        resultado += '</%s>\n' % tag1

    return mark_safe(resultado)


@register.tag('microdata_open_tag')
def microdata_open_tag(parser, token):
    """
    Generate the open html tag with namespaces declaration and the instace
    typeof in microdata format
    """
    try:
        tag_name, instance, etiqueta = token.split_contents()
        nodelist = parser.parse(('microdata_end_tag',))
        parser.delete_first_token()
    except ValueError:
        raise template.TemplateSyntaxError(
              "%r tag requires exactly two arguments" %
              token.contents.split()[0])

    return MicrodataOpenNode(instance, etiqueta, nodelist)


class MicrodataOpenNode(template.Node):
    def __init__(self, instancia, etiqueta, nodelist):
        self.instancia = template.Variable(instancia)
        self.etiqueta = etiqueta
        self.etiqueta = self.etiqueta.replace("\"", "")
        self.etiqueta = self.etiqueta.replace("'", "")
        self.nodelist = nodelist

    def render(self, context):
        try:
            token = self.instancia.resolve(context)

            datos = get_instance_data(token, None)

            resultado = '<%s itemscope itemtype="%s" itemid="%s">\n' % (
                                                               self.etiqueta,
                                                               datos['tipo_m'],
                                                               datos['uri'])

            resultado = mark_safe(resultado)
            resultado += self.nodelist.render(context)
            resultado += '</' + self.etiqueta + '>'

            return resultado
        except template.VariableDoesNotExist:
            return ''


@register.tag('microdata_open_tag_interno')
def microdata_open_tag_interno(parser, token):
    """
    Generate the open html tag with namespaces declaration and the instace
    typeof in microdata format
    """
    try:
        tag_name, padre, instance, field, etiqueta = token.split_contents()
        nodelist = parser.parse(('microdata_end_tag_interno',))
        parser.delete_first_token()
    except ValueError:
        raise template.TemplateSyntaxError(
              "%r tag requires exactly four arguments" %
              token.contents.split()[0])

    return MicrodataOpenInternoNode(padre, instance, field, etiqueta, nodelist)


class MicrodataOpenInternoNode(template.Node):
    def __init__(self, padre, instancia, field, etiqueta, nodelist):
        self.instancia = template.Variable(instancia)
        self.padre = template.Variable(padre)
        self.etiqueta = etiqueta
        self.etiqueta = self.etiqueta.replace("\"", "")
        self.etiqueta = self.etiqueta.replace("'", "")
        self.field = field
        self.field = self.field.replace("\"", "")
        self.field = self.field.replace("'", "")
        self.nodelist = nodelist

    def render(self, context):
        try:
            token = self.instancia.resolve(context)
            padre = self.padre.resolve(context)

            model = get_model_assigned(padre)

            fields = Field.objects.all()
            fields = fields.filter(modelo=model)
            fields = fields.filter(nombre=self.field)
            fields = fields.filter(visibilidad='V')
            fields = fields.exclude(propiedad=None)

            if fields.count() == 1:
                field = fields.get()
                datos = get_instance_data(token, None)

                resultado = '<%s itemscope itemprop="%s" itemtype="%s" '
                resultado += 'itemid="%s">\n'

                resultado = resultado % (self.etiqueta,
                                         field.propiedad.nombre,
                                         datos['tipo_m'],
                                         datos['uri'])

                resultado = mark_safe(resultado)
                resultado += self.nodelist.render(context)
                resultado += '</' + self.etiqueta + '>'

                return resultado
            else:
                return ''
        except template.VariableDoesNotExist:
            return ''
