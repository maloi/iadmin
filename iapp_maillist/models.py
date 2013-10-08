from django.conf import settings

from ldapdb.models.fields import CharField, ImageField, IntegerField, ListField
import ldapdb.models

from iapp_user.utils import debug


class LdapMaillist(ldapdb.models.Model):
    """
    Class for representing an LDAP Maillist entry.
    """
    # LDAP meta-data
    base_dn = "ou=Mailinglists,dc=iapp-intern,dc=de"
    object_classes = ['groupOfNames',
                      'extensibleObject',
                     ]

    # groupOfNames
    cn = CharField(db_column='cn', primary_key=True)
    description =  CharField(db_column='description', blank=True)
    member = ListField(db_column='member')

    # extensibleObject
    mail = CharField(db_column='mail')
    owner = ListField(db_column='owner')
    rfc822MailMember = ListField(db_column='rfc822MailMember', blank=True)

    def __str__(self):
        return self.cn

    def __unicode__(self):
        return self.cn
