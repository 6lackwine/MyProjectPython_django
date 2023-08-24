from io import TextIOWrapper
from csv import DictReader

from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path

from .models import Product, Order, ProductImage
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet
from .forms import CSVImportForm

from .admin_mixins import ExportCSVMixin



class ProductInline(admin.StackedInline):
    model = ProductImage

class OrderInline(admin.TabularInline):
    model = Product.orders.through

@admin.action(description="Archive products") # Указываем что данная функция является Action
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet): # queryset запрос в котором содержатся те сущности которые выбраны
    queryset.update(archived=True) # Действие которое выполнит архивацию продуктов

@admin.action(description="Unarchive products")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportCSVMixin):
    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv", # Указываем имя действия
    ]
    inlines = [
        OrderInline,
        ProductInline,
    ]
    list_display = "pk", "name", "description_short", "price", "discount", "archived"
    list_display_links = "pk", "name"
    ordering = "-name", "pk"
    search_fields = "name", "description", "price", "discount"
    fieldsets = [
        (None, {
            "fields": ("name", "description")
        }),
        ("Price options", {
            "fields": ("price", "discount"),
            #"classes": ("collapse", "wide"),
        }),
        ("Images", {
            "fields": ("preview",),
        }),
        ("Extra_options", {
            "fields": ("archived", ),
            "classes": ("collapse", ),
            "description": "Extra options. File 'archived' is for soft delete",
        })
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."

#admin.site.register(Product, ProductAdmin)

#class ProductInline(admin.TabularInline):
class ProductInline(admin.StackedInline):
    model = Order.products.through

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "shopapp/orders_changelist.html"
    inlines = [
        ProductInline,
    ]
    list_display = "delivery_address", "promocode", "created_at", "user_verbose"

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm # Готовим форму
            context ={
                "form": form,
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)
        csv_file = TextIOWrapper( # Получаем из байт строчки
            form.files["csv_form"].file,
            encoding=request.encoding,
        )
        reader = DictReader(csv_file)

        orders = [
            Order(**row)
            for row in reader
        ]
        Order.objects.bulk_create(orders)
        self.message_user(request, "Data from CSV was imported")
        return redirect("..")


    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("import-orders-csv/", self.import_csv, name="import_orders_csv"),
        ]
        return new_urls + urls
