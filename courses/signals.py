from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .ai.catalog_index import index_course, remove_course_from_index
from .ai.document_index import index_course_document, remove_course_document_from_index
from .models import Course, CourseDocument


@receiver(post_save, sender=Course)
def on_course_saved(sender, instance, **kwargs):
    if instance.is_published:
        index_course(instance)
    else:
        remove_course_from_index(instance.id)


@receiver(post_save, sender=CourseDocument)
def on_course_document_saved(sender, instance, created, **kwargs):
    if instance.file:
        index_course_document(instance)


@receiver(post_delete, sender=CourseDocument)
def on_course_document_deleted(sender, instance, **kwargs):
    remove_course_document_from_index(instance)
