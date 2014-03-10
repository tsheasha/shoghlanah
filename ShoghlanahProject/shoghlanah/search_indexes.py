import datetime
from haystack import indexes
from shoghlanah.models import Task, UserProfile
from haystack.query import SearchQuerySet

"""
Each class of the following is used to register a certain model to have an index
and be included in the Search.
The attributes in each class are the fields of the model to search on example;
You can search a certain user (UserProfileIndex) by  first name or last name

"""

class TaskIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    task_creator = indexes.CharField(model_attr='user')
    status = indexes.CharField(model_attr='status')
    title = indexes.EdgeNgramField(model_attr='title')
    city = indexes.CharField(model_attr='city')
    reward = indexes.CharField(model_attr='reward',null=True)
    price = indexes.IntegerField(model_attr='price',null=True)
    location = indexes.CharField(model_attr='address')
    tags = indexes.MultiValueField()
    def prepare_tags(self, obj): 
        return [tag.name for tag in obj.tags.all()]

    def get_model(self):
        return Task 

class UserProfileIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    first_name = indexes.CharField(model_attr='first_name')
    last_name = indexes.CharField(model_attr='last_name')
    location = indexes.CharField(model_attr='location',null=True)
    job_title = indexes.CharField(model_attr='job_title',null=True)
    votesup = indexes.IntegerField(model_attr='votes_up',null=True)
    isVerified = indexes.BooleanField(model_attr='isVerified',default=False)
    tags = indexes.MultiValueField()
    def prepare_tags(self, obj): 
        return [tag.name for tag in obj.tags.all()]

    def get_model(self):
        return UserProfile


