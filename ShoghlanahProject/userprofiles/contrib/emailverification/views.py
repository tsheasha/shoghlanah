# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.utils import translation
from django.contrib import messages

from userprofiles import settings as up_settings
from userprofiles.contrib.emailverification.forms import ChangeEmailForm
from userprofiles.contrib.emailverification.models import EmailVerification



@login_required
def email_change(request):
    post_change_redirect = reverse('django.contrib.auth.views.password_change_done')
    password_change_form = PasswordChangeForm
    if request.method == 'POST':
        print 'it is post'
        password_form = password_change_form(user=request.user, data=request.POST)
        email_form = ChangeEmailForm(request.POST)
        if password_form.is_valid():
            password_form.save()
            messages.success(request, "We have succesfully changed your password")
            return redirect('home')
        if email_form.is_valid():
            verification = email_form.save(request.user)
            messages.success(request, "An email with a link has been sent, click the link to continue.")
            return redirect('home')
        email_form = ChangeEmailForm()
        password_form = password_change_form(user=request.user)
    else:
        email_form = ChangeEmailForm()
        password_form = password_change_form(user=request.user)

    return {'email_form': email_form, 'password_form': password_form, 'password_length_valid':True, 'password_format_valid':True}


def email_change_save(request):
    post_change_redirect = reverse('django.contrib.auth.views.password_change_done')
    password_change_form = PasswordChangeForm
    if request.method == 'POST':
        password_form = password_change_form(user=request.user, data=request.POST)
        email_form = ChangeEmailForm(request.POST)
        if password_form.is_valid():
            password_form.save()
            messages.success(request, "We have succesfully changed your password")
            return redirect('home')
        if email_form.is_valid():
            verification = email_form.save(request.user)
            messages.success(request, "An email with a link has been sent, click the link to continue.")
            return redirect('home')
        password_form = password_change_form(user=request.user)
    else:
        email_form = ChangeEmailForm()
        password_form = password_change_form(user=request.user)

    return {'email_form': email_form, 'password_form': password_form, 'password_length_valid':True, 'password_format_valid':True}


def password_change_save(request):
    password_length_valid = True
    password_format_valid = True
    post_change_redirect = reverse('django.contrib.auth.views.password_change_done')
    password_change_form = PasswordChangeForm
    if request.method == 'POST':
        password_form = password_change_form(user=request.user, data=request.POST)
        email_form = ChangeEmailForm(request.POST)
        if password_form.is_valid():
            if not len(password_form.cleaned_data["new_password1"]) > 7:
                password_length_valid = False
            if " " in password_form.cleaned_data["new_password1"]:
                password_format_valid = False
            if password_format_valid and password_length_valid:
                password_form.save()
                messages.success(request, "We have succesfully changed your password")
                return redirect('home')
        if email_form.is_valid():
            verification = email_form.save(request.user)
            messages.success(request, "An email with a link has been sent, click the link to continue.")
            return redirect('home')
        email_form = ChangeEmailForm()
    else:
        email_form = ChangeEmailForm()
        password_form = password_change_form(user=request.user)

    return  {'email_form': email_form, 'password_form': password_form, 'password_length_valid': password_length_valid, 'password_format_valid':password_format_valid}

@login_required
def email_change_requested(request):
    return render(request, 'userprofiles/email_change_requested.html', {
        'expiration_days': up_settings.EMAIL_VERIFICATION_DAYS})


@login_required
def email_change_approve(request, token, code):
    try:
        verification = EmailVerification.objects.get(token=token, code=code,
            user=request.user, is_expired=False, is_approved=False)

        verification.is_approved = True
        verification.save()
        messages.success(request, _(u'E-mail address changed to %(email)s' % {
            'email': verification.new_email}))
    except EmailVerification.DoesNotExist:
        messages.error(request,
            _(u'Unable to change e-mail address. Confirmation link is invalid.'))

    return redirect(up_settings.EMAIL_VERIFICATION_DONE_URL)
