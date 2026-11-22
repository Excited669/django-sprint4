"""Static pages and custom HTTP error handlers."""

from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    """About the project."""

    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """The site's rules."""

    template_name = 'pages/rules.html'


def csrf_failure(request, reason=''):
    """Render the CSRF rejection page."""
    return render(request, 'pages/403csrf.html', status=403)


def permission_denied(request, exception):
    """Render HTTP 403 with the supplied error template."""
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    """Render HTTP 404 with the supplied error template."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Render HTTP 500 with the supplied error template."""
    return render(request, 'pages/500.html', status=500)
