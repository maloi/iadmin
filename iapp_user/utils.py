from datetime import datetime
from pprint import pprint

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
