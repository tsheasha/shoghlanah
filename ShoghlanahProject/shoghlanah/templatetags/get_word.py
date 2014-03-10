from django import template
from shoghlanah.models import UserProfile
from django.utils import formats, translation
import json

register = template.Library()

@register.filter
def translate(word):
	return word