from string import ascii_letters

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User, Permission
from django.test import TestCase, TransactionTestCase

from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers
from django.urls import reverse, reverse_lazy
from django.test import Client
from random import choices

class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)

#class ProductCreateViewTestCase(TestCase):
    #@classmethod
    #def setUpClass(cls):
    #    super().setUpClass()
    #    cls.user = User.objects.create_user(username="testname")
    #    cls.user.set_password("some_password")
    #   view_order_perm = Permission.objects.get(codename='view_order')
    #    cls.user.user_permissions.add(view_order_perm)
    #    cls.user.save()

    #@classmethod
    #def tearDownClass(cls):
     #   super().tearDownClass()
      #  cls.user.delete()

    #def setUp(self) -> None:
     #   self.client.force_login(self.user)
      #  self.product_name = "".join(choices(ascii_letters, k=10))
       # Product.objects.filter(name=self.product_name).delete()

    #def test_product_create(self):
    #    response = self.client.post(
    #        reverse("shopapp:product_create"),
    #        {
    #            "name": "Table",
    #            "description": "A good table",
    #            "discount": "10",
    #        }
    #    )
     #   self.assertRedirects(response, reverse("shopapp:products_list"))
      #  self.assertEqual(response.status_code, 302, "Ошибка при получении страницы с описанием заказа!")
       # self.assertTrue(Product.objects.filter(name=self.product_name)).exists()

class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создадим юзера
        cls.user = User.objects.create_user(
            username='test',
            password="test"
        )
        # получим разрешение
        view_order_perm = Permission.objects.get(
            codename='view_order'
        )
        print("finded permissions:", view_order_perm)
        # выдадим разрешение юзеру
        cls.user.user_permissions.add(view_order_perm)
        print("user permissions:", cls.user.user_permissions)
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # удалим заказ
        # очистим таблицу товаров
        for product in Product.objects.all():
            product.delete()
        # удалим юзера
        cls.user.delete()

    def setUp(self) -> None:
        # выполним вход пользователя
        self.client.force_login(self.user)
        print("user permissions:", self.user.user_permissions)
        # создадим заказ
        self.order = Order.objects.create(
            delivery_address="test address",
            promocode="test promocode",
            user=self.user,
        )
        self.order.save()
        # создадим товар
        product = Product.objects.create(
            name='test product',
            price=123.23,
        )
        # добавим товар в заказ
        self.order.products.add(product)

    def tearDown(self) -> None:
        # удалим заказ
        self.order.delete()

    def test_order_details_view(self):
        # получим страницу с описанием заказа
        response = self.client.get(
            reverse("shopapp:order_details", kwargs={"pk": self.order.pk})
        )
        if self.user.is_authenticated:
            print("YES is_authenticated")
        else:
            print("NO is_authenticated")
        # проверка, что страница получена
        self.assertEqual(response.status_code, 200, "Ошибка при получении страницы с описанием заказа!")
        # проверим совпадение адреса доставки
        # если не указывать поля, в которые передаются данные, тест падает
        self.assertContains(
             response,
             self.order.delivery_address,
             msg_prefix="Адрес доставки!"
         )
        print(response)
        order = response.context["order"]
        self.assertContains(
             response=response,
             text=self.order.delivery_address,
             msg_prefix="Адрес доставки не совпадает или отсутствует!"
         )
        # проверим совпадение промокодов
        self.assertContains(
             response=response,
             text=self.order.promocode,
             msg_prefix="Промокод не совпадает или отсутствует!"
         )
        # проверим совпадение ПК заказа
        self.assertEqual(
            order.pk,
            self.order.pk,
            "ПК заказа не совпадает или отсутствует!"
        )
        # вот так проверка не проходит.
        #self.assertContains(response, self.order.delivery_address, "Отсутствует адрес доставки!")
