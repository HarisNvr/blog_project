from django.http import Http404
from django.shortcuts import render
from blog.models import Post
from django.utils import timezone

app_name = 'blog'


def index(request):
    template = 'blog/index.html'
    posts = Post.objects.all().filter(
        category__is_published=True,
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')[:5]
    context = {'post_list': posts}
    return render(request, template, context)


def detail(request, post_id):
    template = 'blog/detail.html'
    posts_by_id = {post['id']: post for post in posts}
    try:
        post = posts_by_id[post_id]
    except KeyError:
        raise Http404('Пост не найден')
    context = {'post': post}
    return render(request, template, context)


def category(request, category_slug):
    template = 'blog/category.html'
    context = {'post_list': posts,
               'category_slug': category_slug}
    return render(request, template, context)
