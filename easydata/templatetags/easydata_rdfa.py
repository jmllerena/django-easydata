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
rdfa.
"""

from django import template
from django.utils.html import escape, mark_safe

from easydata.models import NameSpace, Field
from easydata.utils import get_model_assigned
from easydata.templatetags.get_data import get_instance_data

register = template.Library()


@register.simple_tag(name='rdfa_div')
def rdfa_div(token):
    """
    Generate the html with rdfa format using div blocks
    :param token: is the instance to generate the rdfa
    :return: HTML with the rdfa tags and the instance's info
    """
    return generate_html_rdfa(token, 'div', 'div', True)


@register.simple_tag(name='rdfa_div_span')
def rdfa_div_span(token):
    """
    Generate the html with rdfa format using div and span blocks
    :param token: is the instance to generate the rdfa
    :return: HTML with the rdfa tags and the instance's info
    """
    return generate_html_rdfa(token, 'div', 'span', False)


@register.simple_tag(name='rdfa_ul')
def rdfa_ul(token):
    """
    Generate the html with rdfa format using ul and li blocks
    :param token: is the instance to generate the rdfa
    :return: HTML with the rdfa tags and the instance's info
    """
    return generate_html_rdfa(token, 'ul', 'li', False)


@register.simple_tag(name='rdfa_div_field')
def rdfa_div_field(token, field):
    """
    Generate the html with rdfa format for a concrete field, using div blocks
    :param token: is the instance to generate the rdfa
    :param field: is the concrete field to generate the info
    :return: HTML with the rdfa tags and the instance's info
    """
    return generate_html_rdfa(token, 'div', 'div', True, field)


@register.simple_tag(name='rdfa_span_field')
def rdfa_span_field(token, field):
    """
    Generate the html with rdfa format for a concrete field, using div and span
    blocks
    :param token: is the instance to generate the rdfa
    :param field: is the concrete field to generate the info
    :return: HTML with the rdfa tags and the instance's info
    """
    return generate_html_rdfa(token, 'div', 'span', False, field)


@register.simple_tag(name='rdfa_li_field')
def rdfa_li_field(token, field):
    """
    Generate the html with rdfa format for a concrete field, using ul and li
    blocks
    :param token: is the instance to generate the rdfa
    :param field: is the concrete field to generate the info
    :return: HTML with the rdfa tags and the instance's info
    """
    return generate_html_rdfa(token, 'ul', 'li', False, field)


def generate_html_rdfa(instance, tag1, tag2, content, field=None):
    """
    Generate the html with the rdfa properties using the tags given
    :param instance: is the instance to generate the rdfa
    :param tag1: the first tag to use
    :param tag2: the second tag to use
    :return: HTML with the rdfa tags
    """
    datos = get_instance_data(instance, field)

    if not field is None:
        resultado = ""
    else:
        resultado = '<' + tag1 + ' prefix="'
        for name in NameSpace.objects.all():
            resultado += name.get_type() + ": " + name.get_url() + " "
        resultado += '" '

        resultado += 'typeof="%s" about="%s">\n' % (datos['tipo'],
                                                    datos['uri'])
    for attr in datos['atributos']:
        if content:
            resultado += '<%s property="%s" content="%s"></%s>\n' % (
                         tag2,
                         attr['property'],
                         escape(attr['content']),
                         tag2)
        else:
            resultado += '<%s property="%s">%s</%s>\n' % (
                         tag2,
                         attr['property'],
                         escape(attr['content']),
                         tag2)

    for rel in datos['relaciones']:
        resultado += '<link rel="%s" resource="%s" />\n' % (
                     rel['rel'],
                     rel['resource'])

    if field is None:
        resultado += '</%s>\n' % (tag1)

    return mark_safe(resultado)


@register.tag('rdfa_open_tag')
def rdfa_open_tag(parser, token):
    """
    Generate the open html tag with namespaces declaration and the instace
    typeof in rdfa format
    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, instance, etiqueta = token.split_contents()
        nodelist = parser.parse(('rdfa_end_tag',))
        parser.delete_first_token()
    except ValueError:
        raise template.TemplateSyntaxError(
              "%r tag requires exactly two arguments" %
              token.contents.split()[0])

    return RdfaOpenNode(instance, etiqueta, nodelist)


class RdfaOpenNode(template.Node):
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
            resultado = '<' + self.etiqueta
            resultado += ' prefix="'

            for name in NameSpace.objects.all():
                resultado += name.get_type() + ": " + name.get_url() + " "
            resultado += '" '

            resultado += 'typeof="%s" about="%s"' % (datos['tipo'],
                                                     datos['uri'])
            resultado += ">\n"

            resultado = mark_safe(resultado)
            resultado += self.nodelist.render(context)
            resultado += '</' + self.etiqueta + '>'

            return resultado
        except template.VariableDoesNotExist:
            return ''


@register.tag('rdfa_open_tag_interno')
def rdfa_open_tag_interno(parser, token):
    """
    Generate the open html tag with namespaces declaration and the instace
    typeof in rdfa format
    """
    try:
        tag_name, padre, instance, field, etiqueta = token.split_contents()
        nodelist = parser.parse(('rdfa_end_tag_interno',))
        parser.delete_first_token()
    except ValueError:
        raise template.TemplateSyntaxError(
              "%r tag requires exactly four arguments" %
              token.contents.split()[0])

    return RdfaOpenInternoNode(padre, instance, field, etiqueta, nodelist)


class RdfaOpenInternoNode(template.Node):
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

                resultado = '<div rel="%s">' % field.propiedad.get_full_name()
                resultado += '<' + self.etiqueta
                resultado += ' typeof="%s" about="%s"' % (
                                               datos['tipo'],
                                               datos['uri'])
                resultado += ">\n"

                resultado = mark_safe(resultado)
                resultado += self.nodelist.render(context)
                resultado += '</' + self.etiqueta + '></div>'

                return resultado
            else:
                return ''
        except template.VariableDoesNotExist:
            return ''
