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
En este modulo se almacena la version de Parseador, que se encarga de realizar
el parseo de los datos a partir de ficheros RDF, tanto en formato XML como
Ntriples
"""

#Imported from Python
import rdflib
import urlparse

#Importado de la aplicacion
from easydata.parsing.parseador import Parser
from easydata.parsing.registers import RegisterEntity, RegisterProperty

__author__ = 'llerena'


class ParserXML(Parser):
    """
    This class parse a schema ontology from a XML file.
    """
    def __init__(self, file, namespace):
        super(ParserXML, self).__init__()

        #Load the graph from de file
        self.grafo = rdflib.Graph()
        self.grafo.parse(file, format="xml")
        self.grafo.bind('owl', 'http://www.w3.org/2002/07/owl#')
        self.grafo.bind('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.grafo.bind('rdfs', 'http://www.w3.org/2000/01/rdf-schema#')
        self.grafo.bind('vann', 'http://purl.org/vocab/vann/')

        #Initialize the list to store the entities and properties
        self.list_entities = list()
        self.list_properties = list()

        #Initialize namespace
        self.namespace = namespace

    def parse(self):
        """
        Este metodo se encarga de realizar el parseo de un namespace en el
        formato RDF
        """
        # Captamos la url del namespace
        if self.namespace.url is None or self.namespace.url == "":
            # Get the url of the ontology
            resultado = self.grafo.query(
                       """SELECT DISTINCT ?onto ?url
                          WHERE {
                             ?onto rdf:type owl:Ontology .
                             ?onto vann:preferredNamespaceUri ?url .
                       }""")

            for row in resultado:
                url = row[1]
                if str(url) == 'http://schema.rdfs.org/all':
                    url = 'http://schema.org/'
                try:
                    parts = urlparse.urlsplit(str(url))
                    if parts.scheme or parts.netloc:
                        # rfc3987.parse(url, rule="IRI")
                        if not url.endswith("/") and not url.endswith("#"):
                            url += '#'
                        if self.namespace.url is None or \
                           self.namespace.url == "":
                            self.namespace.url = str(url)
                            self.namespace.save()
                except ValueError:
                    pass  # URL no valida

            # Get the url of the ontology
            resultado = self.grafo.query(
                       """SELECT DISTINCT ?onto
                          WHERE {
                             ?onto rdf:type owl:Ontology .
                       }""")

            for row in resultado:
                url = row[0]
                if str(url) == 'http://schema.rdfs.org/all':
                    url = 'http://schema.org/'
                try:
                    parts = urlparse.urlsplit(str(url))
                    if parts.scheme or parts.netloc:
                        # rfc3987.parse(url, rule="IRI")
                        if not url.endswith("/") and not url.endswith("#"):
                            url += '#'
                        if self.namespace.url is None or \
                           self.namespace.url == "":
                            self.namespace.url = str(url)
                            self.namespace.save()
                except ValueError:
                    pass  # URL no valida

        #Captamos todas las clases
        resultado = self.grafo.query(
   """SELECT DISTINCT ?clase
      WHERE {
         { ?clase rdf:type rdfs:Class } UNION { ?clase rdf:type owl:Class } .
   }""")

        datos = dict()

        #Inicializamos diccionario y almacenamos las clases
        for row in resultado:
            if "#" in row[0]:
                clase = row[0].split("#")[-1]
            elif "/" in row[0]:
                clase = row[0].split("/")[-1]
            else:
                clase = row[0]
            if not clase in datos.keys():
                datos[clase] = dict()
            if row[0].replace(clase, "") == self.namespace.url:
                datos[clase]['url'] = row[0].replace(clase, "")
            elif not 'url' in datos[clase].keys():
                datos[clase]['url'] = ""
            datos[clase]['label'] = ""
            datos[clase]['comment'] = ""
            datos[clase]['padres'] = list()

        #Captamos las etiquetas de cada clase
        resultado = self.grafo.query(
     """SELECT DISTINCT ?clase ?etiqueta
        WHERE {
           { ?clase rdf:type rdfs:Class } UNION { ?clase rdf:type owl:Class } .
           ?clase rdfs:label ?etiqueta .
           FILTER(LANG(?etiqueta) = "" || LANGMATCHES(LANG(?etiqueta), "en")) .
     }""")

        for row in resultado:
            if "#" in row[0]:
                clase = row[0].split("#")[-1]
            elif "/" in row[0]:
                clase = row[0].split("/")[-1]
            else:
                clase = row[0]
            datos[clase]['label'] = unicode(row[1])

        #Captamos las etiquetas de cada clase (otros idiomas)
        resultado = self.grafo.query(
     """SELECT DISTINCT ?clase ?etiqueta
        WHERE {
           { ?clase rdf:type rdfs:Class } UNION { ?clase rdf:type owl:Class } .
           ?clase rdfs:label ?etiqueta .
     }""")

        for row in resultado:
            if "#" in row[0]:
                clase = row[0].split("#")[-1]
            elif "/" in row[0]:
                clase = row[0].split("/")[-1]
            else:
                clase = row[0]
            if datos[clase]['label'] == "":
                datos[clase]['label'] = unicode(row[1])

        # Captamos los comentarios
        resultado = self.grafo.query(
 """SELECT DISTINCT ?clase ?comentario
    WHERE {
       { ?clase rdf:type rdfs:Class } UNION { ?clase rdf:type owl:Class } .
       ?clase rdfs:comment ?comentario .
       FILTER(LANG(?comentario) = "" || LANGMATCHES(LANG(?comentario), "en")) .
 }""")

        for row in resultado:
            if "#" in row[0]:
                clase = row[0].split("#")[-1]
            elif "/" in row[0]:
                clase = row[0].split("/")[-1]
            else:
                clase = row[0]
            datos[clase]['comment'] = unicode(row[1])

        # Captamos los comentarios
        resultado = self.grafo.query(
 """SELECT DISTINCT ?clase ?comentario
    WHERE {
       { ?clase rdf:type rdfs:Class } UNION { ?clase rdf:type owl:Class } .
       ?clase rdfs:comment ?comentario .
 }""")

        for row in resultado:
            if "#" in row[0]:
                clase = row[0].split("#")[-1]
            elif "/" in row[0]:
                clase = row[0].split("/")[-1]
            else:
                clase = row[0]
            if datos[clase]['comment'] == "":
                datos[clase]['comment'] = unicode(row[1])

        # Buscamos los padres de cada clase
        resultado = self.grafo.query(
   """SELECT DISTINCT ?clase ?padre
      WHERE {
         { ?clase rdf:type rdfs:Class } UNION { ?clase rdf:type owl:Class } .
         ?clase rdfs:subClassOf ?padre .
   }""")

        for row in resultado:
            registro = dict()
            if "#" in row[0]:
                clase = row[0].split("#")[-1]
            elif "/" in row[0]:
                clase = row[0].split("/")[-1]
            else:
                clase = row[0]

            if "#" in row[1]:
                padre = row[1].split("#")[-1]
            elif "/" in row[1]:
                padre = row[1].split("/")[-1]
            else:
                padre = row[1]

            registro['name'] = padre
            registro['url'] = row[1].replace(padre, "")

            datos[clase]['padres'].append(registro)

        #Se salvan los registros de entidades
        for key in datos.keys():
            self.list_entities.append(RegisterEntity(key,
                                                     datos[key][u'comment'],
                                                     datos[key][u'label'],
                                                     self.namespace,
                                                     datos[key][u'padres'],
                                                     datos[key]['url']))

        #######################################################################
        #  Captacion de las propiedades                                       #
        #######################################################################

        #Captamos las propiedades (rdf:Property)
        resultado = self.grafo.query(
                   """SELECT DISTINCT ?propiedad
                      WHERE {
                         { ?propiedad rdf:type rdf:Property } UNION
                         { ?propiedad rdf:type owl:ObjectProperty } UNION
                         { ?propiedad rdf:type owl:DatatypeProperty } UNION
                         { ?propiedad rdf:type owl:AnnotationProperty } .
                   }""")

        datos = dict()
        for row in resultado:
            if "#" in row[0]:
                prop = row[0].split("#")[-1]
            elif "/" in row[0]:
                prop = row[0].split("/")[-1]
            else:
                prop = row[0]
            if not prop in datos.keys():
                datos[prop] = dict()
            if row[0].replace(prop, "") == self.namespace.url:
                datos[prop]['url'] = row[0].replace(prop, "")
            elif not 'url' in datos[prop].keys():
                datos[prop]['url'] = ""
            datos[prop]['label'] = ""
            datos[prop]['comment'] = ""
            datos[prop]['domain'] = list()
            datos[prop]['ranges'] = list()

        #Captamos las etiquetas de cada propiedad (rdf:Property)
        resultado = self.grafo.query(
     """SELECT DISTINCT ?propiedad ?etiqueta
        WHERE {
           { ?propiedad rdf:type rdf:Property } UNION
           { ?propiedad rdf:type owl:ObjectProperty } UNION
           { ?propiedad rdf:type owl:DatatypeProperty } UNION
           { ?propiedad rdf:type owl:AnnotationProperty } .
           ?propiedad rdfs:label ?etiqueta .
           FILTER(LANG(?etiqueta) = "" || LANGMATCHES(LANG(?etiqueta), "en")) .
     }""")

        for row in resultado:
            if "#" in row[0]:
                prop = row[0].split("#")[-1]
            elif "/" in row[0]:
                prop = row[0].split("/")[-1]
            else:
                prop = row[0]
            datos[prop]['label'] = unicode(row[1])

        #Captamos las etiquetas de cada propiedad (rdf:Property)
        resultado = self.grafo.query(
     """SELECT DISTINCT ?propiedad ?etiqueta
        WHERE {
           { ?propiedad rdf:type rdf:Property } UNION
           { ?propiedad rdf:type owl:ObjectProperty } UNION
           { ?propiedad rdf:type owl:DatatypeProperty } UNION
           { ?propiedad rdf:type owl:AnnotationProperty } .
           ?propiedad rdfs:label ?etiqueta .
     }""")

        for row in resultado:
            if "#" in row[0]:
                prop = row[0].split("#")[-1]
            elif "/" in row[0]:
                prop = row[0].split("/")[-1]
            else:
                prop = row[0]
            if datos[prop]['label'] == "":
                datos[prop]['label'] = unicode(row[1])

        #Captamos los comentarios (rdf:Property)
        resultado = self.grafo.query(
 """SELECT DISTINCT ?propiedad ?comentario
    WHERE {
       { ?propiedad rdf:type rdf:Property } UNION
       { ?propiedad rdf:type owl:ObjectProperty } UNION
       { ?propiedad rdf:type owl:DatatypeProperty } UNION
       { ?propiedad rdf:type owl:AnnotationProperty } .
       ?propiedad rdfs:comment ?comentario .
       FILTER(LANG(?comentario) = "" || LANGMATCHES(LANG(?comentario), "en")) .
 }""")

        for row in resultado:
            if "#" in row[0]:
                prop = row[0].split("#")[-1]
            elif "/" in row[0]:
                prop = row[0].split("/")[-1]
            else:
                prop = row[0]
            datos[prop]['comment'] = unicode(row[1])

        #Captamos los comentarios (rdf:Property)
        resultado = self.grafo.query(
 """SELECT DISTINCT ?propiedad ?comentario
    WHERE {
       { ?propiedad rdf:type rdf:Property } UNION
       { ?propiedad rdf:type owl:ObjectProperty } UNION
       { ?propiedad rdf:type owl:DatatypeProperty } UNION
       { ?propiedad rdf:type owl:AnnotationProperty } .
       ?propiedad rdfs:comment ?comentario .
 }""")

        for row in resultado:
            if "#" in row[0]:
                prop = row[0].split("#")[-1]
            elif "/" in row[0]:
                prop = row[0].split("/")[-1]
            else:
                prop = row[0]
            if datos[prop]['comment'] == "":
                datos[prop]['comment'] = unicode(row[1])

        #Captamos el dominio de cada propiedad
        resultado = self.grafo.query(
           """SELECT DISTINCT ?propiedad ?dominio
              WHERE {
                 { ?propiedad rdf:type rdf:Property } UNION
                 { ?propiedad rdf:type owl:ObjectProperty } UNION
                 { ?propiedad rdf:type owl:DatatypeProperty } UNION
                 { ?propiedad rdf:type owl:AnnotationProperty } .
                 ?propiedad rdfs:domain ?dominio .
           }""")

        #Almacenamos los dominios de las propiedades
        for row in resultado:
            registro = dict()

            if "#" in row[0]:
                prop = row[0].split("#")[-1]
            elif "/" in row[0]:
                prop = row[0].split("/")[-1]
            else:
                prop = row[0]

            if "#" in row[1]:
                domain = row[1].split("#")[-1]
            elif "/" in row[1]:
                domain = row[1].split("/")[-1]
            else:
                domain = row[1]

            registro['name'] = domain
            registro['url'] = row[1].replace(domain, "")

            datos[prop]['domain'].append(registro)

        #Captamos el dominio de cada propiedad mediante propiedad isDefinedBy
        resultado = self.grafo.query(
           """SELECT DISTINCT ?propiedad ?dominio
              WHERE {
                 ?propiedad rdf:type rdf:Property .
                 ?propiedad rdfs:isDefinedBy ?dominio .
           }""")

        #Almacenamos los dominios de las propiedades
        for row in resultado:
            registro = dict()

            if "#" in row[0]:
                prop = row[0].split("#")[-1]
            elif "/" in row[0]:
                prop = row[0].split("/")[-1]
            else:
                prop = row[0]

            if "#" in row[1]:
                domain = row[1].split("#")[-1]
            elif "/" in row[1]:
                domain = row[1].split("/")[-1]
            else:
                domain = row[1]

            registro['name'] = domain
            registro['url'] = row[1].replace(domain, "")

            datos[prop]['domain'].append(registro)

        #Captamos el rango de cada propiedad
        resultado = self.grafo.query(
           """SELECT DISTINCT ?propiedad ?rango
              WHERE {
                 { ?propiedad rdf:type rdf:Property } UNION
                 { ?propiedad rdf:type owl:ObjectProperty } UNION
                 { ?propiedad rdf:type owl:DatatypeProperty } UNION
                 { ?propiedad rdf:type owl:AnnotationProperty } .
                 ?propiedad rdfs:range ?rango .
           }""")

        #Almacenamos los rangos de las propiedades
        for row in resultado:
            registro = dict()

            if "#" in row[0]:
                prop = row[0].split("#")[-1]
            elif "/" in row[0]:
                prop = row[0].split("/")[-1]
            else:
                prop = row[0]

            #Caso de que no se trate de schema
            if row[0].replace(prop, "") != "http://schema.org/":
                if "#" in row[1]:
                    rango = row[1].split("#")[-1]
                elif "/" in row[1]:
                    rango = row[1].split("/")[-1]
                else:
                    rango = row[1]

                registro['name'] = rango
                registro['url'] = row[1].replace(rango, "")

                datos[prop]['ranges'].append(registro)
            else:
                tipo = row[1]
                if isinstance(tipo, rdflib.URIRef):
                    if "#" in tipo:
                        rango = tipo.split("#")[-1]
                    elif "/" in tipo:
                        rango = tipo.split("/")[-1]
                    else:
                        rango = tipo

                    registro['name'] = rango
                    registro['url'] = unicode(row[1]).replace(rango, "")

                    datos[prop]['ranges'].append(registro)
                elif isinstance(tipo, rdflib.BNode):
                    tipos_prop = self.grafo.query(
                   """SELECT DISTINCT ?m
                      WHERE {
                         <""" + unicode(row[0]) + """> rdf:type rdf:Property .
                         <""" + unicode(row[0]) + """> rdfs:range ?duda .
                         ?duda <http://www.w3.org/2002/07/owl#unionOf> ?union .
                         ?union rdf:rest*/rdf:first ?m
                   }""")

                    for tip in tipos_prop:
                        tip = tip[0]
                        registro = dict()
                        if "#" in tip:
                            rango = tip.split("#")[-1]
                        elif "/" in tip:
                            rango = tip.split("/")[-1]
                        else:
                            rango = tip

                        registro['name'] = rango
                        registro['url'] = unicode(tip).replace(rango, "")

                        datos[prop]['ranges'].append(registro)
                else:
                    pass  # Incoherent state

        #Step 10: Save the properties on the RegisterProperties
        for key in datos.keys():
            self.list_properties.append(RegisterProperty(key,
                                                        datos[key][u'comment'],
                                                        datos[key][u'label'],
                                                        self.namespace,
                                                        datos[key][u'domain'],
                                                        datos[key][u'ranges'],
                                                        datos[key][u'url']))


class ParserN3(ParserXML):
    """
    This class parse a schema ontology from a NTriples file.
    """
    def __init__(self, file, namespace):

        #Load the graph from de file
        self.grafo = rdflib.Graph()
        self.grafo.parse(file, format="nt")

        #Initialize the list to store the entities and properties
        self.list_entities = list()
        self.list_properties = list()

        #Initialize namespace
        self.namespace = namespace
