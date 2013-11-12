from django import forms
from .models import LdapUser
from iapp_room.models import LdapRoom
from .utils import debug

class LdapUserForm(forms.ModelForm):
    userPassword1 = forms.CharField(max_length=200, widget=forms.PasswordInput(), required=False)
    userPassword2 = forms.CharField(max_length=200, widget=forms.PasswordInput(), required=False)
    room = forms.ModelChoiceField(queryset=LdapRoom.objects.all(), required=False)

    def clean(self):
        """
        Checks if form input is valid, password is valid if both passwords match
        """
        cleaned_data = super(LdapUserForm, self).clean()
        password1 = self.cleaned_data.get('userPassword1')
        password2 = self.cleaned_data.get('userPassword2')
        if password1 != password2:
            raise forms.ValidationError('Passwords did not match!')
        return cleaned_data

    class Meta:
        model = LdapUser
        # attributes, that should not be shown in form
        # will be handled in models save() nethod
        exclude = ['cn', 'dn', 'jpegPhoto', 'roomNumber', 'telephoneNumber', 'userPassword',
                   'sambaNTPassword', 'sambaLMPassword', 'homeDirectory', 'loginShell',
                   'sambaSID']
        # sets class date, so it will be handled by jquery datepicker
        # readonly, so it can only be modified by datepicker
        widgets = {
            'deIappBirthday': forms.DateInput(
                format='%d/%m/%Y',
                attrs={'class': 'date', 'readonly': 'readonly',}
            ),
        }
