import time
import datetime

from django.http import HttpRequest
def set_useragent_on_request_middleware(get_response):
    print("Initial call") # Здесь происходит вызов только при старте приложения
    def middleware(request: HttpRequest): # Принимает запрос до того как его обработает вью функция
        print("before get response")
        #request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)
        print("after get response")
        return response
    return middleware

class CountRequestMiddleware: # Подсчет запросов
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_count = 0
        self.response_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest): # Это то что будет вызвано когда middleware будет обрабатывать запросы
        self.request_count += 1
        print("request_count", self.request_count)
        response = self.get_response(request) # Обрабатываем запрос
        self.response_count += 1
        print("response_count", self.response_count)
        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print("got", self.exceptions_count, "exceptions so far")
        #request.META.get()

class ThrottlingMiddleware:
    """ Класс выдает ошибку при частых запросах от пользователя """
    def __init__(self, get_response):
        self.get_response = get_response
        self.user_dict = {}

    def timing(self):
        new_time = time.time()
        return new_time

    def __call__(self, request: HttpRequest):
        user_ip = request.META.get("REMOTE_ADDR", None)
        if user_ip not in self.user_dict:
            self.user_dict[user_ip] = self.timing()
        else:
            if (self.timing() - self.user_dict[user_ip]) > 5:
                self.user_dict[user_ip] = self.timing()
                raise RuntimeError
        response = self.get_response(request)
        return response