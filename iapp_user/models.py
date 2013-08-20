from django.conf import settings

from ldapdb.models.fields import CharField, ImageField, IntegerField, ListField
import ldapdb.models

from iapp_group.models import LdapGroup
from .utils import date2timestamp, get_or_none, debug


class LdapUser(ldapdb.models.Model):
    """
    Class for representing an LDAP user entry.
    """
    # LDAP meta-data
    base_dn = "ou=people,dc=iapp-intern,dc=de"
    object_classes = ['posixAccount',
                      'shadowAccount',
                      'inetOrgPerson',
                      'deIappPerson',
                      'sambaSamAccount',
                     ]

    # inetOrgPerson
    title = CharField(db_column='title', choices=settings.TITLES, blank=True)
    givenName = CharField(db_column='givenName')
    sn = CharField(db_column='sn')
    cn = CharField(db_column='cn')
    mail = CharField(db_column='mail')
    telephoneNumber = CharField(db_column='telephoneNumber', blank=True)
    facsimileTelephoneNumber = CharField(db_column='facsimileTelephoneNumber', blank=True)
    mobile = CharField(db_column='mobile', blank=True)
    employeeType = CharField(db_column='employeeType', choices=settings.EMPLOYEETYPES)
    team = CharField(db_column='description', choices=settings.TEAMS)
    # photo = ImageField(db_column='jpegPhoto')

    # posixAccount
    uidNumber = IntegerField(db_column='uidNumber', unique=True)
    group = IntegerField(db_column='gidNumber')
    gecos =  CharField(db_column='gecos')
    uid = CharField(db_column='uid', primary_key=True)
    password = CharField(db_column='userPassword')

    # deIappPerson
    deIappOrder = CharField(db_column='deIappOrder', choices=settings.ORDERINGS)
    deIappRole = CharField(db_column='deIappRole', blank=True)
    deIappBirthday = CharField(db_column='deIappBirthday', blank=True)

    def save(self, *args, **kwargs):
        userGroups = kwargs.pop('userGroups', None)
        newUserGroups = map(lambda g: get_or_none(LdapGroup, cn=g), userGroups)
        newUserGroups = filter(None, newUserGroups)
        currentUserGroups = LdapGroup.objects.filter(memberUid__contains=self.uid)
        deletedGroups = [g for g in currentUserGroups if g not in newUserGroups]
        for group in deletedGroups:
            group.memberUid.remove(self.uid)
            group.save()
        for group in newUserGroups:
            if self.uid not in group.memberUid:
                group.memberUid.append(self.uid)
                group.save()

        self.sambaSID = settings.SAMBA_SID + '-' + str(self.uidNumber * 2 + 1000)
        self.homeDirectory = '/home/' + self.uid
        self.loginShell = settings.DEFAULT_SHELL
        if self.deIappBirthday:
            self.deIappBirthday = date2timestamp(self.deIappBirthday)
        super(LdapUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.uid

    def __unicode__(self):
        return self.cn

