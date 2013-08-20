from django import forms
from .models import LdapUser

class LdapUserForm(forms.ModelForm):
    class Meta:
        model = LdapUser
        widgets = {
            'deIappBirthday': forms.DateInput(
                format='%d/%m/%Y',
                attrs={'class': 'date', 'readonly': 'readonly',}
            ),
        }
