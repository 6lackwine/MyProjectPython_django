from django.urls import path

from blogapp.views import ArticlesListView

app_name = "blogapp"

urlpatterns = [
    path("article_list/", ArticlesListView.as_view(), name="article_list"),
]