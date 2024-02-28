from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import UserProfileForm, CommentaryForm, PostForm
from .models import Category, Post, Commentary


POSTS_PER_PAGE = 10


def base_request(author_id=None, category_name=None, comment_count=False,
                 filtration=False):
    request = Post.objects.select_related(
        'category',
        'author',
        'location').order_by('-pub_date')
    if filtration:
        request = request.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    if author_id:
        request = request.filter(author_id=author_id)
    if category_name:
        request = request.filter(category=category_name)
    if comment_count:
        request = request.annotate(comment_count=Count('commentaries'))
    return request


def post_paginator(request, context_posts):
    paginator = Paginator(context_posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def profile_view(request, username):
    profile = get_object_or_404(User, username=username)
    user = request.user
    filtration = profile != user
    context_posts = base_request(author_id=profile.pk,
                                 comment_count=True,
                                 filtration=filtration)
    page_obj = post_paginator(request, context_posts)
    context = {'user': user,
               'page_obj': page_obj,
               'profile': profile}
    template = 'blog/profile.html'
    return render(request, template, context)


@login_required
def edit_profile(request):
    username = request.user
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return redirect('blog:homepage')
    form = UserProfileForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=username)
    context = {
        'form': form,
        'user': user
    }
    template = 'blog/user.html'
    return render(request, template, context)


def homepage(request):
    page_obj = post_paginator(request, base_request(comment_count=True,
                                                    filtration=True))
    template = 'blog/homepage.html'
    context = {'page_obj': page_obj}
    return render(request, template, context)


def get_post_details(post_id):
    post = get_object_or_404(
        Post,
        pk=post_id
    )
    form = CommentaryForm()
    comments = post.commentaries.all().select_related(
        'author'
    ).order_by(
        'created_at'
    )
    return post, form, comments


def detail(request, post_id):
    post, form, comments = get_post_details(post_id)
    if ((post.is_published and post.category.is_published and
         post.pub_date <= timezone.now()) or post.author == request.user):
        template = 'blog/detail.html'
        context = {'post': post, 'form': form, 'comments': comments}
        return render(request, template, context)
    else:
        raise Http404


def category(request, category_slug):
    category_obj = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)
    context_posts = base_request(category_name=category_obj,
                                 filtration=True)
    page_obj = post_paginator(request, context_posts)
    template = 'blog/category.html'
    context = {'page_obj': page_obj, 'category': category_obj}
    return render(request, template, context)


@login_required
def create_post(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author and request.user.is_authenticated:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    instance = get_object_or_404(Post, pk=post_id)
    form = PostForm(instance=instance)
    context = {'form': form}
    if (request.method == 'POST'
            and request.user == instance.author):
        instance.delete()
        return redirect('blog:homepage')
    return render(request, 'blog/create.html', context)


@login_required
def create_comment(request, post_id):
    post = get_object_or_404(base_request(filtration=True), pk=post_id)
    form = CommentaryForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        post.save()
        return redirect('blog:post_detail', post_id=post_id)
    context = {'form': form}
    return render(request, 'blog/comment.html', context)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Commentary, id=comment_id,
                                author=request.user.id)
    form = CommentaryForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    context = {'form': form, 'comment': comment}
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(base_request(filtration=True), pk=post_id)
    comment = get_object_or_404(Commentary, id=comment_id,
                                author=request.user.id)
    if comment.author != request.user:
        raise Http404
    if request.method == 'POST':
        comment.delete()
        post.save()
        return redirect('blog:post_detail', post_id=post_id)
    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)
