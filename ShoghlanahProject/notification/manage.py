#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ShoghlanahProject.settings")

    from django.core.management import execute_from_command_line
    from django.conf import settings
    from django.db.models import get_models, signals

    if "notification" in settings.INSTALLED_APPS:
        from notification import models as notification

        def create_notice_types(app, created_models, verbosity, **kwargs):
            notification.create_notice_type("friends_invite", _("Invitation Received"), _("you have received an invitation"))
            notification.create_notice_type("friends_accept", _("Acceptance Received"), _("an invitation you sent has been accepted"))

        signals.post_syncdb.connect(create_notice_types, sender=notification)
    else:
        print "Skipping creation of NoticeTypes as notification app not found"

    execute_from_command_line(sys.argv)
