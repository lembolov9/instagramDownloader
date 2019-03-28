import uuid

from django.db import models

# Create your models here.


def gen_zip_name(instance, name):
    return f'archives/{instance.name}.zip'

def ger_photo_name(instance, user):
    return f'photos/{user}/{uuid.uuid4()}.jpg'


class ProfilePhotos(models.Model):
    name = models.CharField(max_length=40)
    add_date = models.DateTimeField(auto_now_add=True)
    count = models.IntegerField()
    zip = models.FileField(upload_to=gen_zip_name, blank=True)


class Photo(models.Model):
    img = models.ImageField(upload_to=ger_photo_name)
    user = models.ForeignKey(ProfilePhotos, on_delete=models.CASCADE)