from shoghlanah.models import *
from tagging.models import *
from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from notification.models import Notice
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from haystack.inputs import *
from haystack.query import SearchQuerySet
import pusher
from django.utils import translation
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from ShoghlanahProject import settings
from actstream.models import Action
from shoghlanah.live_stream import get_stream, profile_stream, get_discover_stream
from userprofiles.contrib.profiles.views import get_followers
from userprofiles import settings as up_settings
from userprofiles.utils import get_form_class
from django.core.urlresolvers import reverse

pusher.app_id = settings.PUSHER_APP_ID
pusher.key = settings.PUSHER_KEY
pusher.secret = settings.PUSHER_SECRET

p = pusher.Pusher()


def master(request, more=False):
    user = None
    if request.user.is_authenticated():
        if request.user.is_active:
            user = UserProfile.objects.filter(username=request.user.username)
            if(user):
                user = user[0]
                if not user.email:
                    return HttpResponseRedirect(reverse('userprofiles_email_change'))
                if not user.first_name or not user.last_name:
                    return HttpResponseRedirect(reverse('edit_profile'))
            else:
                msg = translation.gettext("Good try, Hack better ;)")
                return render(request, 'userprofiles/registration2.html', {'error_message': msg})
                #return render(request, 'userprofiles/registration.html', {'error_message': msg})
        else:
            msg = translation.gettext("This Email Hasn't Been Activated Yet.")
            #return render(request, 'userprofiles/registration.html', {'error_message': msg})
            return render(request, 'userprofiles/registration2.html', {'error_message': msg})
        custom = False
        if user is not None:
            following = Follow.objects.filter(follower__id=user.id)
            if following:
                custom = True
            if custom:
                output_dict = get_stream(request, user)
            else:
                output_dict = get_discover_stream(request)
        if custom:
            output_dict.update({'home': True})
            output_dict.update({'discover': "False"})
        else:
            output_dict.update({'tip': "True"})
            output_dict.update({'discover': "True"})
            output_dict.update({'home': True})
        return render_to_response("home.html", output_dict, RequestContext(request))
    else:
        return redirect('/accounts/register/', RequestContext(request))


def discover(request):
    output_dict = get_discover_stream(request)
    output_dict.update({'discover': "True"})
    output_dict.update({'home': True})
    return render_to_response("home.html", output_dict, RequestContext(request))


def load_more(request, profile=False):
    """
    This method loads more items to the stream if the stream had
    previously exceeded its 10 Actions limit, in order to make
    loading the stream faster.
    """
    to_add = 0
    user = UserProfile.objects.filter(id=request.user.id)
    if len(user) > 0:
        user = user[0]
    else:
        output_dict = {'more': False}
        return render_to_response("more.html", output_dict, RequestContext(request))

    stream = []

    if 'to_add' in request.POST:
        to_add = int(request.POST['to_add'])
    home = True
    if 'profile' in request.POST:
        profile = True
        home = False
    discover = False
    if 'discover' in request.POST:
        discover = True
        home = False
    if(request.POST.has_key('user_name')):
        user_name = request.POST['user_name']
        user = UserProfile.objects.filter(username=user_name)
        if len(user) > 0:
            user = user[0]
        else:
            output_dict = {'more' : False}
            return render_to_response("more.html", output_dict, RequestContext(request))
    if discover:
        task_stream = Action.objects.filter(verb="task_post")
        for item in task_stream:
            stream.append(item)
    else:                
        if not profile:
            follows = Follow.objects.filter(follower=user)
            for action in follows:
                if isinstance(action.followed_skill, Tag):
                    items = TaggedItem.objects.filter(tag=action.followed_skill)
                    for item in items:
                        if isinstance(item.object, Task):
                            stream.extend(Action.objects.filter(action_object_object_id=item.object.id))
            followers = get_followers(request, request.user.username)
            for item in followers['followers']:
                if item is not None:
                    if isinstance(item.followed, UserProfile):
                        stream += list(reversed(profile_stream(item.followed)))

        for item in stream:
            if item.actor is None:
                list(stream).remove(item)

        stream.extend(Action.objects.filter(actor_object_id=user.id))

        action_objects = Action.objects.filter(action_object_object_id=user.id)
        for obj in action_objects:
            if not isinstance(obj.action_object, UserProfile):
                action_objects = list(action_objects).remove(obj)
                if action_objects is None:
                    break

        if action_objects is not None:
            stream.extend(action_objects)

        target_objects = Action.objects.filter(target_object_id=user.id)
        for obj in target_objects:
            if not isinstance(obj.target, UserProfile):
                target_objects = list(target_objects).remove(obj)
                if target_objects is None:
                    break

        if target_objects is not None:
            stream.extend(target_objects)

        for item in stream:
            if item.actor is None:
                stream.remove(item)
                item.delete()

    stream = list(set(stream))
    stream = list(reversed(sorted(stream, key=lambda action: action.timestamp)))
    if to_add-1 == len(stream):
        output_dict = {'more': False}
    else:
        if len(stream) > 10:
            if to_add >= len(stream):
                output_dict = {'more': False}
            else:
                if (to_add+10) >= len(stream):
                    stream = stream[to_add:]
                else:
                    stream = stream[to_add:to_add + 10]

                output_dict = {'stream': stream}
                output_dict.update({'home': home})
                output_dict.update({'discover': discover})
                output_dict.update({'more': True})
        else:
            output_dict = {'more': False}
    return render_to_response("more.html", output_dict, RequestContext(request))


def load_latest(request, profile=False):
    """
    This method pushes the latest Actions done by a user to their stream
    in order to make the stream a 'LIVE' stream.
    """

    user = UserProfile.objects.filter(id=request.user.id)
    if len(user) > 0:
        user = user[0]
    else:
        output_dict = {'more': False}
        return render_to_response("more.html", output_dict, RequestContext(request))

    if 'user_name' in request.POST:
        user = UserProfile.objects.filter(username=request.POST['user_name'])
        if len(user) > 0:
            user = user[0]
        else:
            output_dict = {'more': False}
            return render_to_response("more.html", output_dict, RequestContext(request))

    home = True
    if 'profile' in request.POST:
        profile = True
        home = False
    if profile:
        stream = profile_stream(user)
    else:
        stream = get_stream(request, user)['stream']

    if not profile:
        follows = Follow.objects.filter(follower=user)
        for action in follows:
            if isinstance(action.followed_skill, Tag):
                items = TaggedItem.objects.filter(tag=action.followed_skill)
                for item in items:
                    if isinstance(item.object, Task):
                        stream.extend(Action.objects.filter(action_object_object_id=item.object.id))
        followers = Follow.objects.filter(follower__id=request.user.id)
        for item in followers:
            if item is not None:
                if isinstance(item.followed, UserProfile):
                    stream.extend(list(reversed(profile_stream(item.followed))))

    stream = list(set(stream))
    stream = list(reversed(sorted(stream, key=lambda action: action.timestamp)))
    item = []
    if len(stream) > 0:
        item = stream[0]
        if item.actor is None:
            list(stream).remove(item)
            item.delete()

    output_dict = {'item': item}
    output_dict.update({'user': user})
    output_dict.update({'home': home})
    return render_to_response("latest.html", output_dict, RequestContext(request))


def log_in(request):
    """
    This method checks for the input username(email) and password.
    If they are empty the user id redirected to the login page, else checks whether
    the user is authenticated. If the user is not found in the database, it renders the login
    page with an error_message that the email or password are invalid. Further, it checks if the user's
    account is activated, it not he is redirected back to login and notified.
    If the user is activated, it checks for the field remember_me, if it is not checked, then the
    expiry date of the session is set to when the browser is closed.
    Then the user is logged in using the login in django backends and it checks on the session
    value if it is his first time or not to open the getstrated instead of the normal profile.
    """
    base_login = True
    print "trying to login"
    if 'username' in request.POST and 'password' in request.POST:
        print "found user and pass in post"
        username = request.POST['username'].lower()
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is None:
            error_message = translation.gettext("The Email/Password is incorrect.")
            print error_message
            #return render(request, 'userprofiles/registration.html', {'error_message': error_message})
            return render(request, 'userprofiles/registration2.html', {'error_message': error_message})
        else:
            if user.is_active:
                if not request.POST.get('remember_me', False):
                    request.session.set_expiry(0)

                login(request, user)

                request.session['DEPLOYED_ADDRESS'] = settings.DEPLOYED_ADDRESS

                logged_user = UserProfile.objects.filter(username=request.user.username)
                if len(logged_user) > 0:
                    logged_user = logged_user[0]
                else:
                    print "no account found!!"
                    error_message = translation.gettext("You do not yet have an Account on Shoghlanah, please Request Invitation below.")
                    return render(request, 'userprofiles/registration2.html', {'error_message': error_message})
                    #return render(request, 'userprofiles/registration.html', {'error_message': error_message})
                if (request.POST['next']):  # Request contains next url
                    return redirect(request.POST['next'], RequestContext(request))

                return redirect('/', RequestContext(request))

            else:
                print "not yet activated"
                error_message = translation.gettext("This Email Hasn't Been Activated Yet. Please Check The Activation Mail Sent To You.")
                #error_message = translation.gettext("This Email Hasn't Been Activated Yet.")
                return render(request, 'userprofiles/registration2.html', {'error_message': error_message})
                #return render(request, 'userprofiles/registration.html', {'error_message': error_message})

    else:
        RegistrationForm = get_form_class(up_settings.REGISTRATION_FORM)

        if request.method == 'POST':
            form = RegistrationForm(data=request.POST, files=request.FILES)

            if form.is_valid():
                new_user = form.save()
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']

                request.session['login'] = "first"

                # Automatically log this user in
                if up_settings.AUTO_LOGIN:

                    if up_settings.EMAIL_ONLY:
                        username = form.cleaned_data['email']

                    user = authenticate(username=username, password=password)
                    if user is not None:
                        if user.is_active:
                            login(request, user)
                            # calculate_profile_completion(request)

                return redirect(up_settings.REGISTRATION_REDIRECT)

        else:
            form = RegistrationForm()
            try:
                next = request.GET['next']  # to save the next url if exists
            except:
         #       return render(request, 'userprofiles/registration.html', {'form': form, 'base_login': base_login})
                return render(request, 'userprofiles/registration2.html', {'form': form, 'base_login': base_login})

        return render(request, 'userprofiles/registration2.html', {'form': form, 'base_login': base_login, 'next': next})
        #return render(request, 'userprofiles/registration.html', {'form': form, 'base_login': base_login, 'next': next})


def logout_view(request):
    """
    This method takes the request and calls the django backends logout method and then
    redirects the user to the login view again.
    """
    if 'django_language' in request.session:
        x = request.session['django_language']
    else:
        x = "en"
    logout(request)
    request.session['django_language'] = x
    return redirect('/accounts/register/', RequestContext(request))


def switch_lang(request, lang):
    try:
        request.session['django_language'] = lang
    except:
        request.session['django_language'] = 'en'
    if 'next' in request.GET:
        return redirect(request.GET['next'], RequestContext(request))
    else:
        return redirect('/', RequestContext(request))


def search(request):
    """
    This view is used for search; it sends the keyword to quey on to the haystcks' search.
    If the user did not provide a keyword to search on, it searches an empty query.
    """
    try:
        q = request.POST['q']
    except:

        q = ''
    if q == '':
        results = SearchQuerySet().all()
    else:
        results = SearchQuerySet().filter(content=AutoQuery(q))
        results = results.filter_or(tags=AutoQuery(q))
        results = results.filter_or(title=AutoQuery(q))
        results = results.filter_or(location=AutoQuery(q))
    people = results.models(UserProfile)
    tasks = results.models(Task)
    return render_to_response('search/results.html', {'tresults': tasks, 'presults': people,'keyword': q, 'peopleCount': len(people), 'taskCount': len(tasks)}, RequestContext(request))


def filter_Search(request):
    """
    Filtering the Search according to the keys sent and the main search keyword
    Main : is the main keyword searched by the user from navbar
    Key: array of filter keywords sent from the view
    """
    main = ''
    if 'main' in request.POST:
        main = request.POST['main']
        if main != '':
            results = SearchQuerySet().filter(content=AutoQuery(main)).models(Task)
            results = results.filter_or(tags=main).models(Task)
            results = results.filter_or(title=AutoQuery(main)).models(Task)
            results = results.filter_or(location=AutoQuery(main)).models(Task)
        else:
            results = SearchQuerySet().all().models(Task)
    else:
        results = SearchQuerySet().all()
    if 'loca' in request.POST:
        loca = request.POST['loca']
        if loca != '':
            results = results.filter_and(city=loca)
    if 'word' in request.POST:
        word = request.POST['word']
        if word != '':
            results1 = results.filter_and(content=AutoQuery(word))
            results2 = results.filter_and(title=AutoQuery(word))
            results3 = results.filter_and(location=AutoQuery(word))
            results4 = results1.__or__(results2)
            results = results4.__or__(results3)
    if 'skills' in request.POST:
        skills = request.POST['skills']
        if skills != '':
            skills = skills.split(',')
            for s in skills:
                results = results.filter_and(tags=s)
    if 'from' in request.POST:
        from_price = request.POST['from']
        to_price = request.POST['to']
        if from_price != '' and to_price != '' and to_price != 'all':
            results = results.filter_and(price__range=[int(from_price), int(to_price)])

    return render_to_response('search/results_tasks.html', {'tresults': results, 'keyword': main, 'taskCount': len(results)}, RequestContext(request))


def notification_test(request):
    """
        this method is accessed when a user enter a message in the input field
        and the ajax function in message.html POST the data here after getting
        the data from the form, it saves the text in the database then trigger
        an event called 'message' to the pusher channel to allow any user
        subscribed to this channel to recieve this event with the data passed too
    """
    p['my_notifications'].trigger('notification', {
        'message': 'hiii',
        'the_title': 'loool',
    })
    return redirect('/notifications/')


def filter_stream(request):
    """
    This method serves to filter the stream of a user according to a given
    Action to make the stream easier to browse. Filtration results should be
    shrinked like in the normal stream to load more when a certain limit is reached.
    """
    verb = ""
    discover = False
    if 'verb' in request.POST:
        verb = request.POST['verb']

    if 'discover' in request.POST:
        discover = True

    if request.user.is_authenticated():
        if request.user.is_active:
            user = UserProfile.objects.get(id=request.user.id)
        latest = []
        stream = []
        if discover:
            task_stream = Action.objects.filter(verb="task_post")
            for item in task_stream:
                stream.append(item)
        else:
            init_res = get_stream(request, user, verb)
            stream = list(init_res['stream'])
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
            if item.actor is None:
                list(stream).remove(item)
            if item.verb == verb or item.verb == alt_verb:
                latest.append(item)
        output_dict = {'filtered_stream': latest}
        if discover:
            output_dict.update({'discover': "True"})
        output_dict.update({'filter': True, 'home': True})
        return render_to_response("filter.html", output_dict, RequestContext(request))


def view_skill(request, skill_id):
    """
    This method gathers the required information to build a profile
    for a certain skill. The items in the profile contain the users
    that have this skill as one of their own, the taks that require
    this skill, and finally the skills that have this skill as their
    parent skill.
    """
    skill = Tag.objects.get(id=skill_id)

    users = [UserProfile.objects.get(id=item.object_id) for item in TaggedItem.objects.filter(tag=skill.id) if item.content_type.name == u'user profile']
    user = UserProfile.objects.filter(username=request.user.username)
    if len(user) > 0:
        user = user[0]

    isFollowing = Follow.objects.filter(follower=user, followed_skill=skill)
    if len(isFollowing) > 0:
        isFollowing = True
    else:
        isFollowing = False

    tasks = [Task.objects.get(id=item.object_id) for item in TaggedItem.objects.filter(tag=skill.id) if item.content_type.name == 'task' and len(Task.objects.filter(id=item.object_id)) > 0]

    subskills = []
    subskills = Tag.objects.filter(parent=skill.id)

    output_dict = {'skill': skill}
    output_dict.update({'users': users})
    output_dict.update({'tasks': tasks})
    output_dict.update({'subskills': subskills})
    output_dict.update({'isFollowing': isFollowing})

    return render_to_response("skill_profile.html", output_dict, RequestContext(request))


def filter_people_search(request):
    main = request.POST['keyword']
    constraint = request.POST['constraint']
    skills = request.POST['skills']
    if skills != "":
        skills = skills.split(',')
    if main == '':
        results = SearchQuerySet().all().models(UserProfile)
    else:
        results = SearchQuerySet().filter(content=main).models(UserProfile)
    if skills != "":
        for s in skills:
            results = results.filter_and(tags=s)
    if constraint != "":
        results = results.filter_and(votesup__gte=constraint)

    return render_to_response('search/results_people.html', {'presults': results, 'keyword': main, 'peopleCount': len(results)}, RequestContext(request))


def refresh_notifications(request):
    new_notifications = Notice.objects.filter(recipient=request.user.id).filter(unseen=True)
    new_notifications_count = new_notifications.count()
    return render_to_response("Notifications/refreshed_notofocations.html", {'new_notifications': new_notifications, 'new_notifications_count': new_notifications_count}, RequestContext(request))


def follow(request, skill_id):
    if request.method == 'GET':
        skill = Tag.objects.get(id=skill_id)
        requestuser = UserProfile.objects.filter(username=request.user.username)
        if len(requestuser) > 0:
            requestuser = requestuser[0]
        else:
            return HttpResponse()
        Follow.objects.get_or_create(follower=requestuser, followed=None, followed_skill=skill)
        from shoghlanah.live_stream import add_action
        add_action(requestuser, "followed_skill", Tag.objects.get(id=skill_id), 'followed', Tag.objects.get(id=skill_id))
        return HttpResponse()


def unfollow(request, skill_id):
    if request.method == 'GET':
        skill = Tag.objects.get(id=skill_id)
        requestuser = UserProfile.objects.filter(username=request.user.username)
        if len(requestuser) > 0:
            requestuser = requestuser[0]
            Follow.objects.get(follower=requestuser, followed_skill=skill).delete()
            actions = Action.objects.filter(actor_object_id=requestuser.id, action_object_object_id=skill.id)
            for item in actions:
                p['stream'].trigger('mainStream', {'follow': (str(item.id))})
            for item in actions:
                item.delete()
        return HttpResponse()


def not_found(request):
    return render_to_response('404.html', {}, RequestContext(request))


def server_error(request):
    return render_to_response('500.html', {}, RequestContext(request))


def email_html(subject=None, from_email=None, to=None, msg=None, dic=None):
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import get_template
    from django.template import Context
    from html2text import html2text

    htmly = get_template('email/email_master.html')
    dic['DEPLOYED_ADDRESS'] = settings.DEPLOYED_ADDRESS or ''

    d = Context({'msg': msg, 'dict': dic, 'DEPLOYED_ADDRESS': settings.DEPLOYED_ADDRESS, 'STATIC_URL': settings.STATIC_URL})

    html_content = htmly.render(d)
    text_content = html2text(html_content)
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def survey(request):
    return render_to_response('survey.html', {}, RequestContext(request))


def passwords(request):
    return render_to_response('passwords.html', {}, RequestContext(request))


def import_simplejson():
    try:
        import simplejson as json
    except ImportError:
        try:
            import json  # Python 2.6+
        except ImportError:
            try:
                from django.utils import simplejson as json  # Google App Engine
            except ImportError:
                raise ImportError("Can't load a json library")
    return json
