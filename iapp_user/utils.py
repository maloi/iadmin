from datetime import datetime
from pprint import pprint

from django.conf import settings

def date2timestamp(dateString):
    # + ' 1' is to set the hour, since legacy ldapentries has timestamps
    # that did it this way
    date = datetime.strptime(dateString + ' 1', '%d.%m.%Y %H')
    return date.strftime('%s')

def timestamp2date(timestamp):
    date = datetime.fromtimestamp(int(timestamp))
    return '%s.%s.%s' % (date.day, date.month, date.year)

# http://stackoverflow.com/a/1512094
def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def debug(msg):
    pprint(msg)

def getPhotoPath(instance, filename):
    import os
    fileName, fileExtension = os.path.splitext(filename)
    fullName = instance.gecos.replace(' ', '_')
    return fullName + '/' + fullName + fileExtension

def is_admin(user):
    for a in settings.ADMINS:
        if user == a[0]:
          return True
    return False
