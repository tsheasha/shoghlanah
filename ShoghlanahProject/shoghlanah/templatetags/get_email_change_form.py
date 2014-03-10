from django import template
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from userprofiles import settings as up_settings
from userprofiles.contrib.emailverification.forms import ChangeEmailForm
from userprofiles.contrib.emailverification.models import EmailVerification
import json

register = template.Library()

@register.filter
def email_change(request):
    form = ChangeEmailForm()
    return render(request, 'userprofiles/email_change.html', {'form': form})