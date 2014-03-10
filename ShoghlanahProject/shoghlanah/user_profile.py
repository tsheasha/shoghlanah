# -*- coding: utf-8 -*-
from shoghlanah.models import *
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import Http404
from django.contrib.auth.decorators import login_required
from forms import uploadProfilePicture
from forms import uploadCoverPicture
from django.http import HttpResponseRedirect, HttpResponse
from shoghlanah.live_stream import add_action
from django.utils import translation
from userprofiles.contrib.profiles.views import get_followers
from ShoghlanahProject import settings
from notification.models import Notice
from notification.models import *
from actstream.models import Action
import pusher
import random
from userprofiles.contrib.emailverification.views import email_change, password_change_save, email_change_save

pusher.app_id = settings.PUSHER_APP_ID
pusher.key = settings.PUSHER_KEY
pusher.secret = settings.PUSHER_SECRET

p = pusher.Pusher()


@login_required
def edit_view(request):
    """
    Dont forget the documentation.
    """
    # calculate_profile_completion(request)
    editor = UserProfile.objects.get(username=request.user.username)
    form = uploadProfilePicture()
    coverform = uploadCoverPicture()
    facebook_link = ''
    twitter_link = ''
    google_plus_link = ''
    linkedin_link = ''
    default = False

    if not editor.facebook_link is None:
        facebook_link = editor.facebook_link

    if not editor.twitter_link is None:
            twitter_link = editor.twitter_link

    if not editor.linkedin_link is None:
            linkedin_link = editor.linkedin_link

    if not editor.google_plus_link is None:
        google_plus_link = editor.google_plus_link

    if str(editor.profile_picture)[9:24] == 'ProfileDefaults':
        default = True

    try:
        if "password_change" in request.path:
            new_context = password_change_save(request)
            new_context.update({'active_tab':2})
        elif "email_change" in request.path:
            new_context = email_change_save(request)
            new_context.update({'active_tab':2})
        else:
            new_context = email_change(request)
            new_context.update({'active_tab':1})
        new_context.update({'default':default, 'editor':editor, 'form':form, 'coverform':coverform, 'facebook_link':facebook_link, 'twitter_link':twitter_link, 'linkedin_link':linkedin_link, 'google_plus_link':google_plus_link})
    except AttributeError:
        return new_context
        
    return render_to_response("userprofiles/edit_profile.html", new_context, RequestContext(request))


@login_required
def edit(request):
    """
    Dont forget the documentation.
    """
    user_name = request.user.username
    editor = UserProfile.objects.get(username=request.user.username)

    try:
        facebook_link = ''
        twitter_link = ''
        google_plus_link = ''
        linkedin_link = ''

        if 'google_plus' in request.POST:
            if not request.POST['google_plus'] is None:
                google_plus_link = request.POST['google_plus']

        if 'linkedin' in request.POST:
            if not request.POST['linkedin'] is None:
                linkedin_link = request.POST['linkedin']

        if 'gender' in request.POST:
            if request.POST['gender'] == "male":
                editor.gender = 'M'
            else:
                editor.gender = 'F'
            editor.save()

        if not request.POST['first_name'] == "":
            if not request.POST['first_name'] == editor.first_name:
                editor.first_name = request.POST['first_name']
                if editor.gender == 'F':
                    add_action(UserProfile.objects.get(username=user_name), "edited_profile", UserProfile.objects.get(username=user_name), 'changed her first name', UserProfile.objects.get(username=user_name))
                else:
                    add_action(UserProfile.objects.get(username=user_name), "edited_profile", UserProfile.objects.get(username=user_name), 'changed his first name', UserProfile.objects.get(username=user_name))
        else:
            raise ValidationError('Empty First Name')

        if not request.POST['last_name'] == "":
            if not request.POST['last_name'] == editor.last_name:
                editor.last_name = request.POST['last_name']
                if editor.gender == 'F':
                    add_action(UserProfile.objects.get(username=user_name), "edited_profile", UserProfile.objects.get(username=user_name), 'changed her last name', UserProfile.objects.get(username=user_name))
                else:
                    add_action(UserProfile.objects.get(username=user_name), "edited_profile", UserProfile.objects.get(username=user_name), 'changed his last name', UserProfile.objects.get(username=user_name))
        else:
            raise ValidationError('Empty Last Name')

        if not request.POST['job_title'] == editor.job_title:
            editor.job_title = request.POST['job_title']
            if editor.gender == 'F':
                add_action(UserProfile.objects.get(username=user_name), "edited_profile", UserProfile.objects.get(username=user_name), 'changed her job title', UserProfile.objects.get(username=user_name))
            else:
                add_action(UserProfile.objects.get(username=user_name), "edited_profile", UserProfile.objects.get(username=user_name), 'changed his job title', UserProfile.objects.get(username=user_name))

        if not request.POST['mobile_number'] == editor.mobile_number:
            if request.POST['mobile_number'] == 11:
                editor.isVerified = False
                editor.isRequest_Verification = False
                if request.POST['mobile_number'] == "":
                    editor.mobile_number = None
                else:
                    editor.mobile_number = int(request.POST['mobile_number'])
                if editor.gender == 'F':
                    add_action(UserProfile.objects.get(username=user_name), "edited_profile", UserProfile.objects.get(username=user_name), 'changed her mobile number', UserProfile.objects.get(username=user_name))
                else:
                    add_action(UserProfile.objects.get(username=user_name), "edited_profile", UserProfile.objects.get(username=user_name), 'changed his mobile number', UserProfile.objects.get(username=user_name))

        if not request.POST['about_me'] == editor.about:
            editor.about = request.POST['about_me']
            if editor.gender == 'F':
                add_action(UserProfile.objects.get(username=user_name), "edited_profile", UserProfile.objects.get(username=user_name), "changed her 'About Me' info", UserProfile.objects.get(username=user_name))
            else:
                add_action(UserProfile.objects.get(username=user_name), "edited_profile", UserProfile.objects.get(username=user_name), "changed his 'About Me' info", UserProfile.objects.get(username=user_name))

        if not request.POST['where'] == editor.location:
            location = request.POST['where']
            city = ''
            if location is not None and len(location) > 0:
                temp_loc = location.split(',')
                if len(temp_loc) > 1:
                    city = temp_loc[len(temp_loc)-2].strip()
                else:
                    city = temp_loc[0].strip()
                if city.endswith('Governorate'):
                    city = city[:-len('Governorate')].strip()
            editor.location = location
            editor.city = city
            longitude = request.POST['lng']
            latitude = request.POST['lat']
            if longitude == '' or latitude == '' or city == '':
                longitude = 200.0
                latitude = 200.0
            editor.latitude = latitude
            editor.longitude = longitude
            if editor.gender == 'F':
                add_action(UserProfile.objects.get(username=user_name), "edited_profile", UserProfile.objects.get(username=user_name), 'changed her location', UserProfile.objects.get(username=user_name))
            else:
                add_action(UserProfile.objects.get(username=user_name), "edited_profile", UserProfile.objects.get(username=user_name), 'changed his location', UserProfile.objects.get(username=user_name))

        # Google+ Saving
        if editor.google_plus_link:
            if not request.POST['google_plus'] == editor.google_plus_link:
                editor.google_plus_link = google_plus_link
        else:
            if not google_plus_link == "":
                editor.google_plus_link = google_plus_link

        # LinkedIn Saving
        if editor.linkedin_link:
            if not request.POST['linkedin'] == editor.linkedin_link:
                editor.linkedin_link = linkedin_link
        else:
            if not linkedin_link == "":
                editor.linkedin_link = linkedin_link

        editor.tags = request.POST['skills']  # Skills editing part

        editor.save()

        if form.is_valid():
            if not image == editor.profile_picture:
                add_action(UserProfile.objects.get(username=user_name), "changed_profile_picture", UserProfile.objects.get(username=user_name), str(editor.profile_picture), UserProfile.objects.get(username=user_name))

        # calculate_profile_completion(request)

    except ValidationError as e:
        raise e
    except ValueError:
        raise Http404("Phone Number cant be a string")
    return redirect('/accounts/profile/' + request.user.username + '/')

@login_required
def edit_profile_pic(request, user_name):
    print request.FILES
    editor = UserProfile.objects.get(username=request.user.username)

    form = uploadProfilePicture(request.POST, request.FILES)
    changeimage = False
    if form.is_valid():
        image = form.cleaned_data.get('image')
        if not image == editor.profile_picture:
            changeimage = True
            editor.profile_picture = image
            editor.save()
            add_action(UserProfile.objects.get(username=user_name), "changed_profile_picture", UserProfile.objects.get(username=user_name), str(editor.profile_picture), UserProfile.objects.get(username=user_name))
    return redirect('/accounts/profile/' + request.user.username + '/')

@login_required
def edit_cover_photo(request, user_name):
    editor = UserProfile.objects.get(username=request.user.username)

    coverform = uploadCoverPicture(request.POST, request.FILES)
    changecover = False
    if coverform.is_valid():
        image = coverform.cleaned_data.get('coverimage')
        if not image == editor.cover_picture:
            changecover = True
            editor.cover_picture = image
            editor.save()
            # add_action(UserProfile.objects.get(username=user_name), "changed_cover_picture", UserProfile.objects.get(username=user_name), str(editor.cover_picture), UserProfile.objects.get(username=user_name))
    return redirect('/accounts/profile/' + request.user.username + '/')


@login_required
def follow(request, user_name):
    if request.method == 'GET':
        userprofile = UserProfile.objects.get(username=user_name)
        requestuser = UserProfile.objects.get(username=request.user.username)

        if(request.user != userprofile):
            mutual_fol = []
            mutual = get_followers(request, user_name)['followers']
            for item in mutual:
                mutual_fol += [item.follower]
            Follow.objects.get_or_create(follower=requestuser, followed=userprofile)
            sender_profile = UserProfile.objects.get(pk=request.user.id)
            sender = User.objects.get(pk=request.user.id)
            the_message = sender.first_name + ' is now following you'
            if sender_profile.gender == 'F':
                the_message_arabic = sender.first_name + " تتابعك الآن".decode("utf-8")
                receivers = [User.objects.get(username=user_name)]
                the_link = '/accounts/profile/' + str(sender.username)
                send_now(receivers, sender, 'new_follower', the_message, the_message_arabic, the_link)
                for receiver in receivers:
                    if not receiver.id == request.user.id:
                        notices = Notice.objects.filter(recipient=receiver, sender=sender, message=the_message, message_arabic=the_message_arabic, link=the_link)
                        p['channel_' + str(receiver.username)].trigger('notification', {
                            'message': '<a href="/notifications/' + str(sender.username) + '/">' + sender.first_name + ' ' + sender.last_name + ' is now following you.</a>',
                            'name': '<a href="/notifications/' + str(notices[0].id) + '/">' + sender.first_name + ' ' + sender.last_name + '</a>',
                            'translated': 'is now following you ',
                            'link': ' ',
                            'the_title': ' ',
                            'the_title_translated': 'You have a new follower',
                        })
            else:
                the_message_arabic = sender.first_name + " يتابعك الآن".decode("utf-8")
                receivers = [User.objects.get(username=user_name)]
                the_link = '/accounts/profile/' + str(sender.username)
                send_now(receivers, sender, 'new_follower', the_message, the_message_arabic, the_link)
                for receiver in receivers:
                    if not receiver.id == request.user.id:
                        notices = Notice.objects.filter(recipient=receiver, sender=sender, message=the_message, message_arabic=the_message_arabic, link=the_link)
                        p['channel_' + str(receiver.username)].trigger('notification', {
                            'message': '<a href="/notifications/' + str(sender.username) + '/">' + sender.first_name + ' ' + sender.last_name + ' is now following you.</a>',
                            'name': '<a href="/notifications/' + str(notices[0].id) + '/">' + sender.first_name + ' ' + sender.last_name + '</a>',
                            'translated': 'is now following you',
                            'link': ' ',
                            'the_title': ' ',
                            'the_title_translated': 'You have a new follower',
                        })

            actor = UserProfile.objects.get(username=request.user.username)
            target = UserProfile.objects.get(username=user_name)

            if isinstance(actor, UserProfile) and isinstance(target, UserProfile):
                add_action(actor, "followed", target, 'followed', target)

            return HttpResponse()
        return HttpResponse()


def unfollow(request, user_name):
    if request.method == 'GET':
        userprofile = UserProfile.objects.get(username=user_name)
        requestuser = UserProfile.objects.get(username=request.user.username)
        if(request.user != userprofile):
            Follow.objects.get(follower=requestuser, followed=userprofile).delete()
            actions = Action.objects.filter(actor_object_id=requestuser.id, target_object_id=userprofile.id, verb="followed")
            for item in actions:
                p['stream'].trigger('mainStream', {'follow': (str(item.id)), })
                item.delete()
            return HttpResponse()
        return HttpResponse()


def delete_profile_picture(request, user_name):
    editor = UserProfile.objects.get(id=request.user.id)
    profile_pictures = ["../media/ProfileDefaults/profile_pic_default.png", "../media/ProfileDefaults/profile_pic_default2.png", "../media/ProfileDefaults/profile_pic_default3.png", "../media/ProfileDefaults/profile_pic_default4.png", "../media/ProfileDefaults/profile_pic_default5.png"]
    editor.profile_picture = profile_pictures[int(random.random() * len(profile_pictures))]
    editor.save()
    return redirect('/accounts/profile/' + request.user.username + '/')


def delete_cover_picture(request, user_name):
    editor = UserProfile.objects.get(id=request.user.id)
    editor.cover_picture = None
    editor.save()
    return redirect('/accounts/profile/' + request.user.username + '/')


def verify_mobile_number(request, user_name):
    requestor = UserProfile.objects.get(username=user_name)
    if not request.POST['mobile_number'] == "":
        try:
            requestor.mobile_number = request.POST['mobile_number']
            requestor.isVerified = False
            requestor.isRequest_Verification = True
            requestor.save()
        except ValueError:
            raise Http404("Phone Number cant be a string")
    return HttpResponse()


def verify_email(request, user_name):
    requestor = UserProfile.objects.get(username=user_name)
    if not request.POST['email'] == "":
        requestor.email = request.POST['email']
        requestor.isVerified_email = False
        requestor.isRequest_Verification_email = True
        requestor.save()
    return HttpResponse()


def check_number_duplicates(request):
    """
    Dont forget the documentation.
    """
    mobile_number = request.POST['mobile_number']
    if UserProfile.objects.filter(mobile_number=mobile_number).exclude(username=request.user.username):
        return HttpResponse("true")
    else:
        return HttpResponse("false")


def send_invitation(request):
    from views import email_html
    subject = "Invitation to join Shoghlanah"
    to = request.GET['to_email'].split(",")
    [x.lower() for x in to]
    from_email = settings.EMAIL_HOST_USER
    msg = request.GET['text']
    dic = {}
    dic['sender'] = UserProfile.objects.get(email=request.user.email)
    email_html(subject=subject, from_email=from_email, to=to, msg=msg, dic=dic)
    return HttpResponseRedirect(request.GET['next'])


def clearnewnotifications(request):
    for notice in Notice.objects.notices_for(request.user.id, unseen=True):
        notice.unseen = False
        notice.save()
    return HttpResponse(" ")
