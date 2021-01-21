from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm
from .owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.decorators.cache import cache_page

User = get_user_model()


# @cache_page(60 * 20)
def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'index.html', {'page': page, 'paginator': paginator, 'tmpl': 'index'})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'group.html', {"group": group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            print(request.user.get_full_name)
            Post.objects.create(**form.cleaned_data, author=request.user)
            return redirect('index')
    else:
        form = PostForm()

    return render(request, 'post_new.html', {'form': form})


def profile(request, username):
    # if request.user.username == username:
    #     return HttpResponse('You are not allowed to view current users profile')

    user_profile = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user_profile)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    following = False
    if not request.user.is_anonymous:
        following = Follow.objects.filter(user=request.user, author=user_profile).exists()

    return render(request, 'profile.html', {
        'page': page, 'profile': user_profile, 'paginator': paginator, 'following': following
    })


def post_view(request, username, post_id):
    user_profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=user_profile)
    form = CommentForm()
    comments = Comment.objects.filter(post=post)
    return render(request, 'post.html', {'user_profile': user_profile, 'post': post, 'form': form, 'items': comments})


@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)

    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)
    # добавим в form свойство files
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect("post", username=request.user.username, post_id=post_id)

    return render(request, 'post_edit.html', {'form': form, 'post': post})


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=user)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post', username=username, post_id=post_id)

    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):

    # информация о текущем пользователе доступна в переменной request.user
    follows = request.user.following.all()
    # follows = Follow.objects.filter(user=request.user).all()

    post_list = list()

    for follow in follows:
        print(follow.user, '->', follow.author)
        query_set = follow.author.posts.all()
        for post in query_set:
            post_list.append(post)

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'follow.html', {'page': page, 'paginator': paginator, 'tmpl': 'follow'})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return HttpResponse('Cannot follow yourself')
    if request.method == 'GET':
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.method == 'GET':
        follow = get_object_or_404(Follow, user=request.user, author=author)
        follow.delete()
    return redirect('profile', username=username)
