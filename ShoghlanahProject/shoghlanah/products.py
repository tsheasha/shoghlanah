from shoghlanah.models import *
from django import forms
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, Http404
from shoghlanah.orders import OrderForm
from django.utils.encoding import smart_str
from json import dumps

def stores_home(request):
    products = Product.objects.all()
    stores = Store.objects.filter(featured= True)
    return render_to_response("stores_home.html", {'products':products, 'stores':stores}, RequestContext(request))

def block(request):
    return render_to_response("shop/product/block.html", RequestContext(request))
    
def index(request, user_id):
    products = Product.objects.filter(user__id=user_id)
    return render_to_response("shop/product/index.html", {'products': products}, RequestContext(request))


@login_required
def create(request):
    if request.method == 'POST':
        productForm = ProductForm(data=request.POST)
        productForm.is_valid()
        return productForm.save(request.user.id)
    else:
        createProductForm = ProductForm()
        return render_to_response("shop/product/create.html", {'form': createProductForm}, RequestContext(request))


@login_required
def update(request, product_id):
    if request.method == 'POST':
        productForm = ProductForm(data=request.POST)
        if productForm.is_valid():
            return productForm.update_save(product_id)
        else:
            return HttpResponse("fix errors first")
    else:
        try:
            product = Product.objects.get(pk=product_id)
            if product.user.id == request.user.id:
                editProductForm = ProductForm({'title': product.title, 'description': product.description, 'price': product.price})
                return render_to_response("shop/product/create.html", {'form': editProductForm, 'product': product}, RequestContext(request))
        except Product.DoesNotExist:
            return HttpResponse("product not found")


@login_required
def delete(request, product_id):
    try:
        user = UserProfile.objects.get(pk=request.user.id)
        product = Product.objects.get(pk=product_id)
        if product.user is user:
            product.delete()
            return HttpResponse("product deleted")
        else:
            return HttpResponse("product not deleted (current user is not the owner")
    except Product.DoesNotExist:
        return HttpResponse("product not found")

def open(request, product_id):
    product = Product.objects.get(pk=product_id)
    return render_to_response("shop/product/view.html", {'product': product}, RequestContext(request))


def filter (request, model_class, field_name):
    try:
        kwargs = {smart_str(field_name): request.GET['q']}
    except KeyError:
        raise Http404
    qs = model_class.objects.filter(**kwargs).values('pk', 'name')
    response = HttpResponse(
        content=dumps(list(qs)),
        mimetype='application/json'
    )
    return response


class ProductForm(forms.Form):
    # TODO: Define form fields here
    title = forms.CharField(max_length=32)
    description = forms.CharField(max_length=265, widget=forms.Textarea)
    price = forms.IntegerField()
    user = None

    def update_save(self, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            product.title = self.cleaned_data['title']
            product.description = self.cleaned_data['description']
            product.price = self.cleaned_data['price']
            product.save()
            return HttpResponse("product updated")
        except Product.DoesNotExist:
            return HttpResponse("product not found")
        except IntegrityError:
            return HttpResponse("this user has created a product with the same title before")

    def save(self, user_id):
        self.user = UserProfile.objects.get(id=user_id)
        try:
            product = Product.objects.create(user=self.user, title=self.cleaned_data['title'])
            product.description = self.cleaned_data['description']
            product.price = self.cleaned_data['price']
            product.save()
            return HttpResponse("Product created successfuly")
        except IntegrityError:
            return HttpResponse("this user has created a product with the same title before")


