import logging
from timeit import default_timer

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.syndication.views import Feed
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse, Http404
from django.contrib.auth.models import Group, User

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.request import Request
from rest_framework.response import Response

from .forms import ProductForm, OrderForm

from .models import Product, ProductImage
from .models import Order

from django.views import View
from .forms import GroupForm
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .serializers import ProductSerializers, OrderSerializers
from django.core.cache import cache

log = logging.getLogger(__name__)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "discount",
        "description",
        "archived",
        "price",
    ]
    ordering_fields = [
        "name",
        "price"
    ]

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializers
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_fields = [
        "user",
        "products",
        "delivery_address",
        "created_at",
    ]
    ordering_fields = [
        "user",
        "products",
        "delivery_address",
        "created_at",
    ]

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
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")
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
    #model = Product
    queryset = Product.objects.prefetch_related("images") # prefetch_related указывает связь один ко многим
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
    fields = "name", "price", "description", "discount", "preview" # Какие поля запрашивать
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
    #fields = "name", "price", "description", "discount", "preview"
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def form_valid(self, form):
       response = super().form_valid(form)
       for image in form.files.getlist("images"):
           ProductImage.objects.create(
                product=self.object,
                image=image)
       return response

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
    permission_required = "shopapp.view_order"
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

class OrderExport(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        order_data = [{
            "pk": order.pk,
            "delivery_address": order.delivery_address,
            "promocode": order.promocode,
            "user": order.user_id,
            "products": [
                {
                    "pk": product.pk,
                }
                    for product in order.products.all()
            ]
        }
                for order in orders
            ]
        # elem = order_data[0]
        # name = elem["user"]
        # print(name)
        return JsonResponse({"order": order_data})

class LatestProductsFeed(Feed):
    title = "Products"
    description = "Product Description"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        # created_at__isnull=False нужен чтобы пользователи не видели продукты которые еще не опубликованы
        return (Product.objects.filter(created_at__isnull=False).order_by("-created_at"))[:5]

    def item_name(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]

class UserOrdersListView(UserPassesTestMixin, ListView):
    template_name = "shopapp/user_orders.html"
    model = Order
    context_object_name = "user_orders"
    #queryset = Order.objects.all()

    def test_func(self):
        return self.request.user.is_authenticated
    def get_queryset(self):
        self.owner = User.objects.get(pk=self.kwargs["user_id"])
        get_object_or_404(User, username=self.owner, pk=self.request.user.pk)
        return Order.objects.filter(user=self.owner)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner"] = self.owner
        return context

# class UserOrdersDataExportJSON(View):
#     def get(self, request: HttpRequest, user_id) -> JsonResponse:
#         cache_key = "orders_data_export"
#         orders_data = cache.get(cache_key) # получаем и сохраняем данные из кэша
#         user = get_object_or_404(User, pk=user_id)
#         if orders_data is None:
#             orders = Order.objects.order_by("pk").filter(user=user)
#             orders_data = [{
#                 "pk": order.pk,
#                 "delivery_address": order.delivery_address,
#                 "promocode": order.promocode,
#                 "user": order.user.pk,
#                 "products": [
#                     {
#                         "pk": product.pk,
#                     }
#                         for product in order.products.all()
#                 ]
#             }
#                     for order in orders
#                 ]
#             cache.set(cache_key, orders_data, 5) # добавляем данные в кэш
#         return JsonResponse({"order": orders_data})

class UserOrdersDataExportJSON(APIView):
    def get(self, request: HttpRequest, user_id) -> JsonResponse:
        cache_key = f"orders_data_export_user_{user_id}"
        orders_data = cache.get(cache_key) # получаем и сохраняем данные из кэша
        user = get_object_or_404(User, pk=user_id)
        if orders_data is None:
            orders = Order.objects.order_by("pk").filter(user=user)
            serialized = OrderSerializers(orders, many=True)
            cache.set(cache_key, serialized.data, 120) # добавляем данные в кэш
        return JsonResponse({"order": orders_data})