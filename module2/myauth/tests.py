import json
from django.test import TestCase
from django.urls import reverse

class GetCookieViewTestCase(TestCase):
    def test_get_cookie_view(self):
        response = self.client.get(reverse("myauth:cookie-get")) # Ответ
        self.assertContains(response, "Cookie value") # Проверяем содержится ли в ответе Cookie value

class FooBarViewTestCase(TestCase):
    def test_foo_bar_view(self):
        response = self.client.get(reverse("myauth:foo-bar"))
        self.assertEqual(response.status_code, 200) # Проверяем статус кода
        self.assertEqual(response.headers["content-type"], "application/json") # Проверяем заголовки
        expected_data = {'foo': 'bar', 'spam': 'eggs'} # Проверим что ожидаемый результат и полученный равны
        #received_data = json.loads(response.content) # Приведем содержимое к словарю
        #self.assertEqual(received_data, expected_data) # Сравним полученный результат с ожидаемым. response.content - содержимое
        self.assertJSONEqual(response.content, expected_data) # Вместо 2 последних строчек кода
