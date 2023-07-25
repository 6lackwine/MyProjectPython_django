from timeit import default_timer

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.contrib.auth.models import Group, User
from .forms import ProductForm, OrderForm

from .models import Product
from .models import Order

from django.views import View
from .forms import GroupForm
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
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

class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related("permissions").all(),
        }
        return render(request, "shopapp/groups-list.html", context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)

class ProductDetailsView(DetailView): # Класс для отображения деталей товара
    template_name = "shopapp/products-details.html"
    model = Product
    context_object_name = "product"

class ProductListView(ListView): # Адресовка шаблона отдельно делается в родительском классе
    template_name = "shopapp/products-list.html" # Теперь отдельно указан шаблон
    #model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)

class ProductCreateView(PermissionRequiredMixin, CreateView):
    #def test_func(self): # если пользователь не суперюзер, то ему не будет доступ к созданию заказа
        #return self.request.user.is_superuser # проверка на суперюзера
    permission_required = "shopapp.add_product"
    model = Product # Какой продукт создавать
    fields = "name", "price", "description", "discount" # Какие поля запрашивать
    success_url = reverse_lazy("shopapp:products_list") # Ссылка куда нужно вернуться после успешного создания продукта
    # reverse_lazy вычисляет значение только когда идет обращение именно к этому объекту
    def form_valid(self, form):
        product = form.save(commit=False)
        product.created_by = self.request.user
        product.save()
        return super().form_valid(form)


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list") # Вернется на эту страницу после удаления

    def form_valid(self, form): # При удалении товар остается в списке, но archived становится True
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)

class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    fields = "name", "price", "description", "discount"
    template_name_suffix = "_update_form"
    def test_func(self):
        is_super_user = self.request.user.is_superuser
        return is_super_user or (self.request.user.has_perm("shopapp.change_product") and
                                 self.request.user.id == self.get_object().created_by.id)


    def get_success_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.object.pk}) # Генерируем ссылку, для datails нужно указать pk, pk нужно передать через kwargs. Kwargs это те параметры url которые мы можем предзаполнить. Нужно указать, что pk ссылается на self.object.pk. На self.object доступен объект обновление которого сейчас идет, то есть объект был обновлен он доступен по self.object
#def create_product(request: HttpRequest) -> HttpResponse:
#    if request.method == "POST":
#        form = ProductForm(request.POST) # Форма которая предзаполнена данными из POST запроса
#        if form.is_valid(): # Проверка на валидность формы
            ##name = form.cleaned_data["name"] # Получение данных из формы
            ##price = form.cleaned_data["price"]
            ##description = form.cleaned_data["description"]
            ##Product.objects.create(**form.cleaned_data) # Распаковка словаря
#            form.save() # Если форма валидна, то можно просто сохранить эту форму
#            url = reverse("shopapp:products_list") # Перенаправляет в список продуктов после заполнения формы
#            return redirect(url)
#    else:
#        form = ProductForm()
#    context = {
#        "form": form,
#    }
#    return render(request, "shopapp/create-product.html", context=context)

class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects.select_related("user").prefetch_related("products")
    )

class OrdersDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "view_order"
    #queryset = (
    #    Order.objects.select_related("user").prefetch_related("products")
    #)
    template_name = "shopapp/order_details.html"
    model = Order
    context_object_name = "order"

class OrderCreateView(CreateView):
    model = Order
    fields = "user", "products",
    success_url = reverse_lazy("shopapp:orders_list")

class OrderUpdateView(UpdateView):
    model = Order
    fields = "user", "products"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("shopapp:order_details", kwargs={"pk": self.object.pk})

class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


    #def create_order(request: HttpRequest) -> HttpResponse:
#    if request.method == "POST":
#        form = OrderForm(request.POST)
#        if form.is_valid():
#            form.save()
#            url = reverse("shopapp:orders_list")
#            return redirect(url)
#    else:
#        form = OrderForm()
#    context = {
#        "form": form
#    }
#    return render(request, "shopapp/order_form.html", context=context)