# -*- coding: utf-8 -*-
from shoghlanah.models import *
from ShoghlanahProject import settings
from notification.models import Notice
from notification.models import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import pusher

pusher.app_id = settings.PUSHER_APP_ID
pusher.key = settings.PUSHER_KEY
pusher.secret = settings.PUSHER_SECRET

p = pusher.Pusher()


def bid(request, bid_id, bid_msg):
    try:
        bid = Bid.objects.get(id=bid_id)
        if request.user.id == bid.user.id and not bid.isAccepted:
            bid.message = bid_msg
            task = Task.objects.get(id=bid.task.id)
            bid.save()
            p['channel_bid' + str(task.id)].trigger('bid', {
            'bid_msg': bid_msg,
            });
            sender_profile = UserProfile.objects.get(pk=request.user.id)
            sender = User.objects.get(pk=request.user.id)
            receivers = [task.user]
            the_link = '/task/' + str(task.id)
            if sender_profile.gender == 'F':
                the_message = sender.first_name + ' changed her bid on "' + task.title + '"'
                the_message_arabic = sender.first_name + ' قامت بتغيير المزايدة على "'.decode("utf-8") + task.title + '"'

                send_now(receivers, sender, 'bid_changed', the_message, the_message_arabic, the_link)
                for receiver in receivers:
                    notices = Notice.objects.filter(recipient=receiver, sender=sender, message=the_message, message_arabic=the_message_arabic, link=the_link)
                    p['channel_' + str(receiver.username)].trigger('notification', {
                        'message': sender.first_name + ' ' + sender.last_name + ' changed her bid on  <a href="/task/' + str(task.id) + '/">' + task.title + '</a>',
                        'name': sender.first_name + ' ' + sender.last_name,
                        'translated': 'changed her bid on',
                        'link': '<a href="/notifications/' + str(notices[0].id) + '/">' + task.title + '</a>',
                        'the_title_translated': 'A bid is changed',
                        'the_title': ' ',
                    })
            else:
                the_message = sender.first_name + ' changed his bid on "' + task.title + '"'
                the_message_arabic = sender.first_name + ' قام بتغيير المزايدة على "'.decode("utf-8") + task.title + '"'
                send_now(receivers, sender, 'bid_changed', the_message, the_message_arabic, the_link)
                for receiver in receivers:
                    notices = Notice.objects.filter(recipient=receiver, sender=sender, message=the_message, message_arabic=the_message_arabic, link=the_link)
                    p['channel_' + str(receiver.username)].trigger('notification', {
                        'message': sender.first_name + ' ' + sender.last_name + ' changed his bid on  <a href="/task/' + str(task.id) + '/">' + task.title + '</a>',
                        'name': sender.first_name + ' ' + sender.last_name,
                        'translated': 'changed his bid on',
                        'link': '<a href="/notifications/' + str(notices[0].id) + '/">' + task.title + '</a>',
                        'the_title_translated': 'A bid is changed',
                        'the_title': ' ',
                    })
            return HttpResponse('')
        else:
            raise ValueError('User has no permission to change bid')
    except:
        return HttpResponse('no permission')


def accept_bid(request, bid_id):
    bid = Bid.objects.get(id=bid_id)
    task = Task.objects.get(id=bid.task.id)
    if task.user.id == request.user.id and task.status == "New":
        task.status = "close"
        task.save()
        bid.isAccepted = True
        bid.save()
        # Put notify user (Target user = bid.user)
        sender_profile = UserProfile.objects.get(pk=request.user.id)
        if sender_profile.gender == "F":
            sender = User.objects.get(pk=request.user.id)
            the_message = sender.first_name + ' accepted your bid on "' + task.title + '"'
            the_message_arabic = sender.first_name + ' قبلت المزايدة على "'.decode("utf-8") + task.title + '"'
            receivers = [User.objects.get(id=bid.user.id)]
            the_link = '/task/' + str(task.id)
            send_now(receivers, sender, 'post_task', the_message, the_message_arabic, the_link)
            notices = Notice.objects.filter(recipient=bid.user, sender=sender, message=the_message, message_arabic=the_message_arabic, link=the_link)
            p['channel_' + str(bid.user.username)].trigger('notification', {
                'message': sender.first_name + ' ' + sender.last_name + ' accepted your bid on  <a href="/task/' + str(task.id) + '/">' + task.title + '</a>',
                'name': sender.first_name + ' ' + sender.last_name,
                'translated': ' accepted your bid on ',
                'link': '<a href="/notifications/' + str(notices[0].id) + '/">' + task.title + '</a>',
                'the_title': sender.first_name,
                'the_title_translated': 'accepted your bid',
            })
        else:
            sender = User.objects.get(pk=request.user.id)
            the_message = sender.first_name + ' accepted your bid on "' + task.title + '"'
            the_message_arabic = sender.first_name + ' قبل المزايدة على "'.decode("utf-8") + task.title + '"'
            receivers = [User.objects.get(id=bid.user.id)]
            the_link = '/task/' + str(task.id)
            send_now(receivers, sender, 'post_task', the_message, the_message_arabic, the_link)
            notices = Notice.objects.filter(recipient=bid.user, sender=sender, message=the_message, message_arabic=the_message_arabic, link=the_link)
            p['channel_' + str(bid.user.username)].trigger('notification', {
                'message': sender.first_name + ' ' + sender.last_name + ' accepted your bid on  <a href="/task/' + str(task.id) + '/">' + task.title + '</a>',
                'name': sender.first_name + ' ' + sender.last_name,
                'translated': 'accepted your bid on',
                'link': '<a href="/notifications/' + str(notices[0].id) + '/">' + task.title + '</a>',
                'the_title': sender.first_name,
                'the_title_translated': 'accepted your bid',
            })
        p['channel_bid' + str(task.id)].trigger('accept_bid', {'bid': bid.isAccepted});
        # thereceiver = UserProfile.objects.get(id=bid.user.id)
        # if thereceiver.email_bid_accepted:
        from shoghlanah.views import email_html
        subject = "Bid Accepted"
        to = [bid.user.email]
        from_email = settings.EMAIL_HOST_USER
        msg = ' accepted your bid on the shoghlanah '
        dic = {}
        dic['bid'] = bid
        email_html(subject=subject, from_email=from_email, to=to, msg=msg, dic=dic)
    return HttpResponse('')


@login_required
def viewbids(request):
    mybids = [Task.objects.get(id=item.task.id) for item in Bid.objects.filter(user=request.user.id)]
    print mybids
    mytasks = Task.objects.filter(user=request.user.id)
    print mytasks
    bactive = False
    tactive = False
    if len(mybids) > len(mytasks):
        bactive = True
    else:
        tactive = True
    print tactive
    print bactive
    return render_to_response('bids.html', {'bids': mybids, 'tasks': mytasks, 'tactive': tactive, 'bactive': bactive}, RequestContext(request))
