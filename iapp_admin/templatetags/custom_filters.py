from django import template

from iapp_user.utils import is_admin as _is_admin

register = template.Library()

@register.filter
def is_admin(user):
        import pprint; pprint.pprint(user)
        import pprint; pprint.pprint(_is_admin(user))
        return _is_admin(user)
