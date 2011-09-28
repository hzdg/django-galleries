from galleries.models import Gallery, ImageModel
from django.db import models
from imagekit.models import ImageSpec
from imagekit.processors.resize import Fit


class Photo(ImageModel):
    thumbnail = ImageSpec([Fit(50, 50)], image_field='original_file')
    full = ImageSpec([Fit(400, 200)], image_field='original_file')


class PortfolioImage(ImageModel):
    thumbnail = ImageSpec([Fit(70, 40)], image_field='original_file')


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
    class PortfolioMembership(Gallery.Membership):
        extra_field = models.CharField(max_length=10)

    class GalleryMeta:
        member_models = [Video]
