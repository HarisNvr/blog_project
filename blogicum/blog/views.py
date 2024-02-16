from django.shortcuts import render, get_object_or_404
from .models import Category, Post
from django.http import Http404
from django.utils import timezone

app_name = 'blog'


def index(request):
    posts = Post.objects.all(
    ).filter(
        category__is_published=True,
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by(
        '-pub_date'
    )[:5]
    template = 'blog/index.html'
    context = {'post_list': posts}
    return render(request, template, context)


def detail(request, post_id):
    post = Post.objects.all(
    ).filter(
        category__is_published=True,
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by(
        '-pub_date'
    )[post_id]
    template = 'blog/detail.html'
    try:
        post
    except Exception:
        raise Http404('Пост не найден')
    context = {'post': post}
    return render(request, template, context)


def category(request, category_slug):
    category_obj = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = category_obj.post_set.filter(
        is_published=True,
        pub_date__lte=timezone.now()).order_by('-pub_date')

    template = 'blog/category.html'
    context = {'post_list': posts,
               'category': category_obj}
    return render(request, template, context)
