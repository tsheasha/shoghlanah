from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth.models import User
from django.utils import translation


class uploadProfilePicture(forms.Form):
    image = forms.ImageField()


class uploadCoverPicture(forms.Form):
    coverimage = forms.ImageField()


class MonospaceForm(forms.Form):
    def addError(self, message):
        self._errors[NON_FIELD_ERRORS] = self.error_class([message])


class CardForm(MonospaceForm):
    last_4_digits = forms.CharField(
        required=True,
        min_length=4,
        max_length=4,
        widget=forms.HiddenInput()
    )

    stripe_token = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )


class InfoCheckForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(), min_length=6)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        #username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError(translation.gettext("This email address is already registered"))
        return email
