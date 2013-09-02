from django import forms
from .models import LdapUser
from .utils import debug

class LdapUserForm(forms.ModelForm):
    userPassword2 = forms.CharField(max_length=200, widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(LdapUserForm, self).clean()
        password = self.cleaned_data.get('userPassword')
        password2 = self.cleaned_data.get('userPassword2')
        if password != password2:
            raise forms.ValidationError('Passwords did not match!')
        return cleaned_data

    class Meta:
        model = LdapUser
        exclude = ['jpegPhoto']
        widgets = {
            'deIappBirthday': forms.DateInput(
                format='%d/%m/%Y',
                attrs={'class': 'date', 'readonly': 'readonly',}
            ),
            'userPassword': forms.PasswordInput(),
        }
