from django.views.generic import ListView

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.forms import UserCreationForm

from .forms import ProfileForm
from .models import Profile
from django.views import View


class AboutMeView(TemplateView):
    model = Profile
    template_name = "myauth/about-me.html"
    #fields = "user", "bio", "avatar"
    queryset = Profile.objects.all()
    context_object_name = "profiles"

class UserProfile(TemplateView):
    model = Profile
    template_name = "myauth/about-me.html"
    #fields = "user", "bio", "avatar"
    queryset = Profile.objects.all()
    context_object_name = "profiles"


class UpdateProfile(UpdateView):
    model = Profile
    template_name = "myauth/profile_update_form.html"
    fields = "user", "bio", "avatar"

    def get_success_url(self):
        return reverse("myauth:update", kwargs={"pk": self.object.pk})

    def user_is_staff(self):
        return (self.request.user.is_staff or self.request.user.pk == self.get_object().user.pk)

class UserList(ListView):
    model = Profile
    template_name = "myauth/user-list.html"
    fields = ["avatar"]
    context_object_name = "profile"
    queryset = Profile.objects.all()


class RegisterView(CreateView):  # Класс для регистрации пользователя
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self,
                   form):  # Производит аутентификацию пользователя (обработка происходит когда форма была опубликована успешно
        response = super().form_valid(form)  # Подготовка ответа. В таком случае пользователь уже сохранен
        Profile.objects.create(user=self.object)
        # Теперь делаем аутентификацию пользователя
        # Вытаскиваем данные из формы, которые были только что опубликованы:
        username = form.cleaned_data.get("username")  # clean_data - это очищенные данные
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password
        )
        login(request=self.request, user=user)  # Выполняем вход пользователя
        return response  # Возвращаем ответ


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticate:
            return redirect("/admin/")
        return render(request, "myauth/login.html")

    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("/admin/")
    return render(request, "myauth/login.html", {"error": "Invalid login credentials"})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)  # Выход пользователя
    return redirect(reverse("myauth:login"))  # переадресация пользователя после выхода


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")


def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)  # max_age - длительность существования в секундах
    return response


def get_cookie_view(request: HttpRequest) -> HttpResponse:  # Функция для отображения cookie
    value = request.COOKIES.get("fizz", "default_value")
    return HttpResponse(f"Cookie value: {value!r}")


@permission_required("myauth.view_profile", raise_exception=True)  # Проверяет есть ли данное разрешение у пользователя
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")  # Получаем значение из сессии
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'foo': 'bar', 'spam': 'eggs'})
