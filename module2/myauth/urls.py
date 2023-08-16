from django.urls import path
from django.contrib.auth.views import LoginView
from .views import get_cookie_view, \
    set_cookie_view, \
    set_session_view, \
    get_session_view, \
    logout_view, \
    MyLogoutView, \
    AboutMeView, \
    RegisterView, \
    FooBarView, UpdateProfile, UserList, UserProfile

app_name = "myauth"

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(
            template_name="myauth/login.html",
            redirect_authenticated_user = True, # Если юзер уже прошел аутентификацию, то ему не нужно ее проходить снова и его направят на нужный адрес

        ),
        name="login"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("user-profile/<int:pk>/", UserProfile.as_view(), name="user-profile"),
    path("about-me/<int:pk>/update/", UpdateProfile.as_view(), name="update"),
    path("user-list/", UserList.as_view(), name="user-list"),
    path("register/", RegisterView.as_view(), name="register"),

    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("cookie/set/", set_cookie_view, name="cookie-get"),

    path("session/get/", get_session_view, name="session-get"),
    path("session/set/", set_session_view, name="session-set"),

    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),
]