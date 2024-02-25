from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView

from .forms import UserProfileForm, CommentaryForm, PostForm
from .models import Category, Post, Commentary


def base_request():
    return Post.objects.select_related(
        'category',
        'author',
        'location'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = base_request().filter(author=user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'user': user, 'page_obj': page_obj}
    template = 'blog/profile.html'
    return render(request, template, context)


def homepage(request):
    paginator = Paginator(base_request(), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'blog/homepage.html'
    context = {'page_obj': page_obj}
    return render(request, template, context)


def detail(request, post_id):
    post = get_object_or_404(base_request(), pk=post_id)
    form = CommentaryForm(request.POST, instance=post)
    comment = Commentary.objects.select_related('author')
    template = 'blog/detail.html'
    context = {'post': post, 'form': form, 'comment': comment}
    return render(request, template, context)


def category(request, category_slug):
    category_obj = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)
    posts = base_request().filter(category=category_obj)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'blog/category.html'
    context = {'page_obj': page_obj, 'category': category_obj}
    return render(request, template, context)


def posting(request, pk=None):
    instance = None
    if pk is not None:
        instance = get_object_or_404(Post, pk=pk)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            post_detail_url = reverse_lazy('blog:post_detail', args=[post.pk])
            return redirect(post_detail_url)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


def delete_post(request, pk):
    instance = get_object_or_404(Post, pk=pk)
    form = PostForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:homepage')
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(base_request(), pk=post_id)
    form = CommentaryForm(request.POST)
    if form.is_valid():
        print('1')
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


class CommentaryDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentaryForm()
        context['commentary'] = (
            self.object.commentary.select_related('author')
        )
        return context


@login_required
def edit_profile(request, username):
    user = get_object_or_404(User, username=username)

    if request.user != user:
        return redirect('blog:homepage')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=username)
    else:
        form = UserProfileForm(instance=user)

    context = {
        'form': form,
        'user': user
    }
    template = 'blog/user.html'
    return render(request, template, context)
