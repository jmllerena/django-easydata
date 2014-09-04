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
En este fichero se han implementado los distintos test que se haran a la
aplicacion easydata, para poder comprobar en cierta medida que esta funciona
correctamente.
"""

from django.test import TestCase
from easydata.models import (Entidad, Propiedad, NameSpace, Modelo, Atributo,
                             Relacion)
from easydata.utils import (descubre_propiedades, get_model_assigned,
                            descubre_hijos, descubre_padres, inverse_relation)
from easydata.templatetags.easydata_links import easydata_include_link
from easydata.templatetags.easydata_microdata import microdata_div_meta
from easydata.templatetags.easydata_rdfa import rdfa_div


class NameSpaceTestCase(TestCase):
    """
    Esta clase de tests se encarga de probar el modelo NameSpace
    """
    def setUp(self):
        """
        Este metodo se encarga de preparar los datos para las pruebas
        """
        name = NameSpace(namespace="Test",
                         url="http://test.com/",
                         short_name="test")
        name.save()

    def test_namespace_save(self):
        """
        Se encarga de probar que los namespaces se crear correctamente
        """
        name = NameSpace.objects.all()

        self.assertEqual(name.count(), 1)

    def test_namespaces_name(self):
        """
        Se encarga de probar que se corresponde el atributo name con el
        indicado
        """
        name = NameSpace.objects.all()
        name = name.get()

        self.assertEqual(name.namespace, "Test")

    def test_namespace_url(self):
        """
        Se encarga de probar que se corresponde el atributo url con el indicado
        """
        name = NameSpace.objects.all()
        name = name.get()

        self.assertEqual(name.url, "http://test.com/")
        self.assertEqual(name.url, name.get_url())

    def test_namespace_shortname(self):
        """
        Se encarga de probar que se corresponde el atributo short_name con el
        indicado
        """
        name = NameSpace.objects.all()
        name = name.get()

        self.assertEqual(name.short_name, "test")
        self.assertEqual(name.short_name, name.get_type())


class EntidadTestCase(TestCase):
    """
    Esta clase de tests se encarga de probar el modelo Entidad
    """
    def setUp(self):
        """
        Este metodo se encarga de preparar los datos para las pruebas
        """
        name = NameSpace(namespace="Test",
                         url="http://test.com/",
                         short_name="test")
        name.save()
        Entidad.objects.create(nombre="test",
                            namespace=name,
                            descripcion="descripcion de un elemento de prueba",
                            etiqueta="etiqueta de prueba")

    def test_entidad_get_tag(self):
        """
        Se encarga de probar que se corresponde el atributo etiqueta con el
        indicado
        """
        ent = Entidad.objects.get(nombre="test")

        self.assertEqual(ent.etiqueta, "etiqueta de prueba")

    def test_entidad_get_description(self):
        """
        Se encarga de probar que se corresponde el atributo descripcion con el
        indicado
        """
        ent = Entidad.objects.get(nombre="test")

        self.assertEqual(ent.descripcion,
                         "descripcion de un elemento de prueba")

    def test_entidades_namespaces(self):
        """
        Se encarga de probar que se le ha asignado correctamente el namespace
        """
        name = NameSpace.objects.all()

        name = name.get()

        self.assertEqual(name.entidades.all().count(), 1)

    def test_entidad_get_type(self):
        """
        Se encarga de probar que funciona correctamente el metodo get_type
        """
        ent = Entidad.objects.get(nombre="test")

        self.assertEqual(ent.generate_type(), "http://test.com/test")

    def test_entidad_get_type_short(self):
        """
        Se encarga de probar que funciona correctamente el metodo
        get_type_short
        """
        ent = Entidad.objects.get(nombre="test")

        self.assertEqual(ent.generate_type_short(), "test:test")

    def test_entidad_get_publish_url(self):
        """
        Se encarga de probar que funciona correctamente el metodo
        get_publish_url
        """
        ent = Entidad.objects.get(nombre="test")

        self.assertEqual(ent.get_publish_url(),
                         "easydata/publish/type/test/test.(xml|nt|ttl)")


class PropiedadTestCase(TestCase):
    """
    Esta clase de tests se encarga de probar el modelo Propiedad
    """
    def setUp(self):
        """
        Este metodo se encarga de preparar los datos para las pruebas
        """
        name = NameSpace(namespace="Test",
                         url="http://test.com/",
                         short_name="test")
        name.save()
        ent = Entidad(nombre="test",
                      namespace=name,
                      descripcion="descripcion de un elemento de prueba",
                      etiqueta="etiqueta de prueba")
        ent.save()

        prop = Propiedad(nombre="proptest",
                         simple=True,
                         descripcion="desc test",
                         etiqueta="prop test",
                         namespace=name)

        prop.save()

        prop.entidades.add(ent)

    def test_propiedad_get_tag(self):
        """
        Este caso de prueba se encarga de probar la asignacion de etiquetas
        """
        prop = Propiedad.objects.get(nombre="proptest")

        self.assertEqual(prop.etiqueta, "prop test")

    def test_propiedad_get_description(self):
        """
        Este caso de prueba se encarga de probar la asignacion de una
        descripcion
        """
        prop = Propiedad.objects.get(nombre="proptest")

        self.assertEqual(prop.descripcion, "desc test")

    def test_get_propiedad_entidad(self):
        """
        Este caso de prueba se encarga de probar que las entidades relacionadas
        se asignan correctamente
        """
        ent = Entidad.objects.get(nombre="test")

        self.assertEqual(ent.propiedades.all().count(), 1)

        prop = ent.propiedades.all().get()

        self.assertIn(ent, prop.entidades.all())

    def test_get_propiedad_fullname(self):
        """
        Este caso de prueba se encarga de probar que el metodo get_full_name
        funciona correctamente
        """
        prop = Propiedad.objects.get(nombre="proptest")

        self.assertEqual(prop.get_full_name(), "test:proptest")


class ModeloTestCase(TestCase):
    """
    Esta clase de tests se encarga de probar el modelo Modelo
    """
    def setUp(self):
        """
        Este metodo se encarga de preparar los datos para las pruebas
        """
        # Create namespace
        name = NameSpace(namespace="Test",
                         url="http://test.com/",
                         short_name="test")
        name.save()

        # Create two entities
        ent1 = Entidad(nombre="father",
                      namespace=name,
                      descripcion="descripcion de un elemento de prueba 1",
                      etiqueta="etiqueta de prueba 1")
        ent1.save()

        ent2 = Entidad(nombre="son",
                      namespace=name,
                      descripcion="descripcion de un elemento de prueba 2",
                      etiqueta="etiqueta de prueba 2")
        ent2.save()

        # Create some properties
        prop1 = Propiedad(nombre="proptest1",
                         simple=True,
                         descripcion="desc test 1",
                         etiqueta="prop test 1",
                         namespace=name)

        prop1.save()
        prop1.entidades.add(ent1)

        prop2 = Propiedad(nombre="proptest2",
                         simple=True,
                         descripcion="desc test 2",
                         etiqueta="prop test 2",
                         namespace=name)

        prop2.save()
        prop2.entidades.add(ent1)

        prop3 = Propiedad(nombre="proptest3",
                         simple=True,
                         descripcion="desc test 3",
                         etiqueta="prop test 3",
                         namespace=name)
        prop3.save()
        prop3.entidades.add(ent2)
        prop3.tipo.add(ent2)
        prop3.save()

        mod = Modelo(nombre="Propiedad", aplicacion="easydata",
                     visibilidad='V', entidad=ent2)
        mod.save()

    def test_devolver_modelo(self):
        mod = Modelo.objects.filter(nombre="Propiedad", aplicacion="easydata")
        mod = mod.get()

        self.assertIsNotNone(mod.devolver_modelo())

    def test_generate_url(self):
        mod = Modelo.objects.filter(nombre="Propiedad", aplicacion="easydata")
        mod = mod.get()
        prop = Propiedad.objects.all().filter(nombre="proptest1")[0]

        self.assertEqual(mod.generate_url(prop),
                         '/easydata/publish/instance/easydata/son-Propiedad/' +
                         str(prop.pk) + '.xml')

    def test_generate_url_without_instance(self):
        mod = Modelo.objects.filter(nombre="Propiedad", aplicacion="easydata")
        mod = mod.get()

        self.assertEqual(mod.generate_url_without_instance(),
                         'easydata/publish/instance/easydata/son-Propiedad/' +
                         '<b>pk</b>.(xml|nt|ttl)')

    def test_generate_full_url(self):
        mod = Modelo.objects.filter(nombre="Propiedad", aplicacion="easydata")
        mod = mod.get()

        self.assertEqual(mod.generate_full_url(),
                         'easydata/publish/model/easydata/son-Propiedad.(xml' +
                         '|nt|ttl)')

    def test_get_d2rq_url(self):
        mod = Modelo.objects.filter(nombre="Propiedad", aplicacion="easydata")
        mod = mod.get()

        self.assertEqual(mod.get_d2rq_url(),
                         'easydata/publish/instance/easydata/son-Propiedad' +
                         '/@@easydata_propiedad.id@@/')


class UtilsTestCase(TestCase):
    """
    Esta clase de test se encarga de realizar las pruebas pertinentes de los
    diferentes utils implementados para la aplicacion easydata.
    """
    def setUp(self):
        """
        Este metodo se encarga de preparar los datos para las pruebas
        """
        # Create namespace
        name = NameSpace(namespace="Test",
                         url="http://test.com/",
                         short_name="test")
        name.save()

        # Create two entities
        ent1 = Entidad(nombre="father",
                      namespace=name,
                      descripcion="descripcion de un elemento de prueba 1",
                      etiqueta="etiqueta de prueba 1")
        ent1.save()

        ent2 = Entidad(nombre="son",
                      namespace=name,
                      descripcion="descripcion de un elemento de prueba 2",
                      etiqueta="etiqueta de prueba 2")
        ent2.save()

        # Create some properties
        prop1 = Propiedad(nombre="proptest1",
                         simple=True,
                         descripcion="desc test 1",
                         etiqueta="prop test 1",
                         namespace=name)

        prop1.save()
        prop1.entidades.add(ent1)

        prop2 = Propiedad(nombre="proptest2",
                         simple=True,
                         descripcion="desc test 2",
                         etiqueta="prop test 2",
                         namespace=name)

        prop2.save()
        prop2.entidades.add(ent1)

        prop3 = Propiedad(nombre="proptest3",
                         simple=True,
                         descripcion="desc test 3",
                         etiqueta="prop test 3",
                         namespace=name)
        prop3.save()
        prop3.entidades.add(ent2)
        prop3.tipo.add(ent2)
        prop3.save()

        mod1 = Modelo(nombre="Propiedad", aplicacion="easydata",
                     visibilidad='V', entidad=ent2)

        mod2 = Modelo(nombre="Entidad", aplicacion="easydata",
                     visibilidad='V', entidad=ent2)

        mod1.save()
        mod2.save()

        rel1 = Relacion(nombre="entidades", modelo=mod1,
                        modelo_relacionado=mod2, visibilidad="V",
                        tipo_relacion="M")
        rel2 = Relacion(nombre="propiedades", modelo=mod2,
                        modelo_relacionado=mod1, visibilidad="V",
                        tipo_relacion="M")

        rel1.save()
        rel2.save()

    def test_descubre_propiedades(self):
        """
        Caso de prueba para el metodo descubre_propiedades
        """
        ent1 = Entidad.objects.get(nombre="father")
        ent2 = Entidad.objects.get(nombre="son")

        propiedades_ent1 = descubre_propiedades(ent1)
        propiedades_ent1_complex = descubre_propiedades(ent1, False)
        propiedades_ent2 = descubre_propiedades(ent2)
        propiedades_ent2_complex = descubre_propiedades(ent2, False)

        self.assertEqual(propiedades_ent1.count(), 2)
        self.assertEqual(propiedades_ent1_complex.count(), 0)
        self.assertEqual(propiedades_ent2.count(), 1)
        self.assertEqual(propiedades_ent2_complex.count(), 1)

        # Set ent1 as father of ent2
        ent2.padres.add(ent1)
        ent2.save()

        propiedades_ent2 = descubre_propiedades(ent2)
        propiedades_ent2_complex = descubre_propiedades(ent2, False)
        self.assertEqual(propiedades_ent2.count(), 3)
        self.assertEqual(propiedades_ent2_complex.count(), 1)

    def test_descubre_padres_hijos(self):
        """
        Este caso de prueba se encarga de que los utils descubre_padres y
        descubre_hijos detectan perfectamente las entidades padre y entidades
        hijas de una determinada entidad
        """
        ent1 = Entidad.objects.get(nombre="father")
        ent2 = Entidad.objects.get(nombre="son")

        # Set ent1 as father of ent2
        ent2.padres.add(ent1)
        ent2.save()

        # Comprobar que tiene a su padre
        padres_ent2 = descubre_padres(ent2)
        self.assertIn(ent1, padres_ent2)

        # Comprobar que tiene a su hijo
        hijos_ent1 = descubre_hijos(ent1)
        self.assertIn(ent2, hijos_ent1)

    def test_get_model_assigned(self):
        """
        Este caso de prueba se encarga de el util get_model_assigned devuelve
        correctamente el modelo con el que se corresponde una determinada
        instancia
        """
        ent = Modelo.objects.all()[0]
        prop = Propiedad.objects.get(nombre="proptest3")

        model_assigned_ent = get_model_assigned(ent)
        self.assertIsNone(model_assigned_ent)

        model_assigned_prop = get_model_assigned(prop)
        self.assertIsInstance(model_assigned_prop, Modelo)

        self.assertRaises(AttributeError, get_model_assigned, ["fail", ])

    def test_inverse_relation(self):
        """
        Este caso de prueba se encarga de que util inverse_relation devuelva
        correctamente la relacion inversa a una relacion dada
        """
        rel1 = Relacion.objects.all()[0]
        rel2 = Relacion.objects.all()[1]

        inverse2 = inverse_relation(rel1)
        inverse1 = inverse_relation(rel2)

        # Comprueba que los inversos devueltos son los correctos
        self.assertEqual(rel1, inverse1)
        self.assertEqual(rel2, inverse2)


class TemplateTagsTestCase(TestCase):
    """
    Esta clase de tests, se encarga de agrupar todos los tests referentes a los
    template tags implementados para la aplicacion easydata.
    """
    def setUp(self):
        """
        Este metodo se encarga de preparar los datos para las pruebas
        """
        # Create namespace
        name = NameSpace(namespace="Test",
                         url="http://test.com/",
                         short_name="test")
        name.save()

        # Create two entities
        ent1 = Entidad(nombre="father",
                       namespace=name,
                       descripcion="descripcion de un elemento de prueba 1",
                       etiqueta="etiqueta de prueba 1")
        ent1.save()

        ent2 = Entidad(nombre="son",
                       namespace=name,
                       descripcion="descripcion de un elemento de prueba 2",
                       etiqueta="etiqueta de prueba 2")
        ent2.save()

        # Create some properties
        prop1 = Propiedad(nombre="proptest1",
                          simple=True,
                          descripcion="desc test 1",
                          etiqueta="prop test 1",
                          namespace=name)

        prop1.save()
        prop1.entidades.add(ent1)

        prop2 = Propiedad(nombre="proptest2",
                          simple=True,
                          descripcion="desc test 2",
                          etiqueta="prop test 2",
                          namespace=name)

        prop2.save()
        prop2.entidades.add(ent1)

        prop3 = Propiedad(nombre="proptest3",
                          simple=True,
                          descripcion="desc test 3",
                          etiqueta="prop test 3",
                          namespace=name)
        prop3.save()
        prop3.entidades.add(ent2)
        prop3.tipo.add(ent2)
        prop3.save()

        mod = Modelo(nombre="Propiedad", aplicacion="easydata",
                     visibilidad='V', entidad=ent2)
        mod.save()

        atri = Atributo(nombre="nombre", modelo=mod, visibilidad='V',
                        propiedad=prop3, tipo_field="CharField")
        atri.save()

    def test_microdata(self):
        """
        Este caso de prueba se encarga de comprobar que el codigo microdata
        generado por un template tag es correcto
        """
        mod = Modelo.objects.all().get()
        prop = Propiedad.objects.all().filter(nombre="proptest1")[0]

        self.assertEqual(microdata_div_meta(mod),
                         '<div itemscope itemtype="" itemid="">\n</div>\n')

        self.assertEqual(microdata_div_meta(prop),
                         '<div itemscope itemtype="http://test.com/son" item' +
                         'id="http://example.com/easydata/publish/instance/e' +
                         'asydata/son-Propiedad/' + str(prop.pk) + '.xml">\n' +
                         '<meta itemprop="http://test.com/proptest3" content' +
                         '="proptest1" ></meta>\n</div>\n')

    def test_rdfa(self):
        """
        Este caso de prueba se encarga de comprobar que el codigo rdfa generado
        por un template tag es correcto
        """
        mod = Modelo.objects.all().get()
        prop = Propiedad.objects.all().filter(nombre="proptest1")[0]

        self.assertEqual(rdfa_div(mod),
                         '<div prefix="test: h' +
                         'ttp://test.com/ " typeof="" about="">\n</div>\n')

        self.assertEqual(rdfa_div(prop),
                         '<div prefix="test: http://test.com/ " typeof="test' +
                         ':son" about="http://example.com/easydata/publish/i' +
                         'nstance/easydata/son-Propiedad/' + str(prop.pk) +
                         '.xml">\n<div property="test:proptest3" content="pr' +
                         'optest1"></div>\n</div>\n')

    def test_links(self):
        """
        Este caso de prueba se encarga de comprobar que el enlace generado para
        una determinada instancia es correcto
        """
        from django.conf import settings

        mod = Modelo.objects.all().get()
        prop = Propiedad.objects.all().filter(nombre="proptest1")[0]

        self.assertEqual(easydata_include_link(mod), '')

        self.assertEqual(easydata_include_link(prop),
                         '<a href="/easydata/publish/instance/easydata/' +
                         mod.entidad.nombre + '-Propiedad/' + str(prop.pk) +
                         '.xml" target="_blank"><img alt="[RDF data]" src="' +
                         settings.STATIC_URL + 'easydata/img/linked_logo.png' +
                         '" /></a>')
