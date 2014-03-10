# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect

from userprofiles import settings as up_settings
from userprofiles.contrib.accountverification.models import AccountVerification
from django.contrib import messages
from django.utils import translation
from django.template import RequestContext
from django.shortcuts import redirect

def registration_activate(request, activation_key):
    activation_key = activation_key.lower()
    account = AccountVerification.objects.activate_user(activation_key)

    messages.info(request, translation.gettext("Your account is now activated"))
    return redirect('/log_in/', context_instance=RequestContext(request))

    # return render(request, 'userprofiles/registration_activate.html', {
    #     'account': account,
    #     'expiration_days': up_settings.ACCOUNT_VERIFICATION_DAYS
    # })
