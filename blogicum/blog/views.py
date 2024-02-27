from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404
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
    user_profile = get_object_or_404(User, username=username)
    user = request.user
    if user_profile == user:
        context_posts = Post.objects.select_related(
            'category',
            'author',
            'location'
        ).filter(
            author_id=user_profile.pk)
    else:
        context_posts = base_request().filter(author_id=user_profile.pk)
    paginator = Paginator(context_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'user': user,
               'page_obj': page_obj,
               'user_profile': user_profile}
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
    post = get_object_or_404(Post, pk=post_id)
    form = CommentaryForm()
    comments = (Commentary.objects.filter(post_id=post_id)
                .order_by('created_at'))
    template = 'blog/detail.html'
    context = {'post': post, 'form': form, 'comments': comments}
    return render(request, template, context)


def category(request, category_slug):
    category_obj = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)
    context_posts = base_request().filter(category=category_obj)
    paginator = Paginator(context_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'blog/category.html'
    context = {'page_obj': page_obj, 'category': category_obj}
    return render(request, template, context)


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            post_detail_url = reverse_lazy('blog:profile',
                                           args=[request.user.username])
            return redirect(post_detail_url)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, pk):
    instance = get_object_or_404(Post, pk=pk)
    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=pk)
    elif request.user is not request.user.is_authenticated:
        return redirect('login')
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            post_detail_url = reverse_lazy('blog:profile',
                                           args=[request.user.username])
            return redirect(post_detail_url)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, pk):
    instance = get_object_or_404(Post, pk=pk)
    form = PostForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:homepage')
    return render(request, 'blog/create.html', context)


@login_required
def manage_comment(request, post_id, comment_id=None):
    post = get_object_or_404(base_request(), pk=post_id)
    instance = None
    if comment_id is not None:
        instance = get_object_or_404(Commentary, id=comment_id)
    if request.method == 'POST':
        if '/delete_comment' in request.path:
            comment = get_object_or_404(Commentary, id=comment_id)
            if comment.author == request.user:
                comment.delete()
                post.comment_count -= 1
                post.save()
                return redirect('blog:post_detail', post_id=post_id)
            else:
                raise Http404
        else:
            if comment_id is not None:
                comment = get_object_or_404(Commentary, id=comment_id)
                if comment.author == request.user:
                    form = CommentaryForm(request.POST, instance=instance)
                else:
                    raise Http404
            else:
                form = CommentaryForm(request.POST, instance=instance)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.post = post
                comment.save()

                if comment_id is None:
                    post.comment_count += 1
                    post.save()

                post_detail_url = reverse_lazy('blog:post_detail',
                                               args=[post_id])
                return redirect(post_detail_url)
    else:
        if comment_id is not None:
            comment = get_object_or_404(Commentary, id=comment_id)
            if comment.author == request.user:
                form = CommentaryForm(instance=instance)
            else:
                raise Http404
        else:
            form = CommentaryForm(instance=instance)
    context = {'form': form, 'comment': instance} if (
            '/delete_comment' not in request.path) else {'comment': instance}
    return render(request, 'blog/comment.html', context)


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
