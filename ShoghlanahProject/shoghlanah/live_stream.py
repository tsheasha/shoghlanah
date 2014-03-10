from shoghlanah.models import *
from actstream.models import Action, user_stream
from tagging.models import *
import pusher
from django.conf import settings
import json
from django.utils import simplejson
from userprofiles.contrib.profiles.views import get_followers

pusher.app_id = settings.PUSHER_APP_ID
pusher.key = settings.PUSHER_KEY
pusher.secret = settings.PUSHER_SECRET

p = pusher.Pusher()

def profile_stream(user):
    """
    Retrieves all Action Objects from database related to User
    where User could be the one doing the action or, part of 
    an Action or even have an Action performed on them
    """
    userprofile = UserProfile.objects.get(username=user.username)

    stream = []

    if user is not None:
        stream.extend(Action.objects.filter(actor_object_id=user.id))

        target_objects = Action.objects.filter(target_object_id=user.id)
        for obj in target_objects:
            if not isinstance(obj.target, UserProfile):
                target_objects = list(target_objects).remove(obj)
                if target_objects is None:
                    break

        if target_objects is not None:
            stream.extend(target_objects)
        stream = list(set(stream))
        stream = sorted(stream, key=lambda action : action.timestamp)

    for item in stream:
        if item.actor is None or item.action_object is None or item.target is None:
            item.delete()

    follow_actions = Action.objects.filter(actor_object_id=user.id, verb="followed")
    follow_duplicates = [item.target for item in follow_actions]
    
    for item in follow_duplicates:
        if follow_duplicates.count(item) > 1:
            if list(follow_actions)[follow_duplicates.index(item)] is not None and list(follow_actions)[follow_duplicates.index(item)].id is not None:
                list(follow_actions)[follow_duplicates.index(item)].delete()
                follow_duplicates.remove(item)
    return stream
    
def add_action(actor, verb, action_object, description, target):
    """
    API to add Action to database:
    actor: Performer of Action
    verb: Action Performed
    action_object: object related to Action if any
    description: details on the action
    target: Who or what the action was done for or on.
    """

    new_action = Action(actor=actor, verb=verb, action_object=action_object, description=description, target=target)
    new_action.save()  
    
    if isinstance(action_object, Task):
        items = TaggedItem.objects.filter(object_id=action_object.id)
        for item in items:
            follows = Follow.objects.filter(followed_skill=item.tag)
            for follow in follows:
                if follow.follower.username != actor.username:
                    if isinstance(target, UserProfile):
                        if follow.follower.username != target.username:
                            p['stream_' + str(follow.follower.username)].trigger('liveStream', {})
                    else:
                        p['stream_' + str(follow.follower.username)].trigger('liveStream', {})

    followers = Follow.objects.filter(followed__id=actor.id)
    for item  in followers:
        if item.follower.username != actor.username:
            if isinstance(target, UserProfile):
                if item.follower.username != target.username:
                    p['stream_' + str(item.follower.username)].trigger('liveStream', {})
            else:            
                p['stream_' + str(item.follower.username)].trigger('liveStream', {})

    p['stream_' + str(actor.username)].trigger('liveStream', {})
    if isinstance(target, UserProfile) and target.username != actor.username:
        p['stream_' + str(target.username)].trigger('liveStream', {})
        

    if verb == "task_post" or verb == "task_assigned":
        p['discover'].trigger('discover_shoghlanah', {})

    return new_action


def get_stream(request, user, verb="", profile=False):
    """
    This method builds the stream that appears in the homepage of a user
    maintaining a maximum length that when exceeded more items of the stream
    are loaded per request. The stream is sorted by timestamp of the Action
    being done keeping the most recent Action at the beginning.
    """
    userprofile = UserProfile.objects.get(username=user.username)
    
    stream = []
    followers = get_followers(request, request.user.username)
    if not profile:
        for item in followers['followers']:
            if item != None and isinstance(item.followed, UserProfile):
                stream.extend(list(reversed(profile_stream(item.followed))))
    follows = Follow.objects.filter(follower=userprofile)
    for action in follows:
        if action != None and isinstance(action.followed_skill, Tag):
            items = TaggedItem.objects.filter(tag=action.followed_skill)
            for item in items:
                if isinstance(item.object, Task):
                    stream.extend(Action.objects.filter(action_object_object_id=item.object.id))
    
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
    stream = list(set(stream))
    stream = list(reversed(sorted(stream, key=lambda action: action.timestamp)))
    for item in stream:
        if verb != "":
            if item.verb != verb:
                list(stream).remove(item) 
            if item.actor is None:
                list(stream).remove(item)
                item.delete()
        if item.actor is None or item.action_object is None or item.target is None:
            item.delete()
    follow_actions = Action.objects.filter(actor_object_id=user.id, verb="followed")
    follow_duplicates = [item.target for item in follow_actions]
    
    for item in follow_duplicates:
        if follow_duplicates.count(item) > 1:
            if list(follow_actions)[follow_duplicates.index(item)] is not None and list(follow_actions)[follow_duplicates.index(item)].id is not None:
                list(follow_actions)[follow_duplicates.index(item)].delete()
                follow_duplicates.remove(item)

    if len(stream) > 10 and verb == "":
        stream = stream[0:10]
        output_dict = {'stream' : stream}
        output_dict.update({'more': True})
    else :
        output_dict = {'stream' : stream}
    return output_dict

def get_discover_stream(request):
    task_stream = Action.objects.filter(verb="task_post")
    stream = []
    for item in task_stream:
        stream.append(item)
    stream = list(set(stream))
    stream = list(reversed(sorted(stream, key=lambda action: action.timestamp)))

    if len(list(stream)) > 10:
        stream = stream[0:10]

    for item in stream: 
        if item.actor is None:
            list(stream).remove(item)
            item.delete()
    output_dict = {'stream': stream}
    return output_dict
    
