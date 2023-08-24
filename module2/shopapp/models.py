from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from django.utils.translation import gettext_lazy as _


def product_preview_directory_patch(instance: "Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )

class Product(models.Model):
    class Meta:
        ordering = ["name", "price"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    name = models.CharField(max_length=100)
    description = models.TextField(null=False, blank=True) # Описание продукта
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, default=1, on_delete=models.PROTECT)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_patch)

    def get_absolute_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.pk})


def product_image_directory_path(instance: "ProductImage", filename: str) -> str: # Будет генерироваться путь для картинок
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename,
    )

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images") # on_delete - означает, что если товар будет удален, то все картинки будут тоже удалены
    image = models.ImageField(upload_to=product_image_directory_path)
    description = models.CharField(null=False, max_length=200, blank=True)


    #@property
    #def description_short(self) -> str:
    #    if len(self.description) < 48:
    #        return self.description
    #    return self.description[:48] + "..."

    #def __str__(self) -> str:
    #    return f"{self.name!r}"

class Order(models.Model):
    class Meta:
        ordering = ["delivery_address", "user"]
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name="orders")
    receipt = models.FileField(null=True, upload_to="orders/receipts") # Сюда поле будет загружать чек после выполнения заказа