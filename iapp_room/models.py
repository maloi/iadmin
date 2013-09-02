from ldapdb.models.fields import CharField
import ldapdb.models


class LdapRoom(ldapdb.models.Model):
    """
    Class for representing an LDAP roon entry.
    """
    # LDAP meta-data
    base_dn = "ou=rooms,dc=iapp-intern,dc=de"
    object_classes = ['room']

    # posixGroup
    cn = CharField(db_column='cn', primary_key=True)
    description =  CharField(db_column='description')
    telephoneNumber = CharField(db_column='telephoneNumber')

    def __str__(self):
        return self.cn

    def __unicode__(self):
        return self.cn
