#!/usr/bin/env python
import os
import sys
from django.conf import settings

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ShoghlanahProject.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

    if "notification" in settings.INSTALLED_APPS:
        print "Creating NoticeTypes"
        from notification import models as notification
        notification.create_notice_type("post_task", ("Posted a shoghlanah"), ("Someone posted a shoghlanah"))
        notification.create_notice_type("open_discussion", ("Opened a discussion"), ("Someone wants to discuss something with you."))
        notification.create_notice_type("bid_changed", ("A bid is changed"), ("Someone changed the bid."))
        notification.create_notice_type("new_follower", ("A new Follower"), ("Someone followed someone."))
        notification.create_notice_type("invite_to_task", ("Invitation to a shoghlanah"), ("Someone invited someone to a shoghlanah."))
    else:
        print "Skipping creation of NoticeTypes as notification app not found"
