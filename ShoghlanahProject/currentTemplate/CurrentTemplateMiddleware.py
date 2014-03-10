from models import UserActivity
from datetime import datetime
from django.conf import settings
import re

compiledLists = {}

class CurrentTemplateMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
            return
        urlsModule = __import__(settings.ROOT_URLCONF, {}, {}, [''])
        skipList = getattr(urlsModule, 'ignore_latest_activity', None)
        skippedPath = request.path
        if skippedPath.startswith('/'):
            skippedPath = skippedPath[1:]
        if skipList is not None:
            for expression in skipList:
                compiledVersion = None
                if not compiledLists.has_key(expression):
                    compiledLists[expression] = re.compile(expression)
                compiledVersion = compiledLists[expression]
                if compiledVersion.search(skippedPath):
                    return
        
        activity = None
        try:
            activity = request.user.useractivity
        except:
            activity = UserActivity()
            activity.user = request.user
            activity.latest_activity = datetime.now()
            activity.current_template = request.build_absolute_uri()
            activity.save()
            return
        activity.latest_activity = datetime.now()
        activity.current_template = request.build_absolute_uri()
        activity.save()
