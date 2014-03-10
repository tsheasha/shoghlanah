from django import template
from shoghlanah.models import UserProfile, Task, Reward
import json
from tagging.models import Tag
from django.conf import settings

register = template.Library()

#@register.simpletag
def get_fields_json():
    '''
        Gets fields first_name and last_name and full name of all Users and Gets the names of all Tasks and Skills
        puts them all in a list, removes duplicates, then returns the list in json, to be accessed in javascript
        this list is the list of auto-complete possibilities.
        Registers a django custom tag.


        Returns:
           returns a list of strings of the users' first_name, last_name , full name , tasks' name and skills' name

        This shouldn't be called from within another method, instead it should be accessed through the browser.

    '''
    users = UserProfile.objects.all()
    tasks = Task.objects.all()
    skills = Tag.objects.all()
    rewards = Reward.objects.all()
    output = []

    for user in users:
        output.append(user.first_name)
        output.append(user.last_name)
        if(user.first_name and user.last_name):
            output.append(user.first_name + " " + user.last_name)
        output.append(user.job_title)
    for task in tasks:
        # output.append(task.title)
        output.append(task.city)
    for reward in rewards:
        output.append(reward.name)
        output.append(reward.ar_name)
    for skill in skills:
        output.append(skill.name)
    # output.append("New")
    # output.append("In Progress")
    # output.append("Done")
    if output.count(None) >= 1:
        output = filter(lambda out: out != None, output)
    x = json.dumps(list(set(output)))
    return x
get_fields_json = register.simple_tag(get_fields_json)


def get_city_json():
    '''
        Gets field city of tasks and userprofile puts them all in a list, removes duplicates, then returns the list in json, to be accessed in javascript
        this list is the list of auto-complete possibilities.
        Registers a django custom tag.


        Returns:
           returns a list of city name
    '''
    users = UserProfile.objects.all()
    tasks = Task.objects.all()
    skills = Tag.objects.all()
    rewards = Reward.objects.all()
    output = []

    for user in users:
        output.append(user.city)
    for task in tasks:
        output.append(task.city)
    if output.count(None) >= 1:
        output = filter(lambda out: out != None, output)
    x = json.dumps(list(set(output)))
    return x
get_city_json = register.simple_tag(get_city_json)


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

def get_tasks_json():
    tasks = Task.objects.all()
    skills = Tag.objects.all()
    rewards = Reward.objects.all()
    users = UserProfile.objects.all()
    output = []

    for user in users:
        output.append(user.first_name)
        output.append(user.last_name)
        output.append(user.first_name + " " + user.last_name)
    for reward in rewards:
        output.append(reward.name)
        output.append(reward.ar_name)
    if output.count(None) >= 1:
        output = filter(lambda out: out != None, output)
    x = json.dumps(list(set(output)))
    return x
get_tasks_json = register.simple_tag(get_tasks_json)
