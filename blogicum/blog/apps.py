"""Django app configuration for the blog."""

from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Display a Russian name in the Django admin."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name = 'Блог'
