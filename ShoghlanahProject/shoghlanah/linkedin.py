from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
import logging
import urllib
from django.core.files import File
from shoghlanah.models import *
from django.conf import settings
import random
import string
from views import import_simplejson
json = import_simplejson()

CONSUMER_KEY = getattr(settings, 'LINKEDIN_ID', '')
CONSUMER_SECRET = getattr(settings, 'LINKEDIN_SECRET', '')
LINKEDIN_PERMISSIONS = getattr(settings, 'LINKEDIN_PERMISSIONS', '')
LOGIN_REDIRECT_URL = getattr(settings, 'LOGIN_REDIRECT_URL', '')
DEPLOYED_ADDRESS = getattr(settings, 'DEPLOYED_ADDRESS', '')
SCOPE_SEPARATOR = ' '
STATE = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(21))


@login_required
def linkedin_disconnect(request):
    userprofile = UserProfile.objects.get(username=request.user.username)
    userprofile.linkedin_link = None
    userprofile.save()
    next = request.META.get('HTTP_REFERER', reverse('home'))
    try:
        LinkedinUserProfile.objects.get(user=userprofile).delete()
    except LinkedinUserProfile.DoesNotExist:
        return HttpResponseRedirect(next)
    return HttpResponseRedirect(next)


def linkedin_login(request):
    params = {}
    params["response_type"] = "code"
    params["client_id"] = CONSUMER_KEY
    params["redirect_uri"] = request.build_absolute_uri(reverse("linkedin_login_done"))
    params['scope'] = SCOPE_SEPARATOR.join(LINKEDIN_PERMISSIONS)
    params["state"] = STATE

    url = "https://www.linkedin.com/uas/oauth2/authorization?" + urllib.urlencode(params)
    if 'HTTP_REFERER' in request.META:
        request.session['next'] = request.META['HTTP_REFERER']
    return HttpResponseRedirect(url)


def linkedin_login_done(request):
    denied = request.GET.get('error', None)
    result = None
    if not denied:
        result = authenticate(request=request)

    if not result:
        logging.debug("LinkedIn Backend: Couldn't authenticate user with Django, redirecting to Register page")
        return redirect(reverse('home'))

    if isinstance(result, UserProfile):
        if result.is_active:
            result.linkedin_link = LinkedinUserProfile.objects.get(user=result).url
            result.save()
            login(request, result)
            logging.debug("LinkedIn Backend: Successfully logged in with LinkedIn!")
            if 'next' in request.session:
                next = request.session['next']
                del request.session['next']
                request.session['Social'] = "linkedin"
                return redirect(next, RequestContext(request))
            else:
                return HttpResponseRedirect(reverse('home'))
    else:
        return result


class LinkedinBackend:
    user = None

    def authenticate(self, request):
        user = request.user or None
        access_token = None
        # assume logging in normal way
        params = {}
        params["grant_type"] = "authorization_code"
        params["code"] = request.GET.get('code', '')
        params["redirect_uri"] = request.build_absolute_uri(reverse("linkedin_login_done"))
        params["client_id"] = CONSUMER_KEY
        params["client_secret"] = CONSUMER_SECRET

        url = ("https://www.linkedin.com/uas/oauth2/accessToken?"
               + urllib.urlencode(params))

        userdata = urllib.urlopen(url).read()

        import ast
        res_parse_qs = ast.literal_eval(userdata)

        # Could be a bot query
        if not ('access_token') in res_parse_qs:
            return None
        access_token = res_parse_qs['access_token']

        params = {}
        params['oauth2_access_token'] = access_token
        params["format"] = "json"
        fields = ":(first-name,last-name,email-address,public-profile-url,summary,id,picture-url)"
        url = "https://api.linkedin.com/v1/people/~" + fields + "?" + urllib.urlencode(params)

        linkedin_data = urllib.urlopen(url).read()
        linkedin_data = ast.literal_eval(linkedin_data)

        #  linkedin_data = ['id'], ['firstName'], ['lastName'], ['emailAddress'], ['pictureUrl'], ['publicProfileUrl'], ['summary']
        if not linkedin_data:
            return None

        try:
            same_email_user = UserProfile.objects.get(email=linkedin_data.get('emailAddress', None))
        except:
            same_email_user = None

        uid = linkedin_data.get('id')

        if user.is_anonymous() and not same_email_user:
            try:
                linkedin_user = LinkedinUserProfile.objects.get(linkedin_uid=uid)
                linkedin_user.accesstoken = access_token
                linkedin_user.save()
                return linkedin_user.user
            except LinkedinUserProfile.DoesNotExist:
                username = uid

                userProfile = UserProfile.objects.create(username=username)
                userProfile.first_name = linkedin_data.get('firstName')
                userProfile.last_name = linkedin_data.get('lastName')
                userProfile.email = linkedin_data.get('emailAddress', None)
                userProfile.about = linkedin_data.get('summary')
                userProfile.isVerified_email = True
                userProfile.save()
                userProfile.linkedin_link = linkedin_data.get('publicProfileUrl', None)

                img = urllib.urlretrieve(linkedin_data.get('pictureUrl'))
                userProfile.profile_picture.save("LinkedIn-profile.jpg", File(open(img[0])))
                urllib.urlcleanup()

                from django.contrib.auth.hashers import make_password
                raw_pass = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(12))
                tmp_pass = make_password(raw_pass)
                userProfile.password = tmp_pass
                userProfile.save()

                linkedin_user = LinkedinUserProfile(linkedin_uid=uid)
                linkedin_user.profile_image_url = linkedin_data.get('pictureUrl')
                linkedin_user.user = userProfile
                linkedin_user.email = linkedin_data.get('emailAddress')
                linkedin_user.url = linkedin_data.get('publicProfileUrl')
                linkedin_user.accesstoken = access_token
                linkedin_user.about_me = linkedin_data.get('summary')
                linkedin_user.save()

                return userProfile
        else:
            try:
                if same_email_user:
                    user = same_email_user
                user_linkedin = LinkedinUserProfile.objects.get(user=user)
                if user_linkedin.linkedin_uid == uid:
                    return user_linkedin.user
                else:
                    request.session['linkedin_accesstoken'] = access_token
                    next = request.session['next'] or ""
                    if next:
                        del request.session['next']
                        return HttpResponseRedirect(next)
                    else:
                        return HttpResponseRedirect(reverse('home'))
                        # return HttpResponseRedirect(reverse('sync_facebook'))

            except LinkedinUserProfile.DoesNotExist:
                try:
                    user_linkedin = LinkedinUserProfile.objects.get(linkedin_uid=uid)
                    request.session['linkedin_accesstoken'] = access_token
                    next = request.session['next'] or ""
                    if next:
                        del request.session['next']
                        return HttpResponseRedirect(next)
                    else:
                        return HttpResponseRedirect(reverse('home'))
                        # return HttpResponseRedirect(reverse('sync_facebook'))

                except LinkedinProfile.DoesNotExist:
                    linkedin_profile = LinkedinUserProfile(linkedin_uid=uid)
                    linkedin_user.profile_image_url = linkedin_data.get('pictureUrl')
                    linkedin_user.user = userProfile
                    linkedin_user.email = linkedin_data.get('emailAddress')
                    linkedin_user.url = linkedin_data.get('publicProfileUrl')
                    linkedin_user.accesstoken = access_token
                    linkedin_user.about_me = linkedin_data.get('summary')
                    linkedin_profile.save()

                    return fb_profile.user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
