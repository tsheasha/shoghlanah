from django import template
from shoghlanah.models import *
from sorl.thumbnail import get_thumbnail
from django.utils import translation
import random

register = template.Library()


@register.filter
def get_profile_pic(user_id):
    pic = ''
    if isinstance(user_id, int):
        pic = UserProfile.objects.get(id=user_id).profile_picture
    else:
        try:
            newId = int(user_id)
            pic = UserProfile.objects.get(id=newId).profile_picture
        except:
            pass
    if pic == '' or pic is None:
        return 'profile-default.jpg'
    return pic


@register.filter
def get_random_pic(x):
    pic = ''
    profile_pictures = ["../media/ProfileDefaults/profile_pic_default.png", "../media/ProfileDefaults/profile_pic_default2.png", "../media/ProfileDefaults/profile_pic_default3.png", "../media/ProfileDefaults/profile_pic_default4.png", "../media/ProfileDefaults/profile_pic_default5.png"]
    pic = profile_pictures[int(random.random() * len(profile_pictures))]
    return pic


@register.filter
def get_cover_pic(user_id):
    if isinstance(user_id, int):
        pic = UserProfile.objects.get(id=user_id).cover_picture
    else:
        newId = int(user_id)
        pic = UserProfile.objects.get(id=newId).cover_picture
    if pic == '':
        return 'profile-default.jpg'
    return pic


@register.filter
def get_thumb_pic(user_id):
    pic = get_profile_pic(user_id)
    im = get_thumbnail(pic, '65x65', crop='center', quality=99)
    return im


@register.filter
def get_rewards(request):
    rewards = Reward.objects.all()
    return rewards


@register.filter
def isFollowing(follower_id, followed_id):
    if isinstance(follower_id, int) and isinstance(followed_id, int):
        try:
            Follow.objects.get(follower__id=follower_id, followed__id=followed_id)
            return True
        except Follow.DoesNotExist:
            return False


@register.filter
def isFollowingSkill(follower_id, followed_skill_id):
    if isinstance(follower_id, int) and isinstance(followed_skill_id, int):
        try:
            Follow.objects.get(follower__id=follower_id, followed_skill__id=followed_skill_id)
            return True
        except Follow.DoesNotExist:
            return False


@register.filter
def checkUserFacebook(user_id):
    if isinstance(user_id, int):
        try:
            FacebookUserProfile.objects.get(user__id=user_id)
            return True
        except FacebookUserProfile.DoesNotExist:
            return False


@register.filter
def checkUserTwitter(user_id):
    if isinstance(user_id, int):
        try:
            TwitterUserProfile.objects.get(user__id=user_id)
            return True
        except TwitterUserProfile.DoesNotExist:
            return False


@register.filter
def gotStarted(user_id):
    return UserProfile.objects.get(id=user_id).got_started


@register.filter
def truncate(data, size=0):
    if data is not None:
        if isinstance(data, unicode):
            x = data
        elif isinstance(data, int):
            x = str(data)
            size = len(x)
            if size == 6:
                x = (x[:size-3] + translation.gettext("K"))
            elif size > 6:
                x = (x[:size-6] + translation.gettext("M"))
            return x
        elif isinstance(data, UserProfile):  # if it's an object, assume the case it's of type userprofile object
            x = data.first_name + ' ' + data.last_name
        else:
            x = data

        info = (x[:size-2] + '..') if len(x) > size else x
        return info


@register.filter
def sessionDeleteSocial(request):
    if "Social" in request.session:
        del request.session["Social"]

@register.filter
def reorderList(list,index):
    x = list[:index]
    y = list[index:]
    list = y+x
    return list
