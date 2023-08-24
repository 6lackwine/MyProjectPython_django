from django import forms
from django.core import validators
from shopapp.models import Product, Order
from django.forms import ModelForm
from django.contrib.auth.models import Group

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "discount", "description", "preview"
    images = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={"allow_multiple_selected": True}) # Позволяет загружать сразу несколько картинок
    )

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "user", "delivery_address", "products", "promocode"

class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ["name"]

class CSVImportForm(forms.Form):
    csv_form = forms.FileField()