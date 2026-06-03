from django.db.models import Q


def filter_published_courses(queryset, *, search=None, category=None, level=None):
    """Apply search/category/level filters to a published-courses queryset."""
    if level:
        queryset = queryset.filter(level=level)
    if category:
        queryset = queryset.filter(category__slug=category)
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    return queryset
