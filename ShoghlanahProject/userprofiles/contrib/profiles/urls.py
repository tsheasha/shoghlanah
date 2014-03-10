from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('userprofiles.contrib.profiles.views',
    url(r'^(?P<user_name>[a-zA-Z0-9._-]+)/$', 'profile',
        name='userprofiles_profile'),
    url(r'^change/$', 'profile_change',
        name='userprofiles_profile_change'),
    url(r'^portfolio/(?P<user_name>[a-zA-Z0-9._-]+)/$', 'get_gallery',
        name='userprofiles_gallery'),
)
