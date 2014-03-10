from django.db import models
from django.contrib.auth.models import User
from time import *
import tagging
import datetime
#from userprofiles.contrib.accountverification.models import AccountVerification


##########################DOWN ARE ANY NEEDED FUNCTIONS##########################

RATINGS_CHOICES = (
    (1, 'Poor'),
    (2, 'Not '),
    (3, 'Average'),
    (4, 'Good'),
    (5, 'Great'),
)

#def validate_phone(value):
#    if re.match('^(010|011|012)[0-9]{8}',value) is None :
#        raise ValidationError(u'%s is not a valid number' % value)
#    if UserProfile.objects.filter(phone_number=value).count() > 1:
#        raise ValidationError("Phone number already exists")


def fib(n):
    fibs = {0: 0, 1: 1}
    if n in fibs:
        return fibs[n]

    if n % 2 == 0:
        fibs[n] = ((2 * fib((n / 2) - 1)) + fib(n / 2)) * fib(n / 2)
        return fibs[n]
    else:
        fibs[n] = (fib((n - 1) / 2) ** 2) + (fib((n+1) / 2) ** 2)
        return fibs[n]


def content_file_name(instance, filename):
    import datetime
    prefix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    #Appending current time and date as prefix to the filename to solve same filename bug
    x = '_'.join([prefix, filename.replace(" ", "_")])
    return '/'.join(['ProfilePic', instance.username, x])


def gallery_file_name(instance, filename):
    x = filename.replace(" ", "_")
    return '/'.join(['Gallery', instance.owner.username, x])


def product_image_path(instance, filename):
    x = instance.product.title.replace(" ", "_")
    return '/'.join(['Products', instance.product.user.username, instance.product.title])

def store_image_path(instance, filename):
    x = filename.replace(" ", "_")
    return '/'.join(['Store', instance.title, x])

##########################DOWN ARE THE MODELS##########################


class CustomUserManager(models.Manager):
    def create_user(self, username, email):
        return self.model._default_manager.create(username=username)

    def get_by_natural_key(self, first_name, last_name):
        return self.get(id=id,)


class Level_Group(models.Model):
    name = models.CharField(max_length=32, unique=True)  # null=True, blank=True
    description = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.name
'''
the save method in the ``Level`` model is the replacement of the use of
``DependentIntegerField`` above which caused the problem for south migrations,
and the save method checks if the value of the threshold isn't manually entered,
if not then it sets it to the default by the equation
'''


class Level(models.Model):
    group = models.ForeignKey(Level_Group)
    number = models.IntegerField(unique=True, null=False)  # , blank=True
    threshold = models.IntegerField(null=False, blank=True)
    #threshold = DependentIntegerField(lambda mi:mi.number*50,null=False,blank=True)

    def save(self, *args, **kwargs):
        if self.threshold is not None:
            super(Level, self).save(*args, **kwargs)
        elif self.number is not None:
            self.threshold = self.number*50
            super(Level, self).save(*args, **kwargs)

    def __str__(self):
        return '%s' % (self.number)

    def get_fib(self):
        return fib(self.number+75)


class Action (models.Model):
    level = models.ManyToManyField(Level, through='level_action')
    name = models.CharField(max_length=256, null=True, blank=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)

    def get_action(self):
        return self.name

    def __str__(self):
        return self.name


class UserProfile(User):
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'),)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    profile_picture = models.ImageField(upload_to=content_file_name, null=True, blank=True)
    cover_picture = models.ImageField(upload_to=content_file_name, null=True, blank=True)
    about = models.CharField(max_length=256, null=True, blank=True)
    job_title = models.CharField(max_length=32, null=True, blank=True, default="")
    mobile_number = models.CharField(null=True, blank=True, unique=True, max_length=16)
    complete_profile = models.IntegerField(default=21)
    got_started = models.BooleanField(default=False)
    city = models.CharField(max_length=32, null=True, blank=True, default="")
    location = models.CharField(max_length=128, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, default=200.0)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, default=200.0)
    job_history = models.CharField(max_length=128, null=True, blank=True)
    points = models.IntegerField(null=True, blank=True, default=0)
    video = models.CharField(max_length=2048, null=True, blank=True)
    isVerified = models.BooleanField(default=False)
    isRequest_Verification = models.BooleanField(default=False)
    isHidden_add = models.BooleanField(default=False)
    isHidden_phone = models.BooleanField(default=False)
    facebook_link = models.CharField(max_length=128, null=True, blank=True)
    twitter_link = models.CharField(max_length=128, null=True, blank=True)
    google_plus_link = models.CharField(max_length=128, null=True, blank=True)
    linkedin_link = models.CharField(max_length=128, null=True, blank=True)
    isVerified_email = models.BooleanField(default=False)
    isRequest_Verification_email = models.BooleanField(default=False)
    votes_up = models.IntegerField(null=True, blank=True, default=0)
    votes_down = models.IntegerField(null=True, blank=True, default=0)
    has_shop = models.BooleanField(default=False)

    objects = CustomUserManager()

    def getLevel(self):
        return self.points  # function that calculates the level according to the points!!

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def natural_key(self):
        return (self.id)

#tagging.register(UserProfile)

#class userprofiles_accountverification(AccountVerification):
#    userprofile = models.ForeignKey(UserProfile)


class Reward(models.Model):
    name = models.CharField(max_length=128)
    img = models.ImageField(upload_to='Badges')
    ar_name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name + " " + self.ar_name


class Task(models.Model):
    user = models.ForeignKey(UserProfile, related_name='task_owner')
    #review = models.ForeignKey(Review, null=True, blank=True)
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=256, null=True, blank=True)
    city = models.CharField(max_length=32)
    address = models.CharField(max_length=128)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    status = models.CharField(max_length=16, default='open')
    price = models.IntegerField(null=True, blank=True, default=0)
    reward = models.ForeignKey(Reward, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    isArchive = models.BooleanField(default=False)
    rating = models.IntegerField(null=True, blank=True, default=0)  # from 0% to 100%, it's calculated in percent.

    def __unicode__(self):
        return self.title

tagging.register(Task)  # To add "Tags" i.e Skills to the model "Task" using the "tagging" app in INSTALLED_APPS
tagging.register(UserProfile)


class Bid(models.Model):
    task = models.ForeignKey(Task)
    user = models.ForeignKey(UserProfile)
    message = models.CharField(max_length=320)
    last_msg = models.DateTimeField(null=True, blank=True)
    isAccepted = models.BooleanField(default=False)
    isRejected = models.BooleanField(default=False)
    isInvited = models.BooleanField(default=False)
    isReviewed = models.BooleanField(default=False)
    isPaied = models.BooleanField(default=False)

    def __unicode__(self):
        return self.message


class Review(models.Model):
    reviewer = models.ForeignKey(UserProfile, related_name='reviewer')
    reviewed = models.ForeignKey(UserProfile, related_name='reviewed')
    #reviewer = models.ManyToManyField(UserProfile, related_name='reviewer')
    #reviewed = models.ManyToManyField(UserProfile, related_name='reviewed')
    text = models.TextField(blank=True, max_length=20480)
    task = models.ForeignKey(Task)
    #punctuality = models.IntegerField(choices=RATINGS_CHOICES, default=1) #punctuality_rate
    #quality = models.IntegerField(choices=RATINGS_CHOICES, default=1) #quality_rate
    #attitude = models.IntegerField(choices=RATINGS_CHOICES, default=1) #attitude_rate
    #overall = models.IntegerField(choices=RATINGS_CHOICES, default=1) #avgerage_rate #function to calculate!!
    isRecommended = models.BooleanField(default=False)
    isUnrecommended = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.text

from tagging.models import *


class Follow(models.Model):
    follower = models.ForeignKey(UserProfile, related_name='follower')
    followed = models.ForeignKey(UserProfile, related_name='followed', null=True, blank=True)
    followed_skill = models.ForeignKey(Tag, related_name='followed_skill', null=True, blank=True)

    def __unicode__(self):
        if self.followed is not None:
            return self.follower.username + " -> " + self.followed.username
        else:
            return self.follower.username + " -> " + self.followed_skill.name


class Newsfeed(models.Model):
    user = models.ForeignKey(UserProfile)
    object_user = models.ForeignKey(UserProfile, related_name='object_user')
    object_task = models.ForeignKey(Task)
    content = models.CharField(max_length=2048)

    def __unicode__(self):
        return self.content


class Discussion(models.Model):
    sender = models.ForeignKey(UserProfile, related_name='sender')
    receiver = models.ForeignKey(UserProfile, related_name='receiver')
    message = models.CharField(max_length=20480)
    time = models.DateTimeField()
    bid = models.ForeignKey(Bid)

    def __unicode__(self):
        return self.message


class level_action(models.Model):
    level = models.ForeignKey(Level)
    action = models.ForeignKey(Action)
    counter = models.IntegerField(editable=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.action.get_action() == "create_task" or self.action.get_action() == "bid on a task":
            self.counter = self.level.get_fib()
            super(level_action, self).save(*args, **kwargs)
        else:
            super(level_action, self).save(*args, **kwargs)

    def __str__(self):
        return self.action.name


class User_Action(models.Model):
    user = models.ForeignKey(UserProfile)
    action = models.ForeignKey(Action)
    counter = models.IntegerField()


class Photo(models.Model):
    title = models.CharField(max_length=256)
    summary = models.TextField(blank=True,null=True)
    owner = models.ForeignKey(UserProfile)
    image = models.ImageField(upload_to=gallery_file_name)

    def __unicode__(self):
        return self.title


class FacebookUserProfile(models.Model):
    """
        For users who login via Facebook.
    """
    user = models.ForeignKey(UserProfile, related_name='facebook_profile')
    facebook_uid = models.CharField(max_length=20, unique=True, db_index=True)
    accesstoken = models.CharField(max_length=1024)
    profile_image_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=160, blank=True, null=True)
    email = models.CharField(max_length=160, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    about_me = models.CharField(max_length=160, blank=True, null=True)

    def __unicode__(self):
        return u"%s's profile" % self.user


class TwitterUserProfile(models.Model):
    """
        For users who login via Twitter.
    """
    user = models.ForeignKey(UserProfile, related_name='twitter_profile')
    screen_name = models.CharField(max_length=200)
    email = models.CharField(max_length=160, blank=True, null=True)
    profile_image_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=160, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    access_token = models.CharField(max_length=200)
    access_secret = models.CharField(max_length=200)

    def __unicode__(self):
        return u"%s's profile" % self.user


class LinkedinUserProfile(models.Model):
    """
        For users who login via LinkedIn.
    """
    user = models.ForeignKey(UserProfile, related_name='linkedin_profile')
    linkedin_uid = models.CharField(max_length=20, unique=True, db_index=True)
    accesstoken = models.CharField(max_length=1024)
    profile_image_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=160, blank=True, null=True)
    email = models.CharField(max_length=160, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    about_me = models.CharField(max_length=160, blank=True, null=True)

    def __unicode__(self):
        return u"%s's profile" % self.user


class GoogleUserProfile(models.Model):
    """
        For users who login via Google.
    """
    user = models.ForeignKey(UserProfile, related_name='google_profile')
    google_uid = models.CharField(max_length=20, unique=True, db_index=True)
    accesstoken = models.CharField(max_length=1024)
    profile_image_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=160, blank=True, null=True)
    email = models.CharField(max_length=160, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    about_me = models.CharField(max_length=160, blank=True, null=True)

    def __unicode__(self):
        return u"%s's profile" % self.user


class ReportTask(models.Model):
    task = models.ForeignKey(Task, related_name='reported_task')
    count = models.IntegerField(default=0)
    reason = models.TextField(max_length=8192)
    accepted = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)


class Product(models.Model):
    user = models.ForeignKey(UserProfile, related_name='product_owner')
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=256, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True, default=0)
    date = models.DateTimeField(auto_now_add=True)
    stock = models.IntegerField(default=10)

    class Meta:
        unique_together = (("user", "title"),)

    def __unicode__(self):
        return u"%s's %s" % (self.user, self.title)

    def get_images(self):
        return ProductImage.objects.filter(product=self, isMain=False)

    def get_main_image(self):
        return ProductImage.objects.get(product=self, isMain=True)

    def get_reviews(self):
        return ProductReview.objects.filter(product=self)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='product')
    image = models.ImageField(upload_to=product_image_path, null=True, blank=True)
    isMain = models.BooleanField(default=False)


class ProductReview(models.Model):
    product = models.ForeignKey(Product, related_name='reviewed_product')
    review = models.ForeignKey(Review, related_name='product_review')
    date = models.DateTimeField(auto_now_add=True)


    def __unicode__(self):
        return u'%s: %s, belongs to %s' % (self.id, self.title, self.user)


class Country(models.Model):
    name = models.CharField(max_length=64)
    arabic_name = models.CharField(max_length=64)

    def chained_relation(self):
        return self.city_set.filter(is_present=True)

    def __unicode__(self):
        return u"%s" % self.name


class City(models.Model):
    name = models.CharField(max_length=64)
    country = models.ForeignKey(Country)
    arabic_name = models.CharField(max_length=64)

    def __unicode__(self):
        return u"%s" % self.name


class Region(models.Model):
    name = models.CharField(max_length=64)
    city = models.ForeignKey(City)
    arabic_name = models.CharField(max_length=64)

    def __unicode__(self):
        return u"%s" % self.name

PAYMENT_CHOICES = (('CASH', 'Cash'),) #Used for the payment choices in the Order model.

class Order(models.Model):

    quantity = models.IntegerField()
    price = models.IntegerField()
    payment_choice = models.CharField(max_length=32, choices = PAYMENT_CHOICES, default=1)
    seller = models.ForeignKey(UserProfile, related_name='seller_orders')
    buyer = models.ForeignKey(UserProfile, related_name='buyer_orders')
    product = models.ForeignKey(Product, related_name='product_orders')
    discussion = models.ForeignKey(Discussion, related_name='order_discussion', null = True)
    status = models.CharField(max_length=12, default='open')
    address = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now_add=True)
    mobile_number = models.CharField(max_length = 20)
    #phone_number = models.CharField(max_length = 20, null = True)
    city = models.ForeignKey(City)
    region = models.ForeignKey(Region, null = True) #Null = true, just in case City doesn't have related regions.
    special_notes = models.TextField(max_length = 1024, null = True)

    def __unicode__(self):
        return u"%s ordered %s" % (self.buyer, self.product)

class Store(models.Model):
    image = models.ImageField(upload_to=store_image_path, null=True, blank=True)
    name = models.CharField(max_length = 32)
    title = models.CharField(max_length = 64)
    featured = models.BooleanField(default = False)

