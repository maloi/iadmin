from datetime import datetime
from pprint import pprint
import os

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
    # return none if wanted object doesn't exist
    # needed because get() throws exception if no object is found
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def debug(msg):
    pprint(msg)

def getPhotoPath(instance, filename):
    """
    give path to photo
    """
    fileName, fileExtension = os.path.splitext(filename)
    fullName = instance.gecos.replace(' ', '_')
    return fullName + '/' + fullName + fileExtension

def is_admin(user):
    # check if user is listed in the ADMIN setting in settings.py (or local_settings.py)
    for a in settings.ADMINS:
        if user == a[0]:
          return True
    return False
