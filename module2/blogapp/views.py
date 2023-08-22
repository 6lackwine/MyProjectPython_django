from django.shortcuts import render
from django.views.generic import ListView, CreateView

from blogapp.models import Article


class ArticlesListView(ListView):
    template_name = 'blogapp/article_list.html'
    context_object_name = 'articles'
    queryset = (
        Article.objects.select_related("author").prefetch_related("category", "tags").defer("content")
    )
    #fields = "title", "author", "category", "tags", "content"