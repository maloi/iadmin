from django.conf import settings

from ldapdb.models.fields import CharField, ImageField, IntegerField, ListField
import ldapdb.models


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
    description =  CharField(db_column='description')
    memberUid = ListField(db_column='memberUid')

    # extensibleObject
    mail = CharField(db_column='mail')
    owner = CharField(db_column='owner')

    def __str__(self):
        return self.cn

    def __unicode__(self):
        return self.cn
