"""Views for posts, profiles and comments in Blogicum."""

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.utils import timezone

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post


User = get_user_model()
POSTS_PER_PAGE = 10


def published_posts():
    """Return posts visible to all visitors, including comment counts."""
    return (
        Post.objects.select_related('author', 'category', 'location')
        .filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )


def paginated_posts(request, queryset):
    """Paginate a queryset using ten posts per page."""
    return Paginator(queryset, POSTS_PER_PAGE).get_page(
        request.GET.get('page')
    )


def index(request):
    """Show ten most recent public posts."""
    page_obj = paginated_posts(request, published_posts())
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, category_slug):
    """List public posts from a published category."""
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )
    page_obj = paginated_posts(
        request, published_posts().filter(category=category)
    )
    return render(
        request,
        'blog/category.html',
        {'category': category, 'page_obj': page_obj},
    )


def profile(request, username):
    """Show a user's public posts or all posts to their owner."""
    profile_user = get_object_or_404(User, username=username)
    posts = (
        Post.objects.filter(author=profile_user)
        .select_related('author', 'category', 'location')
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
    if request.user != profile_user:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )
    page_obj = paginated_posts(request, posts)
    return render(
        request,
        'blog/profile.html',
        {'profile': profile_user, 'page_obj': page_obj},
    )


@login_required
def edit_profile(request):
    """Allow a signed-in user to update only their own information."""
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


def get_accessible_post(request, post_id):
    """Allow unpublished and scheduled posts to be read by their author."""
    post = get_object_or_404(
        Post.objects.select_related('author', 'category', 'location'),
        pk=post_id,
    )
    if request.user != post.author and (
        not post.is_published
        or post.pub_date > timezone.now()
        or post.category is None
        or not post.category.is_published
    ):
        raise Http404('Публикация недоступна')
    return post


def post_detail(request, post_id):
    """Display an accessible post with chronological comments."""
    post = get_accessible_post(request, post_id)
    comments = post.comments.select_related('author').order_by(
        'created_at', 'pk'
    )
    return render(
        request,
        'blog/detail.html',
        {
            'post': post,
            'form': CommentForm(),
            'comments': comments,
        },
    )


@login_required
def create_post(request):
    """Publish a post or schedule it for later."""
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    """Allow only the author to change a post."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author_id != request.user.pk:
        return redirect('blog:post_detail', post_id=post.pk)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.pk)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    """Confirm a post's deletion before removing it."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author_id != request.user.pk:
        return redirect('blog:post_detail', post_id=post.pk)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    return render(
        request, 'blog/create.html', {'form': PostForm(instance=post)}
    )


@login_required
def add_comment(request, post_id):
    """Attach a new comment to an accessible post."""
    post = get_accessible_post(request, post_id)
    if request.method != 'POST':
        return redirect('blog:post_detail', post_id=post.pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('blog:post_detail', post_id=post.pk)
    return render(
        request,
        'blog/detail.html',
        {
            'post': post,
            'form': form,
            'comments': post.comments.select_related('author'),
        },
    )


@login_required
def edit_comment(request, post_id, comment_id):
    """Allow only the comment author to edit a comment."""
    comment = get_object_or_404(
        Comment, pk=comment_id, post_id=post_id
    )
    if comment.author_id != request.user.pk:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request, 'blog/comment.html',
        {'form': form, 'comment': comment},
    )


@login_required
def delete_comment(request, post_id, comment_id):
    """Confirm a comment's deletion before removing it."""
    comment = get_object_or_404(
        Comment, pk=comment_id, post_id=post_id
    )
    if comment.author_id != request.user.pk:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})
