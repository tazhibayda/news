from django import forms
from .models import *


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'image','genres']
    image = forms.FileField(required=False)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'content': forms.Textarea(),
        }

