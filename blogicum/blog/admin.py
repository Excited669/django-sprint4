"""Admin interface for managing blog content."""

from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Manage publication categories."""

    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('is_published',)
    search_fields = ('title', 'description')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Manage geographical labels."""

    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('is_published',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Manage posts and scheduled publications."""

    list_display = (
        'title',
        'author',
        'category',
        'pub_date',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    list_filter = ('is_published', 'category', 'pub_date')
    search_fields = ('title', 'text')
    list_select_related = ('author', 'category', 'location')
    date_hierarchy = 'pub_date'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Manage readers' comments."""

    list_display = ('post', 'author', 'created_at')
    search_fields = ('text',)
    list_select_related = ('post', 'author')
