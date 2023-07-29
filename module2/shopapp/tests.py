from django.contrib.auth.models import User, Permission
from django.test import TestCase, TransactionTestCase

from shopapp.models import Product
from shopapp.utils import add_two_numbers
from django.urls import reverse
from django.test import Client

class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)

class ProductCreateViewTestCase(TestCase):
    #def setUp(self):
    #   self.user = User.objects.create_user(username="usertest", password="123", email="admin@admin.com")
    #    self.client = Client()

    #def test_product_create(self):
    #    self.client.login(username="usertest", password="123", email="admin@admin.com")
    #    response = self.client.post(reverse("shopapp:product_create"),
     #                               {
     #                                   "name": "Table",
     #                                  "description": "A good table",
      #                                  "discount": "10",
       #                             }
        #                            )
        #self.assertRedirects(response, reverse("shopapp:products_list"))

    @classmethod
    def setUpClass(cls):
        permission = Permission.objects.get(name="Can change product")
        cls.user = User.objects.create_user(username="admin", password="123")
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_product_create(self):
        response = self.client.post(reverse("shopapp:product_create"),
                                       {
                                            "name": "Table",
                                            "description": "A good table",
                                            "discount": "10",
                                     }
                                    )
        self.assertRedirects(response, reverse("shopapp:products_list"))

