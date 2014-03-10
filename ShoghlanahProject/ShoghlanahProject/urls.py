from django.conf.urls import patterns, include, url
# from haystack.views import SearchView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.simple import redirect_to
from django.conf import settings
from shoghlanah.models import Country, City
admin.autodiscover()


handler404 = 'shoghlanah.views.not_found'
handler500 = 'shoghlanah.views.server_error'
ignore_latest_activity = ['notifications', 'media', 'static', 'message']

urlpatterns = patterns('',
    url(r'session_security/', include('session_security.urls')),
    # Examples:
    # url(r'^$', 'ShoghlanahProject.views.home', name='home'),
    # url(r'^ShoghlanahProject/', include('ShoghlanahProject.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^filter_profile/$', 'userprofiles.contrib.profiles.views.filter_stream'),
    url(r'^accounts/', include('userprofiles.urls')),

    #url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
)
    #  Url grouping
    #  instead of having
    #   url(r'^results/', 'shoghlanah.search.search')
    #   url(r'^browse/(?P<category_id>\d+)/$', 'shoghlanah.tasks.category'),
    #   url(r'^browse/', 'shoghlanah.tasks.browse'),
    #
    #  this is more readable and organized
    #   urlpatterns = patterns('shoghlanah.search',
    #       url(r'^results/', 'search')
    #   )
    #
    #   urlpatterns += patterns('shoghlanah.tasks',
    #       url(r'^browse/(?P<category_id>\d+)/$', 'category'),
    #       url(r'^browse/', 'browse'),
    #   )
    ###############URLS START HERE###############
urlpatterns += patterns('shoghlanah.user_profile',
    url(r'^profile/(?P<user_name>[a-zA-Z0-9._-]+)/follow/$', 'follow'),
    url(r'^profile/(?P<user_name>[a-zA-Z0-9._-]+)/unfollow/$', 'unfollow'),
    url(r'^profile/(?P<user_name>[a-zA-Z0-9._-]+)/edit/delete_profile_picture/$', 'delete_profile_picture'),
    url(r'^profile/(?P<user_name>[a-zA-Z0-9._-]+)/edit/delete_cover_picture/$', 'delete_cover_picture'),
    url(r'^profile/edit/$', 'edit_view', name="edit_profile"),
    url(r'^profile/edit/save/$', 'edit'),
    # url(r'^profile/(?P<user_name>[a-zA-Z0-9._-]+)/verify/mobile_number/$', 'verify_mobile_number'),
    url(r'^profile/(?P<user_name>[a-zA-Z0-9._-]+)/verify/email/$', 'verify_email'),
    # url(r'^check_email_duplicates/$', 'check_email_duplicates'),
    url(r'^check_number_duplicates/$', 'check_number_duplicates'),
    url(r'^send_invitation/$', 'send_invitation', name='send_invitation'),
    url(r'^clearnewnotifications/$', 'clearnewnotifications', name='clearnewnotifications'),
)

urlpatterns += patterns('shoghlanah.upload',
    url(r'^project/ajax_upload/$', 'ajax_upload', name="ajax_upload"),
    url(r'^project/$', 'upload_page', name="upload_page"),
    # url(r'^addaction/(?P<count>[0-9])/$', 'action_gallery', name='addtostream_gallery')
)

urlpatterns += patterns('shoghlanah.facebook',
    url(r'^facebook/login/$', 'facebook_login', name="facebook_login"),
    url(r'^facebook/login/done/$', 'facebook_login_done', name="facebook_login_done"),
    url(r'^facebook/disconnect/$', 'facebook_disconnect', name="facebook_disconnect"),
    url(r'^facebook/post/task$', 'post_task_fb', name="fb_post"),
    url(r'^facebook/sync/$', 'sync_friends', name="sync_facebook"),
    url(r'^facebook/invite/$', 'social_invite', name="facebook_invite"),
)

urlpatterns += patterns('shoghlanah.twitter',
    url(r'^twitter/login/?$', "twitter_login", name="twitter_login"),
    url(r'^twitter/login/done/?$', "twitter_login_done", name="twitter_login_done"),
    url(r'^twitter/disconnect/$', 'twitter_disconnect', name="twitter_disconnect"),
    url(r'^twitter/message/$', 'direct_message', name="twitter_msg"),
    url(r'^twitter/sync/$', 'sync_friends', name="sync_twitter"),
    url(r'^twitter/invite/$', 'social_invite', name="twitter_invite"),
)


urlpatterns += patterns('shoghlanah.linkedin',
    url(r'^linkedin/login/$', 'linkedin_login', name="linkedin_login"),
    url(r'^linkedin/login/done/$', 'linkedin_login_done', name="linkedin_login_done"),
    url(r'^linkedin/disconnect/$', 'linkedin_disconnect', name="linkedin_disconnect"),
)


urlpatterns += patterns('shoghlanah.google',
    url(r'^google/login/$', 'google_login', name="google_login"),
    url(r'^google/login/done/$', 'google_login_done', name="google_login_done"),
    url(r'^google/disconnect/$', 'google_disconnect', name="google_disconnect"),
)


urlpatterns += patterns('shoghlanah.views',
    url(r'^$', "master", name="home"),
    # url(r'^404/$', "not_found"),
    # url(r'^500/$', "server_error"),
    url(r'^discover/$', "discover"),
    url(r'^more/$', "load_more"),
    url(r'^skill/(?P<skill_id>\d+)/$', 'view_skill'),
    url(r'^filter/$', "filter_stream"),
    url(r'^latest/$', "load_latest"),
    url(r'^log_in/$', "log_in"),
    url(r'^logout_view/$', "logout_view", name='logout_view'),
    url(r'^search/$', "search"),
    url(r'^results/$', include('haystack.urls')),
    url(r'^results/filter/$', "filter_Search"),
    url(r'^test/$', "notification_test"),
    url(r'^switch/(?P<lang>(en|ar))/$', "switch_lang"),
    url(r'^results/people/filter_by_votes/$', "filter_people_search"),
    url(r'^notifications/refresh/$', "refresh_notifications"),
    url(r'^skill/(?P<skill_id>[a-zA-Z0-9._-]+)/follow/$', 'follow'),
    url(r'^skill/(?P<skill_id>[a-zA-Z0-9._-]+)/unfollow/$', 'unfollow'),
    url(r'^send/email$', 'email_html', name="email_html"),
    url(r'^survey/$', 'survey', name="survey"),
    url(r'^passwords/$', 'passwords', name="passwords"),
)

urlpatterns += patterns('shoghlanah.tasks',
    url(r'^task/post_task/$', "post_task", name='post_task'),
    url(r'^task/(?P<task_id>\d+)/$', 'viewTask', name='viewTask'),
    url(r'^task/edit_task/(?P<task_id>\d+)/$', 'edit_task',),
    url(r'^task/(?P<task_id>\d+)/delete/$', 'delete_task'),
    url(r'^chatlist/(?P<task_id>\d+)/$', 'chat_list'),
    url(r'^message/(?P<user_id>\d+)/(?P<task_id>\d+)/$', 'discussion'),
    url(r'^message/(?P<user_id>\d+)/(?P<task_id>\d+)/(?P<bid_id>\d+)/$', 'discussion'),
    url(r'^message/(?P<receiver_id>\d+)/(?P<task_id>\d+)/sendMsg/?$', 'message'),
    url(r'^message/(?P<receiver_id>\d+)/(?P<task_id>\d+)/(?P<bid_id>\d+)/sendMsg/?$', 'message'),
    url(r'^user/(?P<sender_user_name>[a-zA-Z0-9._-]+)/message/(?P<receiver_id>\d+)/auth/?$', 'authUser'),
    url(r'^pay/(?P<bid_id>\d+)/$', 'pay', name='pay'),
    url(r'^reviewing/(?P<receiver_id>\d+)/(?P<bid_id>\d+)/$', 'getreviews', name='reviews'),
    url(r'^review/(?P<bid_id>\d+)/(?P<receiver_id>\d+)/$', 'review'),
    url(r'^search/similar_task/(?P<task_id>\d+)/$', "similarTask", name='similar'),
    url(r'^task/invite/(?P<task_id>\d+)/(?P<contractor_id>\d+)$', "invite_contractor", name="invite_contractor"),
    #url(r'^report_task/$', "report_task", name="report_task"),
)

urlpatterns += patterns('shoghlanah.orders',
    url(r'^product/(?P<product_id>\d+)/order/$', "create", name='create_order'),
    url(r'^order/(?P<order_id>\d+)/update/$', "update", name='update_order'),
    url(r'^order/(?P<order_id>\d+)/delete/$', "delete", name='delete_order'),
    url(r'^order/(?P<order_id>\d+)/view/$', "open", name='view_order'),
    url(r'^product/\d+/order/city-to-region/(?P<city>\d+)/$', "city_to_region"),
)

urlpatterns += patterns('shoghlanah.products',
    url(r'^product/create/$', "create", name='create_product'),
    url(r'^product/(?P<product_id>\d+)/update/$', "update", name='update_product'),
    url(r'^product/(?P<product_id>\d+)/delete/$', "delete", name='delete_product'),
    url(r'^product/(?P<product_id>\d+)/view/$', "open", name='view_product'),
    url(r'^products/(?P<user_id>\d+)/$', "index", name='view_user_products'),
    url(r'^products/stores_home/$', "stores_home", name='stores_home'), #to be the future home page
)

urlpatterns += patterns('shoghlanah.bids',
    url(r'^bid/(?P<bid_id>\d+)/(?P<bid_msg>\d+)/$', 'bid'),
    url(r'^bid/(?P<bid_id>\d+)/$', 'accept_bid'),
    url(r'^myshoghlanahs/$', "viewbids", name='my_bids'),
)

urlpatterns += patterns('shoghlanah.notifications',
    url(r"^notifications/notices/$", 'notices', name="notification_notices"),
    url(r"^notifications/$", 'view_all_notifications', name="all_notifications"),
    url(r"^notifications/(?P<notification_id>\d+)/$", 'view_notification', name="one_notifications"),
    url(r"^notifications/settings/$", 'notice_settings', name="notification_notice_settings"),
    url(r"^notifications/(\d+)/$", 'single', name="notification_notice"),
    url(r"^notifications/feed/$", 'feed_for_user', name="notification_feed_for_user"),
    url(r"^notifications/mark_all_seen/$", 'mark_all_seen', name="notification_mark_all_seen"),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
         'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
