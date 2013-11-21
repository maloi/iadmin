from django.conf import settings

from ldapdb.models.fields import CharField, ImageField, IntegerField, ListField
import ldapdb.models

from iapp_user.utils import debug


class LdapGroup(ldapdb.models.Model):
    """
    Class for representing an LDAP group entry.
    """
    # LDAP meta-data
    base_dn = "ou=group,dc=iapp-intern,dc=de"
    object_classes = ['posixGroup',
                      'extensibleObject',
                     ]

    # posixGroup
    cn = CharField(db_column='cn', primary_key=True)
    gidNumber = IntegerField(db_column='gidNumber', unique=True)
    description =  CharField(db_column='description', blank=True)
    memberUid = ListField(db_column='memberUid')

    # extensibleObject
    owner = ListField(db_column='owner')

    def __str__(self):
        return self.cn

    def __unicode__(self):
        return self.cn
