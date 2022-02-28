from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

PST_PER_PG = 10


def pagin_obj(page, objects, pst_per_pg=PST_PER_PG):
    paginator = Paginator(objects, pst_per_pg)
    return paginator.get_page(page)


def index(request) -> HttpResponse:
    '''Функция выводит на главную последние посты'''
    post_list = (
        Post.objects
        .select_related('group', 'author')
        .order_by('-created')
    )
    page_number = request.GET.get('page')
    page_obj = pagin_obj(page_number, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug) -> HttpResponse:
    '''Функция выводит последние посты выбранного сообщества'''
    group = get_object_or_404(Group, slug=slug)
    post_list = (
        group.posts.select_related('group', 'author').order_by('-created')
    )
    page_number = request.GET.get('page')
    page_obj = pagin_obj(page_number, post_list)
    context = {
        'page_obj': page_obj,
        'group': group
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username) -> HttpResponse:
    '''Функция просмотра постов пользователя'''
    author = get_object_or_404(User, username=username)
    post_list = (
        Post.objects
            .filter(author=author)
            .select_related('group', 'author')
            .order_by('-created')
    )
    page_number = request.GET.get('page')
    page_obj = pagin_obj(page_number, post_list)
    following = Follow.objects.filter(
        user=request.user, author=author).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id) -> HttpResponse:
    '''Функция просмотра деталей поста'''
    post = get_object_or_404(Post, pk=post_id)
    how_much_posts = Post.objects.filter(author=post.author).count()
    form = CommentForm()
    comments = Comment.objects.filter(post=post_id)
    context = {
        'post': post,
        'how_much_posts': how_much_posts,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    '''Функция для создания новых постов'''
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    context = {
        'form': form
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    '''Функция для редактирования существующих постов'''
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    my_authors = (
        Post.objects
            .filter(author__following__user=request.user)
            .select_related('author', 'group')
            .order_by('-created')
    )
    page_number = request.GET.get('page')
    page_obj = pagin_obj(page_number, my_authors)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    favour = Follow.objects.filter(user=request.user, author=author)
    if favour.exists():
        favour.delete()
    return redirect('posts:profile', username)
