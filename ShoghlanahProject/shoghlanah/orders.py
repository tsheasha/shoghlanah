from shoghlanah.models import *
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, Http404
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from shoghlanah.views import email_html
from django.template import RequestContext
from django.forms import ModelChoiceField
from django.utils import translation
import json as simplejson
from django.forms.widgets import RadioSelect, CheckboxInput
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy

@login_required
def create(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
        all_followers = Follow.objects.filter(followed=product.user)
        if(request.method=='POST'):
            orderForm = OrderForm(request.POST)
            if orderForm.is_valid():
                return orderForm.save(product_id, request.user.id)
            else:
                return render_to_response("shop/order/create.html", {'product':product, 'order_form':orderForm, 'all_followers': all_followers}, RequestContext(request))
        else:
            current_user = UserProfile.objects.get(id=request.user.id)
            data = {'phone_number':current_user.mobile_number}
            orderForm = OrderForm(initial=data, auto_id='order_%s') #Initial data has phone number + product(hidden field), auto_id is changed to prevent ambiguity
            return render_to_response("shop/order/create.html", {'product':product, 'order_form':orderForm, 'all_followers': all_followers}, RequestContext(request))
    except Product.DoesNotExist:
        return Http404

@login_required
def update(request, order_id):
    return HttpResponse("update")


@login_required
def delete(request, order_id):
    return HttpResponse("delete")


def open(request, order_id):
    return HttpResponse("open")

def city_to_region(request, city):
    #Method that retrieves list of region in 'city' and returns a json dump of the list with the ids and names of the region.
    parent=request.GET.get('city') or city
    ret=[]
    if parent:
        for child in Region.objects.filter(city__id=parent):
            cur_language = translation.get_language()
            if cur_language == 'ar':
                ret.append(dict(id=child.id, value=child.arabic_name))
            else:
                ret.append(dict(id=child.id, value=unicode(child)))
    #In case an empty region choice is desired in the dropdown menu.
    #if len(ret)!=1:
    #    ret.insert(0, dict(id='', value='---'))
    return HttpResponse(simplejson.dumps(ret), 
              content_type='application/json')

class ChoiceFieldTranslated(ModelChoiceField):
    #Extends ModelChoiceField, used for the city and region. Returns the arabic name (which is a field present in all 3 models, Country City & Region),
    # if the current language is Arabic, else returns the name.
    def label_from_instance(self, obj):
        cur_language = translation.get_language()
        if cur_language == 'ar':
            return obj.arabic_name
        else:
            return obj.name

def validate_positive(value):
    #Validator to check that order quantity is positive.
    if value < 1:
        raise ValidationError(u'Quantity must be greater than 0!')

class OrderForm(forms.Form):
    #The form used to order a product.
    #IMPORTANT: The form html elements are prefixed by "order_" instead of "id_"!
    quantity = forms.IntegerField(label=ugettext_lazy('Quantity'), validators=[validate_positive], initial = 1)
    payment_choice = forms.ChoiceField(label = ugettext_lazy('Payment Method'),
        widget = forms.RadioSelect(attrs={'class' : 'regular-radio'}), choices = PAYMENT_CHOICES, initial = 'CASH')

    address = forms.CharField(label = ugettext_lazy('Address'), max_length=64)
    city = ChoiceFieldTranslated(City.objects.all(), label = ugettext_lazy('City'), empty_label=None)
    region = ChoiceFieldTranslated(Region.objects.none(), label = ugettext_lazy('Region'),  empty_label = None, required=False)
        #City and region field types are "Choice Field Translated", which is a newly defined type extending Model Choice Field,
        #basically used to obtain the choices in arabic or english, based on current language chosen by user.

    mobile_number = forms.RegexField(label = ugettext_lazy('Mobile Number'), regex=r'^01[0-9]{9}$') 
        # Matches phone numbers that start with 01 and have another 9 digits, 11 digits in total.
    special_notes = forms.CharField(label = ugettext_lazy('Special Notes'), max_length = 1024, required= False)
    agree_to_terms = forms.BooleanField(label = ugettext_lazy('Agree to Terms and Conditions'), 
        error_messages={'required': 'You must accept the terms and conditions'}, widget=forms.CheckboxInput(attrs={'class' : 'regular-checkbox'}))
    
    #other_phone_number = forms.RegexField(regex=r'^[\+\- 0-9]{0,20}$',required=False) #To allow international numbers
    

    def __init__(self, *args, **kwargs):
        #This is done to prepopulate the regions of the first city.. Later repopulation is done using json, check city_to_region + filter_location.js
        forms.Form.__init__(self, *args, **kwargs)
        parents=City.objects.all()
        if len(parents) > 0: #Maybe there should be a different action if the number of city is equal zero? Raise error, notify admin?
            self.fields['city'].initial=parents[0].pk

        parent_id=self.fields['city'].initial or self.initial.get('city') \
                  or self._raw_value('city')
        if parent_id:
            children=Region.objects.filter(city__id=parent_id)
            self.fields['region'].queryset=children
            if len(children) > 0: #Maybe there should be a different action if the number of region is equal zero?
                self.fields['region'].initial=children[0].pk

    def save(self, product_id, user_id):
        try:
            quantity = self.cleaned_data['quantity']
            payment_choice = self.cleaned_data['payment_choice']
            buyer = UserProfile.objects.get(id=user_id)
            product = Product.objects.get(id=product_id)
            seller = product.user #Seller is obtained from the product.
            city = self.cleaned_data['city']
            region = self.cleaned_data['region']
            address = self.cleaned_data['address']
            mobile_number = self.cleaned_data['mobile_number']
            special_notes = self.cleaned_data['special_notes']
            price = product.price * quantity

            order = Order.objects.create(
                quantity = quantity,
                price = price,
                payment_choice = payment_choice,
                seller = seller,
                product = product,
                buyer=buyer,
                mobile_number=mobile_number,
                address = address,
                city = city,
                region = region,
                special_notes = special_notes)
            order.save()

            # Email sent to product owner, & also to orders@shoghlanah.com
            subject = "An order has been made on one of your products!"
            to = [seller.email, 'orders@shoghlanah.com']
            from_email = settings.EMAIL_HOST_USER
            msg = 'ordered your product!'
            dic = {}
            dic['order'] = order
            email_html(subject=subject, from_email=from_email, to=to, msg=msg, dic=dic)

            return HttpResponse("Created Successfully!")
        except ObjectDoesNotExist:
            return HttpResponse("Hacker!")
