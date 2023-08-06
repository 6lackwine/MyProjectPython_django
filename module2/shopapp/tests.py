from django.contrib.auth.models import User, Permission
from django.test import TestCase, TransactionTestCase

from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers
from django.urls import reverse
import json

class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)

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
        # выдадим разрешение юзеру
        cls.user.user_permissions.add(view_order_perm)

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
        # проверка, что страница получена
        self.assertEqual(response.status_code, 200, "Ошибка при получении страницы с описанием заказа!")
        # проверим совпадение адреса доставки
        # если не указывать поля, в которые передаются данные, тест падает
        self.assertContains(
             response,
             self.order.delivery_address,
             msg_prefix="Адрес доставки!"
         )
        order = response.context["order"]
        self.assertContains(
             response,
             self.order.delivery_address,
             msg_prefix="Адрес доставки не совпадает или отсутствует!"
         )
        # проверим совпадение промокодов
        self.assertContains(
             response,
             self.order.promocode,
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

class OrdersExportTestCase(TestCase):
    fixtures = [
        "user-fixture.json",
        "products-fixture.json",
        "order-fixture.json",
    ]
    @classmethod
    def setUpClass(cls):
        super(OrdersExportTestCase, cls).setUpClass()
        cls.user = User.objects.create_user(
            username='super',
            password='super',
        )
        cls.user.is_staff = True
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_export(self):
        response = self.client.get(reverse("shopapp:order_export"))
        orders = Order.objects.order_by("pk").all()
        expected_data = [{
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
        order_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(order_data["order"], expected_data)
