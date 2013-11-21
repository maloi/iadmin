from django import template

from iapp_user.utils import is_admin as _is_admin
from iapp_user.utils import timestamp2date as _timestamp2date

register = template.Library()

"""
Filters can be used in templates
the first one checks if the user is an admin
the second builds a date from a timestamp
"""

@register.filter
def is_admin(user):
        return _is_admin(user)

@register.filter
def timestamp2date(timestamp):
        return _timestamp2date(timestamp)
