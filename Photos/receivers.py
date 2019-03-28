import os
import shutil

from django.db.models.signals import post_delete
from django.dispatch import receiver

from Photos.models import ProfilePhotos, Photo, ger_photo_name
from instagramDownloader.settings import MEDIA_ROOT


@receiver(post_delete, sender=ProfilePhotos)
@receiver(post_delete, sender=Photo)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if ( sender == ProfilePhotos and instance.zip):
        if os.path.isfile(instance.zip.path):
            os.remove(instance.zip.path)
        shutil.rmtree(os.path.join(MEDIA_ROOT, f'photos/{instance.name}'), ignore_errors=True)
