# -*- coding: utf-8 -*-
import uuid
import random
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import User

from shoghlanah.models import UserProfile

from userprofiles import settings as up_settings

if up_settings.USE_ACCOUNT_VERIFICATION:
    from userprofiles.contrib.accountverification.models import AccountVerification

if 'userprofiles.contrib.emailverification' in settings.INSTALLED_APPS:
    from userprofiles.contrib.emailverification.models import EmailVerification
from django.core.exceptions import ValidationError
from django.utils import translation


def clean_new_password1(value):
        password1 = value

        # At least MIN_LENGTH long
        if len(password1) < 8 or " " in password1:
            raise ValidationError(translation.gettext("The password must be at least 8 characters long and doesn't contain spaces"))

        # At least one letter and one non-letter
        # first_isalpha = password1[0].isalpha()
        # if all(c.isalpha() == first_isalpha for c in password1):
        #     raise ValidationError(translation.gettext("The password must contain at least one letter and at least one digit or punctuation character"))

        # ... any other validation you want ...

        return password1


class RegistrationForm(forms.Form):

    first_name = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'placeholder': _('First Name')}), required=True)
    last_name = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'placeholder': _('Last Name')}), required=True)
    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[\w.-]+$', error_messages={'invalid': _(
            'This value may contain only letters, numbers and ./-/_ characters.')})

    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder': _('Email')}))
    email_repeat = forms.EmailField(label=_('E-mail (repeat)'), required=True)

    password = forms.CharField(label='', widget=forms.PasswordInput(render_value=False, attrs={'placeholder': _('Password')}),
        validators=[clean_new_password1],
        error_messages={'invalid': _('Enter a valid email address.')},
        )
    password_repeat = forms.CharField(label=_('Password (repeat)'),
        widget=forms.PasswordInput(render_value=False))

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        if not up_settings.DOUBLE_CHECK_EMAIL:
            del self.fields['email_repeat']

        if not up_settings.DOUBLE_CHECK_PASSWORD:
            del self.fields['password_repeat']

        if up_settings.EMAIL_ONLY:
            self.fields['username'].widget = forms.widgets.HiddenInput()
            self.fields['username'].required = False


    def _generate_username(self):
        """ Generate a unique username """
        while True:
            # Generate a UUID username, removing dashes and the last 2 chars
            # to make it fit into the 30 char User.username field. Gracefully
            # handle any unlikely, but possible duplicate usernames.
            username = str(uuid.uuid4())
            username = username.replace('-', '')
            username = username[:-2]

            try:
                UserProfile.objects.get(username=username)
            except User.DoesNotExist:
                return username

    def clean_username(self):
        if up_settings.EMAIL_ONLY:
            username = self._generate_username()
        else:
            username = self.cleaned_data['username']
            if UserProfile.objects.filter(username__iexact=username):
                raise forms.ValidationError(
                    _(u'A user with that username already exists.'))

        return username

    def clean_email(self):
        if not up_settings.CHECK_UNIQUE_EMAIL:
            return self.cleaned_data['email']

        new_email = self.cleaned_data['email']

        emails = UserProfile.objects.filter(email__iexact=new_email).count()
        if 'userprofiles.contrib.emailverification' in settings.INSTALLED_APPS:

            emails += EmailVerification.objects.filter(
                new_email__iexact=new_email, is_expired=False).count()
        if emails > 0:
            raise forms.ValidationError(
                _(u'This email address is already registered'))

        return new_email

    def clean(self):
        if up_settings.DOUBLE_CHECK_EMAIL:
            if 'email' in self.cleaned_data and 'email_repeat' in self.cleaned_data:
                if self.cleaned_data['email'] != self.cleaned_data['email_repeat']:
                    raise forms.ValidationError(_('The two email addresses do not match.'))

        if up_settings.DOUBLE_CHECK_PASSWORD:
            if 'password' in self.cleaned_data and 'password_repeat' in self.cleaned_data:
                if self.cleaned_data['password'] != self.cleaned_data['password_repeat']:
                    raise forms.ValidationError(_('You must type the same password each time.'))

        return self.cleaned_data

    def save(self, *args, **kwargs):
        if up_settings.USE_ACCOUNT_VERIFICATION:
            new_user = AccountVerification.objects.create_inactive_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
            )
        else:
            new_user = UserProfile.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email']
            )
            new_user.email = self.cleaned_data['email']
            new_user.first_name = self.cleaned_data['first_name']
            new_user.last_name = self.cleaned_data['last_name']
            new_user.set_password(self.cleaned_data['password'])
            new_user.save()

        profile_pictures = ["../media/ProfileDefaults/profile_pic_default.png", "../media/ProfileDefaults/profile_pic_default2.png", "../media/ProfileDefaults/profile_pic_default3.png", "../media/ProfileDefaults/profile_pic_default4.png", "../media/ProfileDefaults/profile_pic_default5.png"]
        new_user.profile_picture = profile_pictures[int(random.random() * len(profile_pictures))]
        new_user.save()

        if hasattr(self, 'save_profile'):
            self.save_profile(new_user, *args, **kwargs)

        return new_user
