from django.apps import AppConfig

class PhotosConfig(AppConfig):
    name = 'Photos'

    def ready(self):
        import Photos.receivers
