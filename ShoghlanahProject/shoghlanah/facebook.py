from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
# import FacebookSDK as facebook
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
import logging
import urllib
from shoghlanah.models import *
import requests
from django.core.files import File
from django.conf import settings
import random
import string
from views import import_simplejson
json = import_simplejson()

CONSUMER_KEY = getattr(settings, 'FACEBOOK_ID', '')
CONSUMER_SECRET = getattr(settings, 'FACEBOOK_SECRET', '')
FACEBOOK_PERMISSIONS = getattr(settings, 'FACEBOOK_EXTENDED_PERMISSIONS', '')
LOGIN_REDIRECT_URL = getattr(settings, 'LOGIN_REDIRECT_URL', '')
DEPLOYED_ADDRESS = getattr(settings, 'DEPLOYED_ADDRESS', '')
SCOPE_SEPARATOR = ' '

MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT', '')


@login_required
def post_task_fb(request, task):
    try:
        fb_user = FacebookUserProfile.objects.get(user=request.user)
    except FacebookUserProfile.DoesNotExist:
        return HttpResponseRedirect(reverse('facebook_login'))
    payload = {'access_token': fb_user.accesstoken, "shoghlanah":  DEPLOYED_ADDRESS + 'task/' + str(task.id) + '/'}
    url = "https://graph.facebook.com/me/shoghlanah:post"
    if not DEPLOYED_ADDRESS == 'http://www.shoghlanah.com/':
        url = "https://graph.facebook.com/me/shoghlanah-test:post"
    m = requests.post(url, params=payload)
    # graph = facebook.GraphAPI(fb_user.accesstoken)
    # graph.put_wall_post(message="check out this task.", profile_id="830060503")
    return HttpResponse(m.json['error']['message'])


@login_required
def social_invite(request):
    from django.core.mail import send_mail
    to = []
    subject = "Invitation to join Shoghlanah"
    from_email = settings.EMAIL_HOST_USER
    msg = "Join Shoghlanah"
    dic = {}
    dic['sender'] = UserProfile.objects.get(email=request.user.email)
    for elem in request.POST:
        if elem.startswith('facebook'):
            to.append(elem[9:] + '@facebook.com')
    try:
        send_mail(subject, msg, from_email, to)
        return HttpResponse("Invitation sent successfully")
    except:
        return HttpResponse("Error sending invitaion")


@login_required
def search_filter(request):
    query = request.POST.get('query', '')


@login_required
def sync_friends(request):
    user = request.user
    access_token = ''
    if 'fb_accesstoken' in request.session:
        access_token = request.session['fb_accesstoken']
        del request.session['fb_accesstoken']
    else:
        try:
            fb_user = FacebookUserProfile.objects.get(user=user)
            access_token = fb_user.accesstoken
        except FacebookUserProfile.DoesNotExist:
            request.session['next'] = reverse('shoghlanah.facebook.sync_friends')
            return HttpResponseRedirect(reverse('facebook_login'))

    payload = {'access_token': access_token, "fields": "username, picture, name"}
    results = requests.get("https://graph.facebook.com/me/friends", params=payload)
    fb_friends = results.json["data"]

    users_to_follow = []
    users_to_invite = []
    users_to_invite_names = []
    zipped_to_invite_users_names = []

    for x in fb_friends:
        try:
            fup = FacebookUserProfile.objects.get(facebook_uid=x["id"])
            users_to_follow.append(fup.user)
        except FacebookUserProfile.DoesNotExist:  # means that friend is not in Shoghlanah
            if 'username' in x:
                users_to_invite.append(x)
                users_to_invite_names.append(x[u'name'])

    if len(users_to_follow) > 0:
        return render_to_response('renderPeople.html', {'users': users_to_follow, 'sync_social': 'facebook'}, RequestContext(request))
    elif len(users_to_follow) == 0:
        zipped_to_invite_users_names = zip(users_to_invite, users_to_invite_names)
        return render_to_response('renderSocialPeople.html', {'users': zipped_to_invite_users_names, 'invite_social': 'facebook'}, RequestContext(request))


@login_required
def facebook_disconnect(request):
    userprofile = UserProfile.objects.get(username=request.user.username)
    userprofile.facebook_link = None
    userprofile.save()
    next = request.META.get('HTTP_REFERER', reverse('home'))
    try:
        FacebookUserProfile.objects.get(user=userprofile).delete()
    except FacebookUserProfile.DoesNotExist:
        return HttpResponseRedirect(next)
    return HttpResponseRedirect(next)


def facebook_login(request):
        if request.REQUEST.get("device"):
            device = request.REQUEST.get("device")
        else:
            device = "user-agent"

        params = {}
        params["client_id"] = CONSUMER_KEY
        params["redirect_uri"] = request.build_absolute_uri(reverse("facebook_login_done"))
        params['scope'] = SCOPE_SEPARATOR.join(FACEBOOK_PERMISSIONS)
        params["device"] = device

        url = "https://graph.facebook.com/oauth/authorize?" + urllib.urlencode(params)
        if 'HTTP_REFERER' in request.META:
            request.session['next'] = request.META['HTTP_REFERER']
        return HttpResponseRedirect(url)


def facebook_login_done(request):
    denied = request.GET.get('error', None)
    result = None
    if not denied:
        result = authenticate(request=request)

    if not result:
        logging.debug("Facebook Backend: Couldn't authenticate user with Django, redirecting to Register page")
        return redirect(reverse('home'))

    if isinstance(result, UserProfile):
        if result.is_active:
            result.facebook_link = FacebookUserProfile.objects.get(user=result).url
            result.save()
            login(request, result)
            logging.debug("Facebook Backend: Successfully logged in with Facebook!")
            if 'next' in request.session:
                next = request.session['next']
                del request.session['next']
                request.session['Social'] = "facebook"
                return redirect(next, RequestContext(request))
            else:
                return HttpResponseRedirect(reverse('home'))
    else:
        return result


def del_dict_key(src_dict, key):
    if key in src_dict:
        del src_dict[key]


class FacebookBackend:
    def authenticate(self, request):
        user = request.user or None
        access_token = None
        # assume logging in normal way
        params = {}
        params["client_id"] = CONSUMER_KEY
        params["client_secret"] = CONSUMER_SECRET
        params["redirect_uri"] = request.build_absolute_uri(reverse("facebook_login_done"))
        params["code"] = request.GET.get('code', '')

        url = ("https://graph.facebook.com/oauth/access_token?"
               + urllib.urlencode(params))
        from cgi import parse_qs
        userdata = urllib.urlopen(url).read()
        res_parse_qs = parse_qs(userdata)
        # Could be a bot query
        if not ('access_token') in res_parse_qs:
            return None
        access_token = res_parse_qs['access_token'][-1]

        url = "https://graph.facebook.com/me?access_token=" + access_token

        fb_data = json.loads(urllib.urlopen(url).read())
        uid = fb_data["id"]

        if not fb_data:
            return None

        try:
            same_email_user = UserProfile.objects.get(email=fb_data.get('email', None))
        except:
            same_email_user = None

        if user.is_anonymous() and not same_email_user:
            try:
                fb_user = FacebookUserProfile.objects.get(facebook_uid=uid)
                fb_user.accesstoken = access_token
                fb_user.save()
                return fb_user.user
            except FacebookUserProfile.DoesNotExist:
                fb_picture_url = "http://graph.facebook.com/%s/picture?type=large" % uid

                username = fb_data.get('username')
                if not username:
                    username = uid
                userProfile = UserProfile.objects.create(username=username)
                userProfile.first_name = fb_data['first_name']
                userProfile.last_name = fb_data['last_name']
                if fb_data['gender'] == "male":
                    userProfile.gender = 'M'
                else:
                    if fb_data['gender'] == "female":
                        userProfile.gender = 'F'
                userProfile.email = fb_data.get('email', None)
                userProfile.isVerified_email = True
                userProfile.location = fb_data.get('location', fb_data).get('name', None)
                userProfile.save()

                img = urllib.urlretrieve(fb_picture_url)
                userProfile.profile_picture.save("Facebook-profile.jpg", File(open(img[0])))
                urllib.urlcleanup()

                userProfile.facebook_link = fb_data.get('link', None)
                from django.contrib.auth.hashers import make_password
                raw_pass = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(12))
                tmp_pass = make_password(raw_pass)
                userProfile.password = tmp_pass
                userProfile.save()

                fb_profile = FacebookUserProfile(facebook_uid=uid, user=userProfile, email=fb_data['email'],
                    url=fb_data['link'], location=userProfile.location, accesstoken=access_token)
                fb_profile.save()

                return userProfile
        else:
            try:
                if same_email_user:
                    user = same_email_user
                user_facebook = FacebookUserProfile.objects.get(user=user)
                if user_facebook.facebook_uid == uid:
                    return user_facebook.user
                else:
                    request.session['fb_accesstoken'] = access_token
                    next = request.session['next'] or ""
                    if next:
                        del request.session['next']
                        return HttpResponseRedirect(next)
                    else:
                        return HttpResponseRedirect(reverse('sync_facebook'))
            except FacebookUserProfile.DoesNotExist:
                try:
                    user_facebook = FacebookUserProfile.objects.get(facebook_uid=uid)
                    request.session['fb_accesstoken'] = access_token
                    next = request.session['next'] or ""
                    if next:
                        del request.session['next']
                        return HttpResponseRedirect(next)
                    else:
                        return HttpResponseRedirect(reverse('sync_facebook'))
                except FacebookUserProfile.DoesNotExist:
                    fb_profile = FacebookUserProfile(facebook_uid=uid, user=UserProfile.objects.get(username=user.username), email=fb_data['email'],
                    url=fb_data['link'], location=fb_data.get('location', fb_data).get('name', None), accesstoken=access_token)
                    fb_profile.save()
                    return fb_profile.user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
