from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from shoghlanah.models import *
import urllib
import logging
from django.core.files import File
import tweepy
from forms import InfoCheckForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
import random
import string

CONSUMER_KEY = getattr(settings, 'TWITTER_KEY', '')
CONSUMER_SECRET = getattr(settings, 'TWITTER_SECRET', '')
DEPLOYED_ADDRESS = getattr(settings, 'DEPLOYED_ADDRESS', '')


@login_required
def tweet(request, status):
    try:
        twitter_user = TwitterUserProfile.objects.get(user=request.user)
    except TwitterUserProfile.DoesNotExist:
        request.session['next'] = reverse('sync_twitter')
        return HttpResponseRedirect(reverse('twitter_login'))
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(twitter_user.access_token, twitter_user.access_secret)
    api = tweepy.API(auth)
    try:
        api.update_status(status=status)
        return HttpResponse("tweet sent successfully")
    except:
        return HttpResponse("direct message sending failed")


@login_required
def direct_message(request, to, msg):
    try:
        twitter_user = TwitterUserProfile.objects.get(user=request.user)
    except TwitterUserProfile.DoesNotExist:
        request.session['next'] = reverse('sync_twitter')
        return HttpResponseRedirect(reverse('twitter_login'))

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(twitter_user.access_token, twitter_user.access_secret)
    api = tweepy.API(auth)

    to_user = request.POST['user_to'] or to
    message = request.POST['msg'] or msg
    try:
        api.send_direct_message(user_id=to_user, text=message)
        return True
    except:
        return False


@login_required
def social_invite(request):
    msg = "Join Shoghlanah"
    for elem in request.POST:
        if elem.startswith('twitter'):
            to = elem[8:]
            if not direct_message(request, to, msg):
                return HttpResponse("Error sending invitaion")
    return HttpResponse("Invitation sent successfully")


@login_required
def sync_friends(request):
    access_token = ''
    access_secret = ''
    if 'access_token' in request.session and 'access_secret' in request.session:
        access_token = request.session['access_token']
        access_secret = request.session['access_secret']
        del request.session['access_token']
        del request.session['access_secret']
    else:
        try:
            twitter_user = TwitterUserProfile.objects.get(user=request.user)
            access_token = twitter_user.access_token
            access_secret = twitter_user.access_secret
        except TwitterUserProfile.DoesNotExist:
            request.session['next'] = reverse('shoghlanah.twitter.sync_friends')
            return HttpResponseRedirect(reverse('twitter_login'))

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)

    users_to_follow = []
    users_to_invite = []
    users_to_invite_ids = []
    zipped_users_to_invite = None

    for friend in api.me().friends():
        try:
            tup = TwitterUserProfile.objects.get(screen_name=friend.screen_name)
            users_to_follow.append(tup.user)
        except TwitterUserProfile.DoesNotExist:  # means that friend is not in Shoghlanah
            users_to_invite.append(friend)
            users_to_invite_ids.append(friend.id)

    if len(users_to_follow) > 0:
        return render_to_response('renderPeople.html', {'users': users_to_follow, 'sync_social': 'twitter'}, RequestContext(request))
    elif len(users_to_follow) == 0:
        zipped_users_to_invite = zip(users_to_invite, users_to_invite_ids)
        return render_to_response('renderSocialPeople.html', {'users': zipped_users_to_invite, 'invite_social': 'twitter'}, RequestContext(request))


def twitter_disconnect(request):
    userprofile = UserProfile.objects.get(username=request.user.username)
    userprofile.twitter_link = None
    userprofile.save()
    next = request.META.get('HTTP_REFERER', reverse('home'))
    try:
        TwitterUserProfile.objects.get(user=userprofile).delete()
    except TwitterUserProfile.DoesNotExist:
        return HttpResponseRedirect(next)
    return HttpResponseRedirect(next)


def twitter_login(request):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, request.build_absolute_uri(reverse("twitter_login_done")))
    redirect_url = auth.get_authorization_url(True)
    request.session['request_token.key'] = auth.request_token.key
    request.session['request_token.secret'] = auth.request_token.secret
    if 'HTTP_REFERER' in request.META:
            request.session['next'] = request.META['HTTP_REFERER']
    return HttpResponseRedirect(redirect_url)


def twitter_login_done(request):
    denied = request.GET.get('denied', None)
    result = None
    if not denied:
        result = authenticate(request=request)

    if not result:
        logging.debug("Twitter Backend: Couldn't authenticate user with Django, redirecting to Register page")
        return redirect(reverse('home'))

    if isinstance(result, UserProfile):
        if result.is_active:
            result.twitter_link = TwitterUserProfile.objects.get(user=result).url
            result.save()
            login(request, result)
            logging.debug("Twitter Backend: Successfully logged in with Twitter!")
            if 'next' in request.session:
                next = request.session['next']
                del request.session['next']
                request.session['Social'] = "twitter"
                return redirect(next, RequestContext(request))
            else:
                return HttpResponseRedirect(reverse('home'))
    else:
        return result


class TwitterBackend:
    def authenticate(self, request):
        user = request.user or None
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        # Get access token
        verifier = request.GET.get('oauth_verifier')
        auth.set_request_token(request.session['request_token.key'], request.session['request_token.secret'])
        del request.session['request_token.secret']
        del request.session['request_token.key']
        auth.get_access_token(verifier)
        # Construct the API instance
        api = tweepy.API(auth)

        if user.is_anonymous():
            try:
                twitter_user = TwitterUserProfile.objects.get(screen_name=api.me().screen_name)
                return twitter_user.user
            except TwitterUserProfile.DoesNotExist:
                userProfile = UserProfile.objects.create(username=api.me().screen_name)
                userProfile.first_name = api.me().screen_name
                userProfile.location = api.me().location
                userProfile.save()

                img = urllib.urlretrieve(api.me().profile_image_url)
                userProfile.profile_picture.save("Twitter-profile.jpg", File(open(img[0])))
                urllib.urlcleanup()

                userProfile.twitter_link = 'https://twitter.com/' + api.me().screen_name
                from django.contrib.auth.hashers import make_password
                raw_pass = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(12))
                tmp_pass = make_password(raw_pass)
                userProfile.password = tmp_pass
                userProfile.save()

                twitter_user = TwitterUserProfile.objects.create(user=userProfile)
                twitter_user.screen_name = api.me().screen_name
                twitter_user.profile_image_url = userProfile.profile_picture
                twitter_user.location = api.me().location
                twitter_user.url = 'https://twitter.com/' + api.me().screen_name
                twitter_user.access_token = auth.access_token.key
                twitter_user.access_secret = auth.access_token.secret
                twitter_user.save()
                return userProfile
        else:
            try:
                user_twitter = TwitterUserProfile.objects.get(user=user)
                if user_twitter.screen_name == api.me().screen_name:
                    return user_twitter.user
                else:
                    request.session['access_token'] = auth.access_token.key
                    request.session['access_secret'] = auth.access_token.secret
                    next = request.session['next'] or ""
                    if next:
                        del request.session['next']
                        return HttpResponseRedirect(next)
                    else:
                        return HttpResponseRedirect(reverse('sync_twitter'))

            except TwitterUserProfile.DoesNotExist:
                try:
                    user_twitter = TwitterUserProfile.objects.get(screen_name=api.me().screen_name)
                    request.session['access_token'] = auth.access_token.key
                    request.session['access_secret'] = auth.access_token.secret
                    next = request.session['next'] or ""
                    if next:
                        del request.session['next']
                        return HttpResponseRedirect(next)
                    else:
                        return HttpResponseRedirect(reverse('sync_twitter'))
                except TwitterUserProfile.DoesNotExist:
                    twitter_user = TwitterUserProfile.objects.create(user=UserProfile.objects.get(username=user.username))
                    twitter_user.screen_name = api.me().screen_name
                    twitter_user.location = api.me().location
                    twitter_user.url = 'https://twitter.com/' + api.me().screen_name
                    twitter_user.access_token = auth.access_token.key
                    twitter_user.access_secret = auth.access_token.secret
                    twitter_user.save()
                    return twitter_user.user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None


def validateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
