# -*- coding: utf-8 -*-
from shoghlanah.models import *
from tagging.models import *
from actstream.models import Action
from notification.models import *
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib import messages
from django.utils import translation
from haystack.query import SearchQuerySet
from shoghlanah.live_stream import add_action
from shoghlanah.facebook import post_task_fb
from shoghlanah.twitter import tweet
from django.conf import settings
import datetime
import pusher
import json
import stripe
from shoghlanah.views import email_html
from currentTemplate.models import UserActivity
import re
from forms import *

stripe.api_key = settings.STRIPE_SECRET

DEPLOYED_ADDRESS = getattr(settings, 'DEPLOYED_ADDRESS', '')

pusher.app_id = settings.PUSHER_APP_ID
pusher.key = settings.PUSHER_KEY
pusher.secret = settings.PUSHER_SECRET

p = pusher.Pusher()


@login_required
def post_task(request):
    """
    This method is called when the user posts a task

    The information taken from the html form and creates a task
    with the data entered in the postTask modal

    The Task created is assigned to the user currently login

    After the task is saved in the database, the user is redirected
    to the page the posttask action wast triggered from

    Variable:
    next : is the variable which contains the name of the page
    the posttask was triggered from.
    """

    if request.method == 'POST':
        try:
            # price = request.POST['price']
            # if price == 'Reward':
            #     reward_id = request.POST['reward']
            #     reward = Reward.objects.get(pk = reward_id)
            #     price = None
            # else:
            price = int(request.POST['sliderInput'])
            reward = None
            if isinstance(price, int):
                price = price
            else:
                raise ValueError('Invalid price')
            # if price == None and reward == None:
            if price is None:
                raise ValidationError(u'You have to enter price or reward of the task')
            longitude = request.POST['long']
            latitude = request.POST['lat']
            latitude = latitude.replace(',', '.')
            longitude = longitude.replace(',', '.')
            if longitude == '' or latitude == '':
                longitude = 200.0
                latitude = 200.0
            user = UserProfile.objects.get(id=request.user.id)
            location = request.POST['where']
            if location is not None and len(location) > 0:
                temp_loc = location.split(',')
                if len(temp_loc) > 1:
                    city = temp_loc[len(temp_loc)-2].strip()
                else:
                    city = temp_loc[0].strip()
                if city.endswith('Governorate'):
                    city = city[:-len('Governorate')].strip()
            else:
                raise ValueError('Empty location')

            title = request.POST['task_name']
            if title is not None and len(title) > 0 and not title.isspace():
                if (len(title) <= 128):
                    title = title.strip()
                else:
                    raise ValueError('Title Too long')
            else:
                raise ValueError('Empty Title')
            task = Task.objects.create(
                title=title,
                address=location,
                city=city,
                price=price,
                reward=reward,
                description=request.POST['task_desc'],
                user=user,
                longitude=float(longitude),
                latitude=float(latitude),
                status='New',
                start_date=datetime.datetime.now(),
            )

            task.tags = ',' + request.POST['skills']
            if 'got_started' in request.POST:

                user.got_started = True
                user.save()
            task.save()
            add_action(user, "task_post", task, "", user)
            # sender = []
            # for tag in task.tags:
            #     sender.append(User.objects.filter(tag__contains=tag))
            sender_profile = UserProfile.objects.get(pk=request.user.id)
            sender = User.objects.get(pk=request.user.id)
            the_message = sender.first_name + ' needs "' + task.title + '"'
            if sender_profile.gender == 'F':
                the_message_arabic = sender.first_name + ' تريد "'.decode("utf-8") + task.title + '"'
            else:
                the_message_arabic = sender.first_name + ' يريد "'.decode("utf-8") + task.title + '"'
            receivers = [UserProfile.objects.get(id=item.object_id) for skill in task.tags for item in TaggedItem.objects.filter(tag=skill.id) if item.content_type.name == u'user profile' and item.object_id != request.user.id]
            the_link = '/task/' + str(task.id)
            send_now(receivers, sender, 'post_task', the_message, the_message_arabic, the_link)

            for receiver in receivers:
                if not receiver.id == request.user.id:
                    notices = Notice.objects.filter(recipient=receiver, sender=sender, message=the_message, message_arabic=the_message_arabic, link=the_link)
                    p['channel_' + str(receiver.username)].trigger('notification', {
                        'message': sender.first_name + ' ' + sender.last_name + ' needs  ' + '<a href="/task/' + str(task.id) + '/">' + task.title + '</a>',
                        'name': sender.first_name + ' ' + sender.last_name,
                        'translated': 'needs',
                        'link': '<a href="/notifications/' + str(notices[0].id) + '/">' + task.title + '</a>',
                        'the_title_translated': 'A New shoghlanah is Posted',
                        'the_title': ' ',
                    })

            from shoghlanah.views import email_html
            subject = "A new shoghlanah is posted"
            to = []
            for receiver in receivers:
                # thereceiver = UserProfile.objects.get(id=receiver.id)
                # if thereceiver.email_new_shoghlanah:
                to.append(receiver.email)
            from_email = settings.EMAIL_HOST_USER
            msg = ' shoghlanah is posted.'
            dic = {}
            dic['task'] = task
            email_html(subject=subject, from_email=from_email, to=to, msg=msg, dic=dic)

            # if user.complete_profile <= 100:
            #     return redirect() #to complete hos profile

            if 'facebook' in request.POST:
                post_task_fb(task=task, request=request)
            if 'twitter' in request.POST:
                tweet(request, status="i posted a task on #Shoghlanah " + DEPLOYED_ADDRESS + "task/" + str(task.id) + '/')
            # if 'google' in request.POST:

            messages.info(request, translation.gettext("Created a task successfully"))
            return redirect('/task/' + str(task.id), context_instance=RequestContext(request))
        except:
            messages.warning(request, translation.gettext("Failed to post a task, try again"))
            return redirect(request.GET['next'], context_instance=RequestContext(request))


def viewTask(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        if request.user.is_authenticated():
            bids = Bid.objects.filter(task=task.id)
            if len(bids) > 0:
                if task.user.id == request.user.id:
                    bids = sorted(bids, key=lambda bid: not bid.isAccepted)
                else:
                    bids = bids.filter(user=request.user.id)
                    if len(bids) > 0:
                        bids = bids[0]
                    else:
                        bids = None
        else:
            bids = None
        if task.reward is not None:
            rewardPic = Reward.objects.get(pk=task.reward_id)
        else:
            rewardPic = None
        return render_to_response("viewTask.html", {'task': task, 'rewardPic': rewardPic, 'bids': bids}, RequestContext(request))
    except Task.DoesNotExist:
        raise Http404


@login_required
def chat_list(request, task_id):
    task = Task.objects.get(id=task_id)
    bids = Bid.objects.filter(task=task.id)
    if len(bids) > 0:
        if task.user.id == request.user.id:
            bids = sorted(bids, key=lambda bid: not bid.isAccepted)
        else:
            bids = bids.filter(user=request.user.id)
            bids = bids[0]
    return render_to_response("chats/chat.html", {'task': task, 'bids': bids}, RequestContext(request))


def discussion(request, user_id, task_id, bid_id=None):
    task = Task.objects.get(id=task_id)
    bids = Bid.objects.filter(task=task.id)
    acceptbid = bids.filter(isAccepted=True)
    if acceptbid:
        acceptbid = acceptbid[0]
    if bid_id is None:
        bid = None
        messages = None
    else:
        bid = Bid.objects.get(id=bid_id)
        messages = Discussion.objects.filter(bid=bid_id)
        messages = sorted(messages, key=lambda x: x.time, reverse=False)

    user = UserProfile.objects.get(id=user_id)
    return render_to_response('chats/discussion.html', {'PUSHER_KEY': settings.PUSHER_KEY, 'acceptbid': acceptbid, 'task': task, 'user': user, 'bid': bid, 'messages': messages}, RequestContext(request))


@login_required
def edit_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        if request.user.id != task.user.id and task.status != "New":
            raise ValueError('User has no permission to edit this task')
        title = request.POST['edit_title']
        desc = request.POST['edit_desc']
        if title is not None and len(title) > 0 and len(title.strip()) > 0:
            task.title = title.strip()
        else:
            raise ValueError('Title is a required field')
        # if request.POST.has_key('edit_price'):
        task.description = desc
        price = request.POST['edit_price']
        if price == '':
            raise ValueError('Price is a required field')
        else:
            price = int(price)
        if isinstance(price, int):
            task.price = price
        else:
            raise ValueError('Price entered is invalid')
        # else:
        #     reward_id = int(request.POST['edit_reward'])
        #     r = Reward.objects.get(pk=reward_id)
        #     if not r:
        #         raise ValueError('Reward chosen is invalid')
        #     else:
        #         if desc == '':
        #             raise ValueError('Description is a required field with rewards')
        #         else:
        #             task.description = desc
        #         task.reward = r
        location = request.POST['edit_location']
        # location = "".join([x if ord(x) < 128 else ' ' for x in loca])
        latitude = request.POST['edit_lat']
        longitude = request.POST['edit_lng']
        if location is not None and len(location) > 0:
            if location != task.address:
                if latitude is not None and longitude is not None:
                    latitude = latitude.replace(',', '.')
                    longitude = longitude.replace(',', '.')
                    task.latitude = float(latitude)
                    task.longitude = float(longitude)
                else:
                    task.longitude = 200.0
                    task.latitude = 200.0
                task.address = location
                temp_loc = location.split(',')
                if len(temp_loc) > 1:
                    city = temp_loc[len(temp_loc)-2].strip()
                else:
                    city = temp_loc[0].strip()

                if city.endswith('Governorate'):
                    city = city[:-len('Governorate')].strip()
                task.city = city
        else:
            raise ValueError('Location is a required field')
        tags = ',' + request.POST['edit_tags']
        if tags == '':
            task.tags = ''
        else:
            task.tags = tags
        task.save()
        response = 'The Task data is edited'
        return HttpResponse(response)
    except ValueError as e:
        temp = translation.gettext(str(e))
        msg = 'Error: ' + temp
        return HttpResponse(msg)


def message(request, receiver_id, task_id, bid_id=None):
    """
        this method is accessed when a user enter a message in the input field
        and the ajax function in message.html POST the data here after getting
        the data from the form, it saves the text in the database then trigger
        an event called 'message' to the pusher channel to allow any user
        subscribed to this channel to recieve this event with the data passed too
    """
    stamp = datetime.datetime.now()
    timestamp = stamp.strftime("%b %d, %Y | %I:%M %p")
    sender = UserProfile.objects.get(id=request.user.id)
    receiver = UserProfile.objects.get(id=receiver_id)
    task = Task.objects.get(id=task_id)
    msg = request.POST.get('message')
    if msg == ' ':
        return HttpResponse('')
    if bid_id is None:
        bids = Bid.objects.filter(task=task_id).filter(user=request.user.id)
        if bids:
            bid = bids[0]
            bid.last_msg = datetime.datetime.now()
        else:
            bid = None
            if task.price is None:
                bid = Bid.objects.create(task=task, user=sender, message=task.reward, last_msg=datetime.datetime.now())
            else:
                bid = Bid.objects.create(task=task, user=sender, message=task.price, last_msg=datetime.datetime.now())

            # if receiver.email_bid_placed:
            from shoghlanah.views import email_html
            subject = "A bid on your shoghlanah"
            to = [receiver.email]
            from_email = settings.EMAIL_HOST_USER
            msg = 'bidded on your shoghlanah '
            dic = {}
            dic['bid'] = bid
            email_html(subject=subject, from_email=from_email, to=to, msg=msg, dic=dic)
        bid.save()
    else:
        bid = Bid.objects.get(id=bid_id)
        bid.last_msg = datetime.datetime.now()
        bid.save()
    if request.POST.get('message'):
        p['channel_chat' + str(receiver_id) + str(sender.id)+str(task_id)].trigger('message', {
            'message': request.POST.get('message'),
            'user': sender.username,
            'id': str(sender.id),
            'name': sender.first_name + " " + sender.last_name,
            'timestamp': timestamp,
        })
        p['channel_chat' + str(sender.id) + str(receiver_id) + str(task_id)].trigger('message', {
            'message': request.POST.get('message'),
            'user': sender.username,
            'id': str(sender.id),
            'name': sender.first_name + " " + sender.last_name,
            'timestamp': timestamp,
        })
        Discussion.objects.create(message=request.POST.get('message'), sender=sender, receiver=receiver, time=datetime.datetime.now(), bid=bid)
        if sender.gender == "F":
            if bid_id is None:
            # Put notify user (Target user = receiver)
                sender = UserProfile.objects.get(id=request.user.id)
                the_message = sender.first_name + ' bidded on your task "' + task.title + '"'
                the_message_arabic = sender.first_name + ' وضعت مزايدة على "'.decode("utf-8") + task.title + '"'
                receivers = [UserProfile.objects.get(id=receiver_id)]
                the_link = '/task/' + str(task.id)
                try:
                    send_now(receivers, sender, 'post_task', the_message, the_message_arabic, the_link)
                    notices = Notice.objects.filter(recipient=receiver, sender=sender, message=the_message, message_arabic=the_message_arabic, link=the_link)
                except:
                    pass
                p['channel_' + str(receiver.username)].trigger('notification', {
                    'message': sender.first_name + ' ' + sender.last_name + ' bidded on your task  <a href="/task/' + str(task.id) + '/">' + task.title + '</a>',
                    'name': sender.first_name + ' ' + sender.last_name,
                    'translated': ' bidded on your task ',
                    'link': '<a href="/notifications/' + str(notices[0].id) + '/">' + task.title + '</a>',
                    'the_title': sender.first_name,
                    'the_title_translated': 'bidded on your task',
                })
            else:
                sender = UserProfile.objects.get(id=request.user.id)
                the_message = sender.first_name + ' discussed "' + task.title + '"'
                the_message_arabic = sender.first_name + ' ناقشت "'.decode("utf-8") + task.title + '"'
                receivers = [UserProfile.objects.get(id=receiver_id)]
                the_link = '/task/' + str(task.id)
                # Notice.objects.filter(recipient=receiver, sender=sender, link=the_link).delete()
                try:
                    send_now(receivers, sender, 'post_task', the_message, the_message_arabic, the_link)
                    notices = Notice.objects.filter(recipient=receiver, sender=sender, message=the_message, message_arabic=the_message_arabic, link=the_link)
                except:
                    pass
                p['channel_' + str(receiver.username)].trigger('notification', {
                    'message': sender.first_name + ' ' + sender.last_name + ' sent a message on your task  <a href="/task/' + str(task.id) + '/">' + task.title + '</a>',
                    'name': sender.first_name + ' ' + sender.last_name,
                    'translated': ' sent a message on your task ',
                    'link': '<a href="/notifications/' + str(notices[0].id) + '/">' + task.title + '</a>',
                    'the_title': sender.first_name,
                    'the_title_translated': 'is chatting with you',
                })
                # thereceiver = UserProfile.objects.get(id=receiver.id)
                # if thereceiver.email_discuss_shoghlanah:
                from shoghlanah.views import email_html
                ########################### BEGIN CURRENT TEMPLATE CHECK #####################
                from currentTemplate.models import UserActivity
                import re
                thirty_minutes = datetime.datetime.now() - datetime.timedelta(minutes=30)
                sql_datetime = datetime.datetime.strftime(thirty_minutes, '%Y-%m-%d %H:%M:%S')
                users = UserActivity.objects.filter(latest_activity__gte=sql_datetime, user__is_active__exact=1, )
                send = True
                for user in users:
                    template = user.current_template
                    task_id = re.findall(r'/task/(.*?)/', template)
                    if task_id and user.user.username == receiver.username:
                        send = False
                ######################### END CURRENT TEMPLATE CHECK ############################
                if send:
                    subject = "Discussion on your shoghlanah"
                    to = [receiver.email]
                    from_email = settings.EMAIL_HOST_USER
                    msg = ' sent you a message on your shoghlanah '
                    dic = {}
                    dic['bid'] = bid
                    email_html(subject=subject, from_email=from_email, to=to, msg=msg, dic=dic)
        else:
            if bid_id is None:
            # Put notify user (Target user = receiver)
                sender = UserProfile.objects.get(id=request.user.id)
                the_message = sender.first_name + ' bidded on your task "' + task.title + '"'
                the_message_arabic = sender.first_name + ' وضع مزايدة على "'.decode("utf-8") + task.title + '"'
                receivers = [UserProfile.objects.get(id=receiver_id)]
                the_link = '/task/' + str(task.id)
                try:
                    send_now(receivers, sender, 'post_task', the_message, the_message_arabic, the_link)
                    notices = Notice.objects.filter(recipient=receiver, sender=sender, message=the_message, message_arabic=the_message_arabic, link=the_link)
                except:
                    pass
                p['channel_' + str(receiver.username)].trigger('notification', {
                    'message': sender.first_name + ' ' + sender.last_name + ' bidded on your task  <a href="/task/' + str(task.id) + '/">' + task.title + '</a>',
                    'name': sender.first_name + ' ' + sender.last_name,
                    'translated': 'bidded on your task',
                    'link': '<a href="/notifications/' + str(notices[0].id) + '/">' + task.title + '</a>',
                    'the_title': sender.first_name,
                    'the_title_translated': 'bidded on your task',
                })
            else:
                sender = UserProfile.objects.get(id=request.user.id)
                the_message = sender.first_name + ' discussed "' + task.title + '"'
                the_message_arabic = sender.first_name + ' ناقش "'.decode("utf-8") + task.title + '"'
                receivers = [UserProfile.objects.get(id=receiver_id)]
                the_link = '/task/' + str(task.id)
                # Notice.objects.filter(recipient=receiver, sender=sender, link=the_link).delete()
                try:
                    send_now(receivers, sender, 'post_task', the_message, the_message_arabic, the_link)
                    notices = Notice.objects.filter(recipient=receiver, sender=sender, message=the_message, message_arabic=the_message_arabic, link=the_link)
                except:
                    pass
                p['channel_' + str(receiver.username)].trigger('notification', {
                    'message': sender.first_name + ' ' + sender.last_name + ' sent a message on your task  <a href="/task/' + str(task.id) + '/">' + task.title + '</a>',
                    'name': sender.first_name + ' ' + sender.last_name,
                    'translated': 'sent a message on your task',
                    'link': '<a href="/notifications/' + str(notices[0].id) + '/">' + task.title + '</a>',
                    'the_title': sender.first_name,
                    'the_title_translated': 'is chatting with you',
                })
                # thereceiver = UserProfile.objects.get(id=receiver.id)
                # if thereceiver.email_discuss_shoghlanah:
                from shoghlanah.views import email_html
                ########################### BEGIN CURRENT TEMPLATE CHECK #####################
                from currentTemplate.models import UserActivity
                import re
                thirty_minutes = datetime.datetime.now() - datetime.timedelta(minutes=30)
                sql_datetime = datetime.datetime.strftime(thirty_minutes, '%Y-%m-%d %H:%M:%S')
                users = UserActivity.objects.filter(latest_activity__gte=sql_datetime, user__is_active__exact=1, )
                send = True
                for user in users:
                    template = user.current_template
                    task_id = re.findall(r'/task/(.*?)/', template)
                    if task_id and user.user.username == receiver.username:
                        send = False
                ######################### END CURRENT TEMPLATE CHECK ############################
                if send:
                    subject = "Discussion on your shoghlanah"
                    to = [receiver.email]
                    from_email = settings.EMAIL_HOST_USER
                    msg = ' sent you a message on your shoghlanah '
                    dic = {}
                    dic['bid'] = bid
                    email_html(subject=subject, from_email=from_email, to=to, msg=msg, dic=dic)

    return HttpResponse('')


@csrf_exempt
def authUser(request, sender_user_name, receiver_id):
    """
        this method is the authentication endpoint of pusher which is adjusted
        also in the javascript tag in message.html it just allows you to authenticate
        the user before allowing/granting the permission (to the user) to subscribe to
        your channel its an option for private channels provided by pusher
    """
    response = p[request.POST.get('channel_name')].authenticate(request.POST.get('socket_id'))
    return HttpResponse(json.dumps(response), mimetype="application/json")


@login_required
def delete_task(request, task_id):
    """
    tasks to do :  1-if the task has bids.
                   2-if task doesn't exist.(Done)
                   3-the redirect page if the owner is not valid.
                   4-localization
    """
    get_object_or_404(Task, id=task_id)
    if request.user.username == Task.objects.get(id=task_id).user.username and Task.objects.get(id=task_id).status == "New":
        for item in TaggedItem.objects.filter(object_id=task_id):
            item.delete()
        Task.objects.get(id=task_id).delete()

        for item in Action.objects.filter(action_object_object_id=task_id):
            p['stream'].trigger('mainStream', {'action': (str(item.id)), })
            item.delete()

        messages.info(request, translation.gettext("Task was deleted successfully"))
        return redirect('/', context_instance=RequestContext(request))
    else:
        messages.warning(request, translation.gettext("You cannot delete this task"))
        return redirect('/', context_instance=RequestContext(request))


def soon():
    soon = datetime.date.today() + datetime.timedelta(days=30)
    return {'month': soon.month, 'year': soon.year}


@login_required
def pay(request, bid_id):
    if bid_id is None:
        return HttpResponse("No bid")
    else:
        bid = Bid.objects.get(id=bid_id)
        task = Task.objects.get(id=bid.task.id)
    if request.user.id != task.user.id:
        return HttpResponse(" Unauthorized user ")
    if request.method == 'POST':
        form = CardForm(request.POST)
        token = form.cleaned_data['stripe_token']
        if form.is_valid():
            stripe.Charge.create(
                amount=int(bid.message),
                currency="usd",  # need to be changed
                card=token
            )
            task = Task.objects.get(id=bid.task.id)
            bid.isPaied = True
            bid.save()
            # Put notify user (Target user = bid.user)
            sender_profile = UserProfile.objects.get(pk=request.user.id)
            if sender_profile.gender == "F":
                sender = User.objects.get(pk=request.user.id)
                the_message = sender.first_name + ' paid the money for "' + task.title + '"'
                the_message_arabic = sender.first_name + ' دفعت المال لل "'.decode("utf-8") + task.title + '"'
                receivers = [User.objects.get(id=bid.user.id)]
                the_link = '/task/' + str(task.id)
                send_now(receivers, sender, 'post_task', the_message, the_message_arabic, the_link)
                notices = Notice.objects.filter(recipient=bid.user, sender=sender, message=the_message, message_arabic=the_message_arabic, link=the_link)
                p['channel_' + str(bid.user.username)].trigger('notification', {
                    'message': sender.first_name + ' ' + sender.last_name + ' paid the money for  <a href="/task/' + str(task.id) + '/">' + task.title + '</a>',
                    'name': sender.first_name + ' ' + sender.last_name,
                    'translated': ' paid the money for ',
                    'link': '<a href="/notifications/' + str(notices[0].id) + '/">' + task.title + '</a>',
                    'the_title': sender.first_name,
                    'the_title_translated': 'paid the required amount of money',
                })
            else:
                sender = User.objects.get(pk=request.user.id)
                the_message = sender.first_name + ' paid the money for "' + task.title + '"'
                the_message_arabic = sender.first_name + ' دفع المال لل "'.decode("utf-8") + task.title + '"'
                receivers = [User.objects.get(id=bid.user.id)]
                the_link = '/task/' + str(task.id)
                send_now(receivers, sender, 'post_task', the_message, the_message_arabic, the_link)
                notices = Notice.objects.filter(recipient=bid.user, sender=sender, message=the_message, message_arabic=the_message_arabic, link=the_link)
                p['channel_' + str(bid.user.username)].trigger('notification', {
                    'message': sender.first_name + ' ' + sender.last_name + ' paid the money for  <a href="/task/' + str(task.id) + '/">' + task.title + '</a>',
                    'name': sender.first_name + ' ' + sender.last_name,
                    'translated': 'paid the money for',
                    'link': '<a href="/notifications/' + str(notices[0].id) + '/">' + task.title + '</a>',
                    'the_title': sender.first_name,
                    'the_title_translated': 'paid the required amount of money',
                })
            return HttpResponseRedirect("/task/"+str(task.id)+"/")
            # return HttpResponseRedirect("/reviewing/"+user_id+"/"+task_id+"/")
    else:
        form = CardForm()
    return render_to_response('stripe_pay.html', {'task': task, 'bid': bid, 'form': form, 'publishable': settings.STRIPE_PUBLISHABLE, 'soon': soon(), 'months': range(1, 13), 'years': range(2012, 2030)}, RequestContext(request))


@login_required
def getreviews(request, receiver_id, bid_id):
    receiver = UserProfile.objects.get(id=receiver_id)
    sender = UserProfile.objects.get(id=request.user.id)
    bid = Bid.objects.get(id=bid_id)
    review = Review.objects.filter(task=bid.task, reviewer=sender, reviewed=receiver)
    if review:
        return HttpResponse('')
    # try:
    #     review = Review.objects.get(task = task ,reviewer = sender , reviewed = receiver)
    #     reviewRecommend = review.isRecommended
    #     reviewUnrecommend = review.isUnrecommended
    # except:
    #     reviewRecommend = False
    #     reviewUnrecommend = False
    return render_to_response('reviewform.html', {'bid': bid, 'user': receiver}, RequestContext(request))


@login_required
def review(request, receiver_id, bid_id):  # user reviews only once
    try:
        text = request.POST.get('text')
        recommend = request.POST.get('recommend')
        bid = Bid.objects.get(id=bid_id)
        receiver = UserProfile.objects.get(id=receiver_id)
        sender = UserProfile.objects.get(id=request.user.id)
        task = Task.objects.get(id=bid.task.id)
        if sender.id == receiver.id or (sender.id != bid.task.user.id and sender.id != bid.user.id) or (receiver.id != bid.task.user.id and receiver.id != bid.user.id):
            return HttpResponse('')
        else:
            review = Review.objects.filter(task=bid.task, reviewer=sender, reviewed=receiver)
        if review or recommend is None:
            return HttpResponse('')
        else:
            review = Review.objects.create(reviewer=sender, reviewed=receiver, task=task, text=text)
            if recommend == '1' or recommend == '0':
                if recommend == '1':
                    review.isRecommended = True
                    receiver.votes_up += 1
                elif recommend == '0':
                    review.isUnrecommended = True
                    receiver.votes_down += 1
                receiver.save()
                if request.user.id == bid.task.user.id:  # if reviewed the bidderd set the isReviewed to true
                    bid.isReviewed = True
                    bid.save()
                else:
                    task.status = 'review'  # set the task status to review if the owner is reviewed by the bidder
                    task.save()
                review.save()
            else:
                return HttpResponse('')
        # Put notify user (Target user = receiver)

        sender = User.objects.get(pk=request.user.id)
        the_message = sender.first_name + ' reviewed you for "' + task.title + '"'
        the_message_arabic = sender.first_name + ' قام بتقييمك على "'.decode("utf-8") + task.title + '"'
        receivers = [User.objects.get(id=receiver.id)]
        the_link = '/task/' + str(task.id)
        send_now(receivers, sender, 'post_task', the_message, the_message_arabic, the_link)
        notices = Notice.objects.filter(recipient=receiver, sender=sender, message=the_message, message_arabic=the_message_arabic, link=the_link)
        p['channel_' + str(receiver.username)].trigger('notification', {
            'message': sender.first_name + ' ' + sender.last_name + ' reviewed you for  <a href="/task/' + str(task.id) + '/">' + task.title + '</a>',
            'name': sender.first_name + ' ' + sender.last_name,
            'translated': 'reviewed you for',
            'link': '<a href="/notifications/' + str(notices[0].id) + '/">' + task.title + '</a>',
            'the_title': sender.first_name,
            'the_title_translated': 'reviewed you',
        })
        return HttpResponse('Success')
    except:
        return HttpResponse('No bid for the user')


def similarTask(request, task_id):
    task = Task.objects.get(id=task_id)
    skills = task.tags
    results = SearchQuerySet().all()
    q = ""
    for s in skills:
        results = results.filter_and(tags=s)
        q += " "+s.name
    people = results.models(UserProfile)
    tasks = results.models(Task)
    return render_to_response('search/results.html', {'tresults': tasks, 'presults': people, 'keyword': q, 'peopleCount': len(people), 'taskCount': len(tasks)}, RequestContext(request))


@login_required
def report_task(request):
    from views import import_simplejson
    json = import_simplejson()
    task_id = request.POST.get('task_id', 1)
    reason = request.POST.get('reason', "no reason entered")
    task = Task.objects.get(id=task_id)
    try:
        report = ReportTask.objects.get(task=task)
        report_reason = json.loads(report.reason)
        duplicate = False
        for i in range(1, report.count+1):
            if report_reason[str(i)]['username'] == request.user.username:
                duplicate = True
                break
        if not duplicate:
            report_reason = {}
            report_reason = json.loads(report.reason)
            report.count += 1
            report_reason[report.count] = {"username": request.user.username, "reason": reason}
            print report_reason
            report.reason = json.dumps(report_reason)
            report.save()
    except ReportTask.DoesNotExist:
        report = ReportTask.objects.create(task=task)
        report_reason = {}
        report.count += 1
        report_reason[report.count] = {"username": request.user.username, "reason": reason}
        report.reason = json.dumps(report_reason)
        report.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))


@login_required
def invite_contractor(request, task_id, contractor_id):
    user = request.user
    contractor = UserProfile.objects.get(pk=contractor_id)
    task = Task.objects.get(pk=task_id)

    # try:
    if contractor.email:
        from views import email_html
        subject = 'invitation to a shoghlanah'
        to = [contractor.email]
        msg = 'please have a look at this shoghlanah, I thought you might be interested in'
        dic = {'task': task}
        email_html(subject=subject, to=to, msg=msg, dic=dic)

    from ShoghlanahProject import settings
    DEPLOYED_ADDRESS = getattr(settings, 'DEPLOYED_ADDRESS', '')

    receivers = [contractor]
    sender = user
    label = 'invite_to_task'
    the_message = 'Invitation to a Shoghlanah'
    message_arabic = 'دعوة عمل علي شغلانة'
    the_link = DEPLOYED_ADDRESS + 'task/' + task_id
    send_now(users=receivers, sender=sender, label=label, the_message=the_message, message_arabic=message_arabic, the_link=the_link)

    return HttpResponse("invitation sent to " + contractor.first_name + ' ' + contractor.last_name)
    # except:
    #     return HttpResponse("invitation not sent")
