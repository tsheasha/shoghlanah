from django import template
from notification.models import Notice
import json

register = template.Library()

@register.filter
def get_user_new_notifications(user_id):
    new_notifications = Notice.objects.filter(recipient=user_id).filter(unseen=True)
    return new_notifications

@register.filter
def get_user_new_notifications_count(user_id):
    new_notifications = Notice.objects.filter(recipient=user_id).filter(unseen=True)
    new_notifications_count = new_notifications.count()
    return new_notifications_count




