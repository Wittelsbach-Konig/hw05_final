from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from .forms import PostForm, CommentForm
from .models import Group, Post, Comment, Follow
from .paginator.paginator import custom_paginator

User = get_user_model()
DEFAULT_POSTS_NUMBER = 10  # Базовое число выводимых постов


def index(request):
    """Главная страница
        posts : Объект типа Post
        template : Шаблон html
        context : Словарь контекста
    """
    post_list = Post.objects.select_related('group', 'author').all()
    page_obj = custom_paginator(request, post_list, DEFAULT_POSTS_NUMBER)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Фильтрация по группам
        slug : Уникальный фрагмент URL
        template : Шаблон списка групп
        posts : Объект типа Post
        context : Словарь контекста
    """
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author').all()
    page_obj = custom_paginator(request, post_list, DEFAULT_POSTS_NUMBER)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Профайл пользователя"""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group').all()
    page_obj = custom_paginator(request, post_list, DEFAULT_POSTS_NUMBER)
    template = 'posts/profile.html'
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Страница поста"""
    post = get_object_or_404(Post.objects.select_related('author', 'group'),
                             pk=post_id)
    comments = Comment.objects.filter(post=post)

    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста"""

    template_name = 'posts/create_post.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'posts:profile',
            kwargs={'username': self.request.user.username}
        )


@login_required
def post_edit(request, post_id):
    """Редактирование поста"""
    template_create = 'posts/create_post.html'
    related_path = 'posts:post_detail'
    post = get_object_or_404(Post.objects.select_related('author', 'group'),
                             pk=post_id)
    if request.user != post.author:
        return redirect(related_path, post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect(related_path, post_id=post_id)
    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, template_create, context)


@login_required
def add_comment(request, post_id):
    """Добавление комментариев"""
    post = get_object_or_404(Post.objects.select_related('author', 'group'),
                             pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Лента подписок"""
    list_of_posts = Post.objects.filter(author__following__user=request.user)
    page_obj = custom_paginator(request, list_of_posts, DEFAULT_POSTS_NUMBER)
    context = {'page_obj': page_obj}
    template = 'posts/follow.html'
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписаться"""
    user = request.user
    author = User.objects.get(username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=author)


@login_required
def profile_unfollow(request, username):
    """Отписаться"""
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect('posts:profile', username=author)
