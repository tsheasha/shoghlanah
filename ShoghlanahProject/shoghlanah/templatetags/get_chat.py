# -*- coding: utf-8 -*-
from django import template
import json
import datetime
from django.db.models import Q
import pusher
from shoghlanah.models import *
from django.utils import formats
import math
from django.utils import translation


register = template.Library()

@register.simple_tag
def get_bid(user_id,task_id):
	bid = Bid.objects.filter(user = UserProfile.objects.get(id = user_id) , task=Task.objects.get(id = task_id), isAccepted=True);
	if(len(bid) > 0 ):
		return translation.gettext('Accepted')
	else:
		return translation.gettext('Bidder')


@register.simple_tag
def getlast_bid(task_id,user_id):
	the_bids = Bid.objects.filter(task = Task.objects.get(id = task_id) , user = UserProfile.objects.get(id = user_id))
	if(len(the_bids)>0):
		bid = the_bids[len(the_bids) - 1].message
		return get_price(bid)
	else:
		return get_price(Task.objects.get(id = task_id).price)

@register.simple_tag
def getlast_bid_pay(task_id,user_id):
	the_bids = Bid.objects.filter(task = Task.objects.get(id = task_id) , user = UserProfile.objects.get(id = user_id))
	if(len(the_bids)>0):
		bid = the_bids[len(the_bids) - 1].message
		return bid
	else:
		return Task.objects.get(id = task_id).price

@register.filter
def bid_accepted(task_id,user_id):
	the_bids = Bid.objects.filter(task = Task.objects.get(id = task_id) , user = UserProfile.objects.get(id = user_id) , isAccepted = True)
	if(len(the_bids)>0):
		return True
	else:
		return False

@register.simple_tag
def get_messages_time(bid_id):
	messages = Discussion.objects.filter(bid = bid_id)
	messages = sorted(messages, key=lambda x: x.time, reverse=False)
	if len(messages) > 0:
		return formats.date_format(messages[-1].time, "DATETIME_FORMAT")
	else:
		return ''