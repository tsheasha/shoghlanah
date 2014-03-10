def settings(request):
    from django.conf import settings
    dic = {}
    for elem in settings.TEMPLATE_VISIBLE_SETTINGS:
        dic[elem] = getattr(settings, elem, '')
    return dic
