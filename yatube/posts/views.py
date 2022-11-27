from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, Follow
from .utils import get_paginator

User = get_user_model()


@cache_page(20)
def index(request):
    posts = Post.objects.select_related(
        'author', 'group')[:settings.NUMBER_POSTS]
    pagin = get_paginator(posts, request)
    return render(request,
                  'posts/index.html',
                  context={'posts': posts,
                           'page_obj': pagin,
                           })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    pagin = get_paginator(posts, request)
    return render(request,
                  'posts/group_list.html',
                  context={'group': group,
                           'page_obj': pagin,
                           })


def profile(request, username):
    posts_authors = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related(
        'group', 'author').filter(author=posts_authors)
    pagin = get_paginator(post_list, request)
    return render(request,
                  'posts/profile.html',
                  context={'page_obj': pagin,
                           'posts_authors': posts_authors, })


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    post_detail = post.text
    comments = post.comments.select_related('author')
    form = CommentForm()
    return render(request,
                  'posts/post_detail.html',
                  context={'post': post,
                           'post_detail': post_detail,
                           'form': form,
                           'comments': comments,
                           })


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None,)
    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        create_post.save()
        return redirect('posts:profile', create_post.author)
    return render(request, 'posts/create_post.html', context={'form': form})


@login_required
def post_edit(request, post_id):
    edit_post = get_object_or_404(Post, id=post_id)
    if request.user != edit_post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=edit_post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request,
                  'posts/create_post.html',
                  context={'post': edit_post,
                           'form': form,
                           'is_edit': True})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user)
    pagin = get_paginator(posts, request)
    return render(request, 'posts/follow.html', context={'page_obj': pagin})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    user_follower = get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    )
    user_follower.delete()
    return redirect('posts:profile', username)
