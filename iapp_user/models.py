from django.conf import settings
from django.db import models, connections, router

from ldapdb.models.fields import CharField, IntegerField, ListField, ImageField
import ldapdb.models

from iapp_group.models import LdapGroup
from .utils import date2timestamp, get_or_none, debug, getPhotoPath


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
    givenName = CharField(db_column='givenName', blank=True)
    sn = CharField(db_column='sn')
    cn = CharField(db_column='cn')
    mail = CharField(db_column='mail', blank=True)
    telephoneNumber = CharField(db_column='telephoneNumber', blank=True)
    facsimileTelephoneNumber = CharField(db_column='facsimileTelephoneNumber', blank=True)
    mobile = CharField(db_column='mobile', blank=True)
    employeeType = CharField(db_column='employeeType', choices=settings.EMPLOYEETYPES, blank=True)
    team = CharField(db_column='description', choices=settings.TEAMS, blank=True)
    # use django imatgefield, cause the ldap one is buggy
    # we use this one in the form and set the jpegPhoto in the view
    photo = models.ImageField(upload_to=getPhotoPath, blank=True)
    jpegPhoto = ImageField(db_column='jpegPhoto', blank=True)
    roomNumber = CharField(db_column='roomNumber', blank=True)

    # posixAccount
    uidNumber = IntegerField(db_column='uidNumber', unique=True)
    gidNumber = IntegerField(db_column='gidNumber', choices=settings.GROUPS)
    gecos =  CharField(db_column='gecos')
    uid = CharField(db_column='uid', primary_key=True)
    userPassword = CharField(db_column='userPassword')
    homeDirectory = CharField(db_column='homeDirectory')
    loginShell = CharField(db_column='loginShell')

    # deIappPerson
    deIappOrder = CharField(db_column='deIappOrder', choices=settings.ORDERINGS)
    deIappRole = CharField(db_column='deIappRole', blank=True)
    deIappBirthday = CharField(db_column='deIappBirthday', blank=True)

    # sambaSamAccount
    sambaLMPassword = CharField(db_column='sambaLMPassword')
    sambaNTPassword = CharField(db_column='sambaNTPassword')
    sambaSID = CharField(db_column='sambaSID')

    def save(self, *args, **kwargs):
        """
        save the model and set implicit attributes like sambaSID etc
        """
        # userGroups is given as kwarg by the view as list of strings
        # we get the corresponding ldapgroups and check which are new
        # and which can be deleted
        userGroups = kwargs.pop('userGroups', [])
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

        # implicit attributes
        self.cn = self.givenName + ' ' + self.sn
        self.sambaSID = settings.SAMBA_SID + '-' + str(self.uidNumber * 2 + 1000)
        self.homeDirectory = '/home/' + self.uid
        self.loginShell = settings.DEFAULT_SHELL
        # build unix timestamp from given date format (dd.mm.yyyy)
        if self.deIappBirthday:
            self.deIappBirthday = date2timestamp(self.deIappBirthday)
        # password is given as kwarg by the view
        # sha1, lm/nt hashes are build from this password and will be saved
        password = kwargs.pop('password', False)
        if password:
            from passlib.hash import ldap_salted_sha1 as lss
            from passlib.hash import lmhash
            from passlib.hash import nthash
            self.userPassword = lss.encrypt(password)
            self.sambaLMPassword = lmhash.encrypt(password).upper()
            self.sambaNTPassword = nthash.encrypt(password).upper()
        super(LdapUser, self).save(*args, **kwargs)

    def delete(self, using=None):
        """
        Delete this entry. (move user to former-members ou)
        """
        using = using or router.db_for_write(self.__class__, instance=self)
        connection = connections[using]
        cursor = connection._cursor()
        cursor.connection.rename_s(self.dn.encode(connection.charset),
                                   'uid=' + self.uid.encode(connection.charset),
                                   newsuperior='ou=Former-Members,dc=iapp-intern,dc=de')

    def groups(self):
        # returns the groups of a ldapuser
        return LdapGroup.objects.filter(memberUid__contains=self.uid)

    def __str__(self):
        return self.uid

    def __unicode__(self):
        return self.cn


class FormerLdapUser(LdapUser):
    """
    Class for representing an LDAP user entry.
    This is need, because django-ldapdb can handle only one base dn
    and only former members can be undeleted
    """
    # LDAP meta-data
    base_dn = "ou=former-members,dc=iapp-intern,dc=de"

    def undelete(self, using=None):
        """
        'Undelete' this entry. (move user back to people ou)
        """
        using = using or router.db_for_write(self.__class__, instance=self)
        connection = connections[using]
        cursor = connection._cursor()
        cursor.connection.rename_s(self.dn.encode(connection.charset),
                                   'uid=' + self.uid.encode(connection.charset),
                                   newsuperior='ou=People,dc=iapp-intern,dc=de')

