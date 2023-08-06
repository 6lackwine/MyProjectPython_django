from django.contrib import admin
from .models import Product, Order, ProductImage
from django.http import HttpRequest
from django.db.models import QuerySet

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
    inlines = [
        ProductInline,
    ]
    list_display = "delivery_address", "promocode", "created_at", "user_verbose"

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username
