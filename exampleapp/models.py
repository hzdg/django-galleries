from galleries.models import Gallery
from django.db import models


class PhotoAlbum(Gallery):
    class GalleryOptions:
        extra_image_sizes = {
            'thumbnail': (50, 50),
            'full': (400, 200),
        }
    class Meta:
        verbose_name = 'Photo Album'


class Video(models.Model):
    """
    Default Video models
    """
    title = models.CharField(max_length=50)
    video = models.FileField(upload_to='galleries/video/video')
    thumbnail = models.ImageField(upload_to='galleries/video/thumbnail', blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Portfolio(Gallery):
    class GalleryOptions:
        extra_image_sizes = {
            'thumbnail': (70, 40),
        }
        member_models = [Video]
