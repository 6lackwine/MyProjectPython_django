from django import forms
from django.forms import ModelForm

from blogapp.models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = "title", "author", "category", "tags", "content"