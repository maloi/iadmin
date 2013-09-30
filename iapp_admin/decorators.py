from functools import wraps

from django.http import Http404

from iapp_user.models import LdapUser
from iapp_user.utils import debug, get_or_none, is_admin

"""
Decorators wrap functions
This ones allow the function to be executed only if
user is an admin or is an owner of the object
"""

def admin_required(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        if is_admin(request.user.username):
            return function(request, *args, **kwargs)
        raise Http404

    return decorator

def owner_or_admin_required(cls, function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        user = get_or_none(LdapUser,pk=request.user.username)
        if not user:
            raise Http404
        object = cls.objects.get(pk=kwargs['pk'])
        if is_admin(user.uid) or user.dn in object.owner:
            return function(request, *args, **kwargs)
        raise Http404

    return decorator

