from django import forms
from .models import LdapGroup

class LdapGroupForm(forms.ModelForm):

    class Meta:
        model = LdapGroup
        exclude = ['dn']
