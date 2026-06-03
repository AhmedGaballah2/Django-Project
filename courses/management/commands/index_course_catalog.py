from django.core.management.base import BaseCommand

from courses.ai.catalog_index import reindex_all_published
from courses.ai.config import ai_configured


class Command(BaseCommand):
    help = "Embed all published courses into the ChromaDB catalog (requires OPENAI_API_KEY)."

    def handle(self, *args, **options):
        if not ai_configured():
            self.stderr.write(
                self.style.ERROR("OPENAI_API_KEY is not set. Add it to your .env file first.")
            )
            return
        reindex_all_published()
        self.stdout.write(self.style.SUCCESS("Published course catalog indexed."))
