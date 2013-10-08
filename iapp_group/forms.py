from django import forms
from .models import LdapGroup

class LdapGroupForm(forms.ModelForm):

    class Meta:
        model = LdapGroup
        exclude = ['dn']

    def __init__(self, *args, **kwargs):
        super(LdapGroupForm, self).__init__(*args, **kwargs)
        self.fields['gidNumber'].widget.attrs['readonly'] = True