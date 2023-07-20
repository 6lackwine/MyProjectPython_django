from timeit import default_timer
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.models import Group
from .forms import ProductForm, OrderForm

from .models import Product
from.models import Order

def shop_index(request: HttpRequest):
    products = [
        ("Laptop", 1999),
        ("Desktop", 2999),
        ("Smartphone", 999),
    ]
    context = {
        "time_running": default_timer(),
        "products": products,
    }
    return render(request, "shopapp/shop-index.html", context=context)

def groups_list(request: HttpRequest):
    context = {
        "groups": Group.objects.prefetch_related("permissions").all(),
    }
    return render(request, "shopapp/groups-list.html", context=context)

def products_list(request: HttpRequest):
    context = {
        "products": Product.objects.all(),
    }
    return render(request, "shopapp/products-list.html", context=context)

def create_product(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProductForm(request.POST) # Форма которая предзаполнена данными из POST запроса
        if form.is_valid(): # Проверка на валидность формы
            #name = form.cleaned_data["name"] # Получение данных из формы
            #price = form.cleaned_data["price"]
            #description = form.cleaned_data["description"]
            #Product.objects.create(**form.cleaned_data) # Распаковка словаря
            form.save() # Если форма валидна, то можно просто сохранить эту форму
            url = reverse("shopapp:products_list") # Перенаправляет в список продуктов после заполнения формы
            return redirect(url)
    else:
        form = ProductForm()
    context = {
        "form": form,
    }
    return render(request, "shopapp/create-product.html", context=context)

def orders_list(request: HttpRequest):
    context = {
        "orders": Order.objects.select_related("user").prefetch_related("products").all(),
    }
    return render(request, "shopapp/orders-list.html", context=context)

def create_order(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            url = reverse("shopapp:orders_list")
            return redirect(url)
    else:
        form = OrderForm()
    context = {
        "form": form
    }
    return render(request, "shopapp/create-order.html", context=context)