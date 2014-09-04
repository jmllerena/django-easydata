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
Este modulo almacena las vistas tanto de bienvenida, como las vistas donde se
ofrece ayuda a los usuarios, indicandoles ejemplos de uso de la aplicacion
tanto para urls y plantillas
"""

from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from django.template import RequestContext
from django.contrib.auth import logout
from django.utils.translation import ugettext as _

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login


__author__ = 'llerena'


def disconnect(request):
    """
    Esta vista se encarga de cerrar la sesion
    """
    if request.user.is_authenticated():
        # Logout the user
        logout(request)

        # Create logout message
        messages.info(request, _('You have been logged out'))
    else:
        # Create logout message
        messages.info(request, _("You aren't logged in"))

    # Redirect to the welcome view
    return redirect('easydata.views.information.welcome')


def login(request):
    """
    Esta vista se encarga de iniciar la sesion
    """
    if request.POST:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return redirect('easydata.views.information.welcome')
    else:
        form = AuthenticationForm(request)

    if request.user.is_authenticated() and not request.user.is_superuser:
        messages.info(request, _("You have to be a superuser to access to \
this section"))

    request.session.set_test_cookie()

    return render_to_response('easydata/information/login.html',
                              {'form': form, },
                              context_instance=RequestContext(request))
