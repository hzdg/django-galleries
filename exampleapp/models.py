from galleries.models import Gallery
from django.db import models
from imagekit.models import ImageSpec
from imagekit.processors import ResizeToFit


class Photo(models.Model):
    title = models.CharField(max_length=50)
    caption = models.CharField(max_length=100)
    original_image = models.ImageField(upload_to='galleries')
    full = ImageSpec([ResizeToFit(400, 200)])
    thumbnail = ImageSpec([ResizeToFit(50, 50)], source='original_image')

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']


class PortfolioImage(models.Model):
    title = models.CharField(max_length=50)
    caption = models.CharField(max_length=100)
    original_image = models.ImageField(upload_to='galleries')
    thumbnail = ImageSpec([ResizeToFit(70, 40)], source='original_image')

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Video(models.Model):
    title = models.CharField(max_length=50)
    video = models.FileField(upload_to='galleries/video/video')
    thumbnail = models.ImageField(upload_to='galleries/video/thumbnail', blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']


class PhotoAlbum(Gallery):
    class GalleryMeta:
        member_models = [Photo]

    class Meta:
        verbose_name = 'Photo Album'


class Portfolio(Gallery):
    class GalleryMeta:
        member_models = [Video]
        membership_class = 'PortfolioMembership'


class PortfolioMembership(Portfolio.BaseMembership):
    extra_field = models.CharField(max_length=10)
