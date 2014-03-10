# -*- coding: utf-8 -*-
from shoghlanah import user_profile
from django.conf.urls.defaults import patterns, url, include

from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django import forms


class MySetPasswordForm(forms.Form):
    """
    A form that lets a user change set his/her password without entering the
    old password
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'password_length': _("The length of the Passwords should be a min. 8 characters."),
    }
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(MySetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'])
            if len(password1) < 8 or len(password2) < 8:
                raise forms.ValidationError(
                    self.error_messages['password_length'])
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user

urlpatterns = patterns('userprofiles.views',
    url(r'^register/$', 'registration', name='userprofiles_registration'),
    url(r'^register/complete/$', 'registration_complete',
        name='userprofiles_registration_complete'),
)

if 'userprofiles.contrib.accountverification' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^activate/', include('userprofiles.contrib.accountverification.urls')),
    )

if 'userprofiles.contrib.emailverification' in settings.INSTALLED_APPS:
    # urlpatterns += patterns('',
    #     (r'^email/', include('userprofiles.contrib.emailverification.urls')),
    # )
    urlpatterns += patterns('userprofiles.contrib.emailverification.views',
    url(r'^requested/$', 'email_change_requested',
        name='userprofiles_email_change_requested'),
    url(r'^verify/(?P<token>[0-9A-Za-z-]+)/(?P<code>[0-9A-Za-z-]+)/$',
        'email_change_approve', name='userprofiles_email_change_approve'),
    )
    urlpatterns += patterns('shoghlanah',
    url(r'^settings/email_change/$', 'user_profile.edit_view', name='email_change_save'),
    url(r'^settings/password_change/$', 'user_profile.edit_view', name='password_change_save'),
    )


if 'userprofiles.contrib.profiles' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^profile/', include('userprofiles.contrib.profiles.urls')),
    )

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^logout/$', 'logout', {'template_name': 'userprofiles/logged_out.html'},
        name='auth_logout'),
    url(r'^password/change/$', 'password_change',
        {'template_name': 'userprofiles/password_change.html'},
        name='auth_password_change'),
    url(r'^password/change/done/$', 'password_change_done',
        {'template_name': 'userprofiles/password_change_done.html'},
        name='auth_password_change_done'),
    url(r'^password/reset/$', 'password_reset',
        {'template_name': 'userprofiles/password_reset.html',
         'email_template_name': 'userprofiles/mails/password_reset_email.html'},
        name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'password_reset_confirm',
        {'template_name': 'userprofiles/password_reset_confirm.html', 'set_password_form':MySetPasswordForm},
        name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$', 'password_reset_complete',
        {'template_name': 'userprofiles/registration.html', 'extra_context':{'pass_reset': True}},
        name='auth_password_reset_complete'),
    url(r'^password/reset/done/$', 'password_reset_done',
        {'template_name': 'userprofiles/registration.html', 'extra_context':{'email_sent': True}},
        name='auth_password_reset_done'),
)
