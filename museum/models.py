from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from imagekit.models import ImageModel as _ImageModel


class ImageModel(_ImageModel, models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    original_image = models.ImageField(upload_to='crap')

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']
    
    class IKOptions:
        image_field = 'original_image'


class GalleryModel(models.Model):
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title


class GalleryMembership(models.Model):
    gallery = models.ForeignKey(GalleryModel, related_name="memberships")
    content_type = models.ForeignKey(ContentType)
                            # limit_choices_to=galleryrelation_limits)
    object_id = models.PositiveIntegerField()
    item = generic.GenericForeignKey('content_type', 'object_id')
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order']
