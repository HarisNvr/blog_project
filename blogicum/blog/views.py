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


def get_post_details(post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentaryForm()
    comments = (Commentary.objects.filter(post_id=post_id)
                .order_by('created_at'))
    return post, form, comments


def detail(request, post_id):
    post, form, comments = get_post_details(post_id)

    if (post.is_published == 0 or post.category.is_published == 0
            or post.pub_date > timezone.now()):
        if post.author == request.user:
            template = 'blog/detail.html'
            context = {'post': post, 'form': form, 'comments': comments}
            return render(request, template, context)
        else:
            raise Http404
    else:
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
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            post_detail_url = reverse_lazy('blog:profile',
                                           args=[request.user.username])
            return redirect(post_detail_url)
    else:
        form = PostForm()
    context = {'form': form}
    return render(request, 'blog/create.html', context)


def edit_post(request, pk):
    print(request.user.is_authenticated)
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author and request.user.is_authenticated:
        return redirect('blog:post_detail', post_id=pk)
    elif not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            post_detail_url = reverse_lazy('blog:profile',
                                           args=[request.user.username])
            return redirect(post_detail_url)
    else:
        form = PostForm(instance=post)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, pk):
    instance = get_object_or_404(Post, pk=pk)
    form = PostForm(instance=instance)
    context = {'form': form}
    if (request.method == 'POST'
            and (request.user == instance.author
                 or request.user.is_superuser)):
        instance.delete()
        return redirect('blog:homepage')
    return render(request, 'blog/create.html', context)


@login_required
def create_comment(request, post_id):
    post = get_object_or_404(base_request(), pk=post_id)
    if request.method == 'POST':
        form = CommentaryForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            post.comment_count += 1
            post.save()
            post_detail_url = reverse_lazy('blog:post_detail', args=[post_id])
            return redirect(post_detail_url)
    else:
        form = CommentaryForm()
    context = {'form': form}
    return render(request, 'blog/comment.html', context)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Commentary, id=comment_id)
    if comment.author != request.user:
        raise Http404
    if request.method == 'POST':
        form = CommentaryForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            post_detail_url = reverse_lazy('blog:post_detail', args=[post_id])
            return redirect(post_detail_url)
    else:
        form = CommentaryForm(instance=comment)
    context = {'form': form, 'comment': comment}
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(base_request(), pk=post_id)
    comment = get_object_or_404(Commentary, id=comment_id)
    if comment.author != request.user:
        raise Http404
    if request.method == 'POST':
        comment.delete()
        post.comment_count -= 1
        post.save()
        post_detail_url = reverse_lazy('blog:post_detail', args=[post_id])
        return redirect(post_detail_url)
    context = {'comment': comment}
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
