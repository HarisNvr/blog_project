from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Commentary, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'location', 'category', 'image', 'pub_date']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CommentaryForm(forms.ModelForm):
    class Meta:
        model = Commentary
        fields = ('text',)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
