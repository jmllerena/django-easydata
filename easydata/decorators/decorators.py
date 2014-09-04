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
En este modulo se encuentran definida el decorador encargado de comprobar en
las vistas de la aplicacion que el usuario que intenta acceder a la vista, esta
logueado y tiene los permisos de superusuario.
"""

__author__ = 'llerena'

from functools import wraps
from easydata.views.sesiones import login


def easydata_super_member(view_func):
    """
    Comprueba que un usuario esta logueado y que es super usuario. Si no se
    cumpliese este requisito, redirige al formulario de login.
    """
    @wraps(view_func)
    def _checklogin(request, *args, **kwargs):
        """
        Esta es la funcion que comprueba los permisos del usuario y devuelve la
        vista original en caso de que los posea o envia a la vista de login
        """
        if request.user.is_active and request.user.is_superuser:
            # El usuario es valido
            return view_func(request, *args, **kwargs)

        return login(request)

    return _checklogin
