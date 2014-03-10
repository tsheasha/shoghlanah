from django.contrib.auth import authenticate
from shoghlanah.models import *
from django.contrib import admin

admin.site.register(UserProfile)
admin.site.register(Review)
admin.site.register(Action)
admin.site.register(Level)
admin.site.register(Level_Group)
admin.site.register(Task)
admin.site.register(Bid)
admin.site.register(Follow)
admin.site.register(Newsfeed)
admin.site.register(Discussion)
admin.site.register(level_action)
admin.site.register(User_Action)
admin.site.register(Photo)
admin.site.register(Reward)
admin.site.register(FacebookUserProfile)
admin.site.register(TwitterUserProfile)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductReview)
admin.site.register(Store) 
admin.site.register(Order)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Region)


def accept_report_task(modeladmin, request, queryset):
    for obj in queryset:
        # obj.task.delete()  # when completely deleted el stream bybooz
        obj.task.isArchived = True
        obj.task.save()
    queryset.update(accepted=True)
accept_report_task.short_description = "Accept selected reported tasks"


class ReportTaskAdmin(admin.ModelAdmin):
    list_display = ['task', 'count', 'accepted']
    ordering = ['count', 'accepted']
    actions = [accept_report_task]

admin.site.register(ReportTask, ReportTaskAdmin)
