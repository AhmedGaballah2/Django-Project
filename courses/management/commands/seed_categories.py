from django.core.management.base import BaseCommand

from courses.models import Category


DEFAULT_CATEGORIES = [
    ("Programming", "programming"),
    ("Design", "design"),
    ("Business", "business"),
]


class Command(BaseCommand):
    help = "Seed default course categories (at least 3)."

    def handle(self, *args, **options):
        created = 0
        for name, slug in DEFAULT_CATEGORIES:
            _, was_created = Category.objects.get_or_create(
                slug=slug, defaults={"name": name}
            )
            if was_created:
                created += 1
        self.stdout.write(
            self.style.SUCCESS(f"Categories ready ({created} newly created).")
        )
