from functools import wraps

from django.conf import settings
from django.http import Http404

from iapp_user.models import LdapUser
from iapp_user.utils import debug

def admin_required(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        if _is_admin(request.user.username):
            return function(request, *args, **kwargs)
        raise Http404

    return decorator

def owner_or_admin_required(cls, function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        user = LdapUser.objects.get(pk=request.user.username)
        object = cls.objects.get(pk=kwargs['pk'])
        if _is_admin(user.uid) or user.dn in object.owner:
            return function(request, *args, **kwargs)
        raise Http404

    return decorator

def _is_admin(user):
    for a in settings.ADMINS:
        if user == a[0]:
          return True
    return False
