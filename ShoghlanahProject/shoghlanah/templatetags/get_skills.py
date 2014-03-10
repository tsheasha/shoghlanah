from django import template
from tagging.models import Tag
from django.template.defaultfilters import stringfilter
import json
import re

register = template.Library()

def get_json_skills():
    """
    Used to get all the skills (Tags) and pass them as json template tag,
    and then used in "Tag-it" script the posttask.html as a list of tags for autocompletion
    """
    skills = Tag.objects.all()
    output = []
    
    for skill in skills:
        output.append(skill.name)
    
    json_skills = json.dumps(list(set(output)))
    return json_skills

get_json_skills = register.simple_tag(get_json_skills)

@register.filter
@stringfilter
def trim(value):
    x = re.sub('\s+',' ',value)
    return x
