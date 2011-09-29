from galleries.models import Gallery, ImageModel
from django.db import models
from imagekit.models import ImageSpec
from imagekit.processors.resize import Fit


class Photo(ImageModel):
    thumbnail = ImageSpec([Fit(50, 50)])
    full = ImageSpec([Fit(400, 200)])
    caption = models.CharField(max_length=100)


class PortfolioImage(ImageModel):
    thumbnail = ImageSpec([Fit(70, 40)])


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
