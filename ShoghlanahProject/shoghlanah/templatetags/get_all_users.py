from django import template
from shoghlanah.models import UserProfile
import json

register = template.Library()

@register.filter
def get_all_the_users(lol):
	all_users = UserProfile.objects.all()
	return all_users