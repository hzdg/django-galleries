from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from imagekit.models import ImageModel as _ImageModel
from imagekit import processors
from imagekit.specs import ImageSpec
from django.db.models.base import ModelBase
from django.db.models import Q
import sys, imp, importlib


class ImageModel(_ImageModel, models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    original_image = models.ImageField(upload_to='galleries')

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']
    
    class IKOptions:
        default_image_field = 'original_image'


# def create_membership_model(app_label, class_name, gallery_model, member_models, verbose_name=None):
#     _app_label = app_label
#     _verbose_name = verbose_name
#     member_choices = Q()
#     for member_model in member_models:
#         member_choices |= Q(app_label=member_model._meta.app_label,
#             model=member_model._meta.module_name)
#     
#     # TODO: Pull this out so that people can make their own custom membership classes without having to rewire everything.
#     class DynamicGalleryMembership(models.Model):
#         gallery = models.ForeignKey(gallery_model, related_name='memberships')
#         content_type = models.ForeignKey(ContentType,
#                 limit_choices_to=member_choices)
#         object_id = models.PositiveIntegerField()
#         item = generic.GenericForeignKey('content_type', 'object_id')
#         sort_order = models.IntegerField(default=0)
# 
#         def __unicode__(self):
#             return str(self.item)
# 
#         class __metaclass__(ModelBase):
#             def __new__(cls, old_class_name, bases, attrs):
#                 return ModelBase.__new__(cls, class_name, bases, attrs)
# 
#         class Meta:
#             app_label = _app_label
#             verbose_name = _verbose_name
#             ordering = ['sort_order']
# 
#     return DynamicGalleryMembership


class GalleryBase(ModelBase):

    def __init__(cls, class_name, bases, attrs):
        if [b for b in bases if isinstance(b, GalleryBase)]:
            gallery_meta = getattr(cls, 'GalleryMeta')
            gallery_meta.gallery_class = cls
            cls._gallery_meta = gallery_meta

            # Don't inherit Membership classes.
            membership_class = attrs.get('Membership')
            print cls
            print membership_class
            if membership_class is not None:
                del attrs['Membership']
            ModelBase.__init__(cls, class_name, bases, attrs)
            try:
                delattr(cls, 'Membership')
            except AttributeError:
                pass

            # If there is no inner Membership class, create one.
            if membership_class is None:
                membership_class = type('Membership', (Gallery.Membership,), {
                        '__module__': cls.__module__})

            # Augment the membership class with the relational fields. You can
            # "opt out" of this by not extending Gallery.Membership
            if issubclass(membership_class, Gallery.Membership):
                _update_membership(membership_class, cls)

            cls.Membership = membership_class
        else:
            ModelBase.__init__(cls, class_name, bases, attrs)


def _update_membership(membership, gallery):
    gallery_meta = gallery._gallery_meta
    member_choices = Q()
    for member_model in gallery_meta.member_models:
        member_choices |= Q(app_label=member_model._meta.app_label,
                model=member_model._meta.module_name)
    fields = {
        'gallery': models.ForeignKey(gallery_meta.gallery_class,
                related_name='memberships'),
        'content_type': models.ForeignKey(ContentType,
                limit_choices_to=member_choices),
        'object_id': models.PositiveIntegerField(),
        'item': generic.GenericForeignKey('content_type', 'object_id'),
    }
    for k, v in fields.items():
        v.contribute_to_class(membership, k)


class Gallery(models.Model):
    __metaclass__ = GalleryBase

    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

    class Membership(models.Model):
        sort_order = models.IntegerField(default=0)

        def __unicode__(self):
            return str(self.item)

    class GalleryMeta:
        pass
