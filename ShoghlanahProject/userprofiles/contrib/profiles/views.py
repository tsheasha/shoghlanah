# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render, redirect
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from userprofiles import settings as up_settings
from userprofiles.utils import get_form_class
from shoghlanah.models import *
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from shoghlanah.forms import uploadProfilePicture
from shoghlanah.forms import uploadCoverPicture


@login_required
def profile(request, user_name, more=False, to_add=0):
    from shoghlanah.live_stream import profile_stream
    # calculate_profile_completion(request)
    output_dict = {'user': request.user}
    output_dict.update({'home': False})
    editor = UserProfile.objects.get(username=request.user.username)
    form = uploadProfilePicture()
    coverform = uploadCoverPicture()
    output_dict.update({'editor': editor, 'form': form, 'coverform': coverform})
    userprofile = UserProfile.objects.filter(username=user_name)
    if len(userprofile) > 0:
        userprofile = userprofile[0]
        if not userprofile.email:
            return HttpResponseRedirect(reverse('userprofiles_email_change'))
        if not userprofile.first_name or not userprofile.last_name:
            return HttpResponseRedirect(reverse('edit_profile'))
    else:
        return redirect('/accounts/register/', RequestContext(request))
    output_dict.update({'userprofile': userprofile})
    following = isFollowing(request.user, userprofile)
    output_dict.update({'isFollowing': following})
    all_tasks = Task.objects.filter(user=userprofile)
    all_tasks_no = Task.objects.filter(user=userprofile).count()

    if 'to_add' in request.POST:
        to_add = request.POST['to_add']

    if user_name != request.user.username:
        output_dict.update({'viewed_user': userprofile})
    else:
        output_dict.update({'viewed_user': request.user})

    stream = list(reversed(profile_stream(output_dict['viewed_user'])))

    task_stream = stream

    if len(stream) > 10:
        if (11+to_add) > len(stream):
            stream = stream[0:]
        else:
            stream = stream[0:10+to_add]
        output_dict.update({'stream': stream})
    else:
        output_dict.update({'stream': stream})
    output_dict.update(get_followers(request, user_name))
    p = Photo.objects.filter(owner__username=user_name)
    products = Product.objects.filter(user__id=userprofile.id)
    output_dict.update({'products': products})
    output_dict.update({'Photos': p})
    output_dict.update({'all_followers': Follow.objects.filter(followed=userprofile)})
    output_dict.update({'all_following': Follow.objects.filter(follower=userprofile)})
    output_dict.update({'reviews': Review.objects.filter(reviewed=userprofile)})
    output_dict.update({'all_tasks_no': all_tasks_no})
    output_dict.update({'results': all_tasks})
    output_dict.update({'task_stream': task_stream})
    output_dict.update({'profile': True})
    return render_to_response('userprofiles/profile.html', output_dict, context_instance=RequestContext(request))


def get_followers(request, user_name):
    #if viewing his profile, then he sees people he's following
    user_follow = Follow.objects.filter(follower__id=request.user.id)

    if user_name != request.user.username:
        #if the user is viewing other user's profile, then he sees their mutual followers
        viewed_user_following = Follow.objects.filter(follower__username=user_name)
        mutual = []

        viewed_user_following_list = []
        for f in viewed_user_following:
            viewed_user_following_list.append(f.followed)

        for follow in user_follow:
            if follow.followed in viewed_user_following_list:
                mutual.append(follow.followed)
        return {'followers': mutual}

    user_following = []
    for follow in user_follow:
        user_following.append(follow.followed)
    return {'followers': user_following}


def get_gallery(request, user_name):
    photos = Photo.objects.filter(owner__username=user_name)
    userprofile = UserProfile.objects.get(username=user_name)
    output_dict = {'Photos': photos}
    output_dict.update({'viewed_user': userprofile})
    return render_to_response('userprofiles/portfolio.html', output_dict, context_instance=RequestContext(request))


@login_required
def profile_change(request):
    ProfileForm = get_form_class(up_settings.PROFILE_FORM)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES,
            instance=request.user.get_profile())
        if form.is_valid():
            profile = form.save()
            messages.success(request, _(u'Profile changed'))
            return redirect(up_settings.PROFILE_CHANGE_DONE_URL)
    else:
        if up_settings.REGISTRATION_FULLNAME:
            form = ProfileForm(instance=request.user.get_profile(), initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email
            })
        else:
            form = ProfileForm(instance=request.user.get_profile())

    return render(request, 'userprofiles/profile_change.html', {'form': form})


def isFollowing(follower, followed):
    try:
        Follow.objects.get(follower=follower, followed=followed)
        return True
    except:
        return False


def filter_stream(request):
    """
    This method serves to filter the stream of a user according to a given
    Action to make the stream easier to browse. Filtration results should be
    shrinked like in the normal stream to load more when a certain limit is reached.
    """
    from shoghlanah.live_stream import get_stream
    verb = ""
    if 'verb' in request.POST:
        verb = request.POST['verb']

    user_name = ''

    if 'user_name' in request.POST:
        user_name = request.POST['user_name']

    if request.user.is_authenticated():
        if request.user.username == user_name:
            if request.user.is_active:
                user = UserProfile.objects.get(id=request.user.id)
        else:
                user = UserProfile.objects.get(username=user_name)

        init_res = get_stream(request, user, verb, profile=True)
        stream = list(init_res['stream'])
        latest = []
        alt_verb = ""

        if verb == 'task':
            verb = 'task_post'
            alt_verb = 'task_assigned'

        if verb == 'followed':
            verb = 'followed'
            alt_verb = 'followed_skill'

        if verb == 'photo':
            verb = 'changed_profile_picture'
            alt_verb = 'upload_photo'

        if verb == 'edited_profile':
            alt_verb = 'joined'

        for item in stream:
            if item.verb == verb or item.verb == alt_verb:
                latest.append(item)
        output_dict = {'filtered_stream': latest}
        output_dict.update({'filter': True})
        return render_to_response("filter.html", output_dict, RequestContext(request))
