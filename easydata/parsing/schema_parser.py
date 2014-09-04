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
el parseo de los datos a partir de ficheros json (experimental, solo funciona
para Schema)
"""

#Imported from Python
import rdflib
import json
import re

#Importado de la aplicacion
from easydata.parsing.parseador import Parser
from easydata.parsing.registers import RegisterEntity, RegisterProperty

__author__ = 'llerena'


class ParserJSON(Parser):
    """
    This class parse a schema ontology from a JSON file.
    """
    def __init__(self, file, namespace):
        super(ParserJSON, self).__init__()

        #Load the json from de file
        self.grafo = json.load(file)

        #Initialize the list to store the entities and properties
        self.list_entities = list()
        self.list_properties = list()

        #Initialize namespace
        self.namespace = namespace

    def parse(self):
        """
        Catch the entities and properties from the JSON, and store on the
        object
        """

        #Catch the entities
        entities = self.grafo['types']

        url = entities[entities.keys()[0]][u'url']
        if "#" in url:
            clase = url.split("#")[-1]
        elif "/" in url:
            clase = url.split("/")[-1]
        else:
            clase = url
        url = url.replace(clase, "")

        #Load all the entities of the Schema
        for key in entities.keys():
            list_super = list()
            for supertype in entities[key][u'supertypes']:
                registro = dict()
                registro['url'] = url
                registro['name'] = supertype
                list_super.append(registro)
            self.list_entities.append(RegisterEntity(key,
                                                   entities[key][u'comment'],
                                                   entities[key][u'label'],
                                                   self.namespace,
                                                   list_super,
                                                   url))

        #Catch the properties
        properties = self.grafo['properties']

        for key in properties.keys():
            list_ranges = list()
            for rango in properties[key][u'ranges']:
                registro = dict()
                registro['url'] = url
                registro['name'] = rango
                list_ranges.append(registro)
            list_domains = list()
            for domain in properties[key][u'domains']:
                registro = dict()
                registro['url'] = url
                registro['name'] = domain
                list_domains.append(registro)

            self.list_properties.append(RegisterProperty(key,
                                               properties[key][u'comment'],
                                               properties[key][u'label'],
                                               self.namespace,
                                               list_domains,
                                               list_ranges,
                                               url,
                                               self.grafo["datatypes"].keys()))


class SchemaParserXML(Parser):
    """
    This class parse a schema ontology from a N-Triples file.
    """
    def __init__(self, file, namespace):
        super(SchemaParserXML, self).__init__()

        #Load the json from de file
        self.grafo = rdflib.Graph()
        self.grafo.parse(file, format="xml")

        #Initialize the list to store the entities and properties
        self.list_entities = list()
        self.list_properties = list()

        #Initialize namespace
        self.namespace = namespace

    def parse(self):
        #Step 1: Get the main entitie Thing of the namespace
        resultado = self.grafo.query(
           """SELECT DISTINCT ?etiqueta ?comentario
              WHERE {
                 <http://schema.org/Thing> rdf:type rdfs:Class .
                 <http://schema.org/Thing> rdfs:label ?etiqueta .
                 <http://schema.org/Thing> rdfs:comment ?comentario .
           }""")

        datos = dict()
        for row in resultado:
            try:
                datos["Thing"] = dict()
                datos["Thing"]['label'] = unicode(row[0])
                datos["Thing"]['comment'] = unicode(row[1])
                datos["Thing"]['padres'] = list()
            except KeyError:
                pass

        #Step 2: Get all the entities of the namespace
        resultado = self.grafo.query(
           """SELECT DISTINCT ?clase ?etiqueta ?comentario ?padres
              WHERE {
                 ?clase rdf:type rdfs:Class .
                 ?clase rdfs:label ?etiqueta .
                 ?clase rdfs:comment ?comentario .
                 ?clase rdfs:subClassOf ?padres .
           }""")

        #Step 3: Load the data into a dictionary
        for row in resultado:
            clase = row[0].split("/")[-1]
            label = unicode(row[1])
            comment = unicode(row[2])
            padre = row[3].split("/")[-1]

            try:
                datos[clase]['padres'].append(padre)
            except KeyError:
                datos[clase] = dict()
                datos[clase]['label'] = label
                datos[clase]['comment'] = comment
                datos[clase]['padres'] = list()
                datos[clase]['padres'].append(padre)

        #Step 4: Register all the entities of the Schema
        for key in datos.keys():
            self.list_entities.append(RegisterEntity(key,
                                                     datos[key][u'comment'],
                                                     datos[key][u'label'],
                                                     self.namespace,
                                                     datos[key][u'padres']))

        #Step 5: Get the entities's properties of the namespace
        resultado = self.grafo.query(
           """SELECT DISTINCT ?propiedad ?etiqueta ?comentario ?domain
              WHERE {
                 ?propiedad rdf:type rdf:Property .
                 ?propiedad rdfs:label ?etiqueta .
                 ?propiedad rdfs:comment ?comentario .
                 ?propiedad rdfs:isDefinedBy ?domain .
           }""")

        #Step 6: Load the properties data except their domains
        datos = dict()
        for row in resultado:
            prop = row[0].split("/")[-1]
            label = unicode(row[1])
            comment = unicode(row[2])
            domain = row[3].split("/")[-1]

            try:
                datos[prop]['domain'].append(domain)
            except KeyError:
                datos[prop] = dict()
                datos[prop]['label'] = label
                datos[prop]['comment'] = comment
                datos[prop]['domain'] = list()
                datos[prop]['domain'].append(domain)
                datos[prop]['ranges'] = list()

        #Step 7: Get the properties's ranges
        #re to test if is a simple or complex tipe
        simple = "^(http://www.w3.org/2001/XMLSchema#)|"
        simple += "(http://www.w3.org/2000/01/rdf-schema#)"
        compl = "^http://schema.org/"

        resultado = self.grafo.query(
           """SELECT DISTINCT ?propiedad ?range
              WHERE {
                 ?propiedad rdf:type rdf:Property .
                 ?propiedad rdfs:range ?range .
           }""")

        for row in resultado:
            prop = row[0].split("/")[-1]
            tipo = row[1]
            if isinstance(tipo, rdflib.URIRef):
                if re.match(simple, tipo):
                    datos[prop]['ranges'].append(tipo.split("#")[-1])
                elif re.match(compl, tipo):
                    datos[prop]['ranges'].append(tipo.split("/")[-1])
                else:
                    pass  # Incoherent state
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
                    if re.match(simple, tip):
                        datos[prop]['ranges'].append(tip.split("#")[-1])
                    elif re.match(compl, tip):
                        datos[prop]['ranges'].append(tip.split("/")[-1])
                    else:
                        pass  # Incoherent state
            else:
                pass  # Incoherent state

        for key in datos.keys():
            self.list_properties.append(RegisterProperty(key,
                                                        datos[key][u'comment'],
                                                        datos[key][u'label'],
                                                        self.namespace,
                                                        datos[key][u'domain'],
                                                        datos[key][u'ranges']))


class SchemaParserNT(SchemaParserXML):
    """
    This class parse a schema ontology from a N-Triples file.
    """
    def __init__(self, file, namespace):
        #Load the json from de file
        self.grafo = rdflib.Graph()
        self.grafo.parse(file, format="nt")

        #Initialize the list to store the entities and properties
        self.list_entities = list()
        self.list_properties = list()

        #Initialize namespace
        self.namespace = namespace
