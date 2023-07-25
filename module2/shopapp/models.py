from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    class Meta:
        ordering = ["name", "price"]
    name = models.CharField(max_length=100)
    description = models.TextField(null=False, blank=True) # Описание продукта
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, default=1, on_delete=models.PROTECT)

    #@property
    #def description_short(self) -> str:
    #    if len(self.description) < 48:
    #        return self.description
    #    return self.description[:48] + "..."

    def __str__(self) -> str:
        return f"{self.name!r}"

class Order(models.Model):
    class Meta:
        ordering = ["delivery_address", "user"]
    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name="orders")