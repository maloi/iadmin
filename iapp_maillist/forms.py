from django import forms
from .models import LdapMaillist

class LdapMaillistForm(forms.ModelForm):

    class Meta:
        model = LdapMaillist
        exclude = ['dn']
