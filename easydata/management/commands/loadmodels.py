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
Este modulo contiene comando loadmodels que se ejecutara desde el manage.py de
Django, el cual realizara la captacion de los distintos modelos y fields del
proyecto Django donde se encuetra instalada la aplicacion EasyData
"""

from django.core.management.base import BaseCommand
from django.db.models import get_models, get_model, get_app, get_apps
from django.db import IntegrityError
from django.core.exceptions import ImproperlyConfigured
from easydata.models import Modelo, Relacion, Atributo


class Command(BaseCommand):
    """
    Esta clase se encarga de implementar el comando loadmodels de manage.py
    """

    args = '<app_name>'
    help = 'Load the models and fields of the project, into the EasyData \
            application'

    def handle(self, *args, **options):
        modelos = list()
        if len(args) != 0:
            #Load only the models of the specified app
            try:
                aplicacion = get_app(app_label=args[0])
                modelos = get_models(aplicacion)
            except ImproperlyConfigured:
                print "The application doesn't exist"
        else:
            aplicaciones = get_apps()

            #Load the models of the apps except of EasyData app
            for app in aplicaciones:
                if not app.__name__.startswith('easydata.'):
                    modelos += get_models(app)

        #Iterate over the models
        for mod in modelos:
            modelo_instance = Modelo(nombre=mod.__name__,
                                     aplicacion=mod._meta.app_label)

            #Save the model instance
            try:
                modelo_instance.save()
            except IntegrityError:
                print "El modelo %s ya esta incluido y no se \
salva" % mod.__name__

        #Delete the models and fields that don't exist on the project
        self.elimina_modelos()
        self.elimina_fields()

        #Iterate one more time over the models, to add the fields
        for mod in modelos:
            modelo_instance = Modelo.objects.all()
            modelo_instance = modelo_instance.filter(nombre=mod.__name__)
            modelo_instance = modelo_instance.filter(
                              aplicacion=mod._meta.app_label).get()

            #Load the fiel list
            lista_fields = mod._meta.fields

            # Store the many relations if not are stored
            for many in mod._meta.many_to_many:
                if not many in lista_fields:
                    lista_fields.append(many)

            fields_texto = list()

            for atributo in lista_fields:
                #Case: Relation
                if not getattr(atributo, 'related', None) is None:
                    #Take the related model
                    mod_class = atributo.rel.to

                    #Search this model
                    try:
                        mod_rel = Modelo.objects.all()
                        mod_rel = mod_rel.filter(nombre=mod_class.__name__)
                        mod_rel = mod_rel.filter(
                                  aplicacion=mod_class._meta.app_label)
                        mod_rel = mod_rel.get()
                    except Modelo.DoesNotExist:
                        mod_rel = Modelo(nombre=mod_class.__name__,
                                         aplicacion=mod_class._meta.app_label)

                        #Save the model instance
                        try:
                            mod_rel.save()
                            mod_class_rel = get_model(
                                            model_name=mod_class.__name__,
                                            app_label=mod_class._meta
                                            .app_label)
                            modelos.append(mod_class_rel)
                        except IntegrityError:
                            print "El modelo %s ya esta incluido y no se \
salva" % mod_class.__name__

                    #Get the relation type
                    tipo_relacion = self.get_relation_type(atributo.__class__)

                    #Si se encuentra el tipo de relacion, continuamos
                    if not tipo_relacion is None:
                        #Relation in one direction
                        field_instance = Relacion(nombre=atributo.name,
                                                  modelo=modelo_instance,
                                                  tipo_relacion=tipo_relacion,
                                                  modelo_relacionado=mod_rel)

                        #Save the field
                        try:
                            field_instance.save()
                        except IntegrityError:
                            print "El field %s del modelo %s ya existe y no se\
 salva" % (atributo.name, modelo_instance)

                            #Get the relation to update
                            field_instance = Relacion.objects.all()
                            field_instance = field_instance.filter(
                                             nombre=atributo.name)
                            field_instance = field_instance.filter(
                                             modelo=modelo_instance)

                            if field_instance.count() == 1:
                                field_instance = field_instance.get()

                                #Update the relation
                                field_instance.tipo_relacion = tipo_relacion
                                field_instance.modelo_relacionado = mod_rel
                                field_instance.save()

                            else:
                                field_instance = Relacion.objects.all()
                                field_instance = field_instance.filter(
                                                 nombre=atributo.name)
                                field_instance = field_instance.filter(
                                                 modelo=modelo_instance)

                                if field_instance.count() == 1:
                                    field_instance.delete()

                                    field_instance = Relacion(
                                                   nombre=atributo.name,
                                                   modelo=modelo_instance,
                                                   tipo_relacion=tipo_relacion,
                                                   modelo_relacionado=mod_rel)
                                    field_instance.save()

                        if tipo_relacion == "FO":
                            tipo_relacion = "OF"

                        #If doesn't have accessor name
                        #I can't access in the other direction
                        if not atributo.related.get_accessor_name() is None \
                           and mod == atributo.model:
                            #In the other direction
                            field_instance_related = Relacion(
                                            nombre=atributo.related
                                            .get_accessor_name(),
                                            modelo=mod_rel,
                                            tipo_relacion=tipo_relacion,
                                            inversa=field_instance,
                                            modelo_relacionado=modelo_instance)

                            #Save the field
                            try:
                                field_instance_related.save()
                            except IntegrityError:
                                print "El field %s del modelo %s ya existe y \
no se salva" % (atributo.related.get_accessor_name(), mod_rel.nombre)

                                #Get the relation to update
                                field_instance = Relacion.objects.all()
                                field_instance = field_instance.filter(
                                                 nombre=atributo.related
                                                 .get_accessor_name())
                                field_instance = field_instance.filter(
                                                  modelo=mod_rel)

                                if field_instance.count() == 1:
                                    field_instance = field_instance.get()

                                    #Update the relation
                                    field_instance.tipo_relacion = \
                                                                tipo_relacion
                                    field_instance.modelo_relacionado = \
                                                                modelo_instance
                                    field_instance.save()
                                else:
                                    field_instance = Atributo.objects.all()
                                    field_instance = field_instance.filter(
                                   nombre=atributo.related.get_accessor_name())
                                    field_instance = field_instance.filter(
                                                     modelo=mod_rel)

                                    if field_instance.count() == 1:
                                        field_instance.delete()

                                        field_instance_related = Relacion(
                                   nombre=atributo.related.get_accessor_name(),
                                   modelo=mod_rel,
                                   tipo_relacion=tipo_relacion,
                                   modelo_relacionado=modelo_instance)
                                        field_instance_related.save()

                else:  # Case: normal field
                    field_instance = Atributo(
                                     nombre=atributo.name,
                                     modelo=modelo_instance,
                                     tipo_field=atributo.__class__.__name__)

                    #Save the field
                    try:
                        field_instance.save()
                    except IntegrityError:
                        print "El field %s del modelo %s ya existe y no se \
salva" % (atributo.name, modelo_instance)

                        field_instance = Atributo.objects.all()
                        field_instance = field_instance.filter(
                                         nombre=atributo.name)
                        field_instance = field_instance.filter(
                                          modelo=modelo_instance)

                        if field_instance.count() == 1:
                            field_instance = field_instance.get()

                            #If exists, update the fields
                            field_instance.tipo_field = \
                                                    atributo.__class__.__name__
                            field_instance.save()
                        else:
                            field_instance = Relacion.objects.all()
                            field_instance = field_instance.filter(
                                             nombre=atributo.name)
                            field_instance = field_instance.filter(
                                             modelo=modelo_instance)

                            if field_instance.count() == 1:
                                field_instance.delete()

                                field_instance = Atributo(
                                                 nombre=atributo.name,
                                                 modelo=modelo_instance,
                                                 tipo_field=atributo.__class__
                                                 .__name__)
                                field_instance.save()

                #Add the field to the list
                fields_texto.append(atributo.name)

        print ">> The load has finished succesfully <<"

    def elimina_modelos(self):
        """
        Iterate over all the models in the data base, and check if exist or not
        """

        #Recorremos todos los modelos de la aplicacion
        for mod in Modelo.objects.all():
            #Si no existe, borramos el modelo y sus fields
            if mod.devolver_modelo() is None:
                relations = Relacion.objects.all()
                relations = relations.filter(modelo_relacionado=mod)
                relations.delete()
                mod.fields.all().delete()
                print "Se borra el modelo %s" % mod.nombre
                mod.delete()

    def elimina_fields(self):
        """
        Iterate over all the models's fields in the data base, and check if the
        fields already exist or not
        """
        mods = Modelo.objects.all()

        # For each model on the system
        for mod in mods:
            mod_class = mod.devolver_modelo()
            lista_fields = mod_class._meta.fields
            lista_fields += mod_class._meta.many_to_many

            # Get only the names
            lista_name_fields = [attr.name for attr in lista_fields]

            # Get the Attributes loaded on the application
            loaded_attrs = Atributo.objects.all()
            loaded_attrs = loaded_attrs.filter(modelo=mod)

            for attr in loaded_attrs:
                # If don't find the name, delete the field
                if not attr.nombre in lista_name_fields:
                    attr.delete()

            # Get the Relations loaded on the application
            loaded_rels = Relacion.objects.all()
            loaded_rels = loaded_rels.filter(modelo=mod)

            for rel in loaded_rels:
                exist = False

                if rel.nombre in lista_name_fields:
                    exist = True

                if not exist:
                    # Get the fields of the model related
                    model_related = rel.modelo_relacionado.devolver_modelo()
                    rels_model_related = model_related._meta.fields
                    rels_model_related += model_related._meta.many_to_many

                    for relaux in rels_model_related:
                        if not getattr(relaux, 'related', None) is None and \
                           not relaux.related.get_accessor_name() is None and \
                           rel.nombre == relaux.related.get_accessor_name():
                            exist = True
                            break

                if not exist:
                    rel.delete()

    def get_relation_type(self, clase_relacion):
        """
        Return the relatio type. If there are custom relations, it search their
        base types relations, util find a ForeignKey, OneToOneField or
        ManyToManyField.
        """
        if not clase_relacion is None:
            if clase_relacion.__name__ == 'ManyToManyField':
                tipo_relacion = "M"
            elif clase_relacion.__name__ == 'OneToOneField':
                tipo_relacion = "O"
            elif clase_relacion.__name__ == 'ForeignKey':
                tipo_relacion = "FO"
            else:
                return self.get_relation_type(clase_relacion.__base__)
        else:
            #Uso esta por defecto
            tipo_relacion = None

        return tipo_relacion
