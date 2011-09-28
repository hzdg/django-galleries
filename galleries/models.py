from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.base import ModelBase
from django.db.models import Q
from django.core.exceptions import FieldError
import sys, imp, importlib


class GalleryMetaNotDefined(Exception):
    "The gallery is missing the required meta class."
    pass


class MemberModelsNotDefined(Exception):
    "The gallery options do not define a list of allowed member models."
    pass


class MembershipClassNotDefined(Exception):
    "The gallery does not define a membership class."
    pass


class ImageModel(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    original_image = models.ImageField(upload_to='galleries')

    class __metaclass__(models.base.ModelBase):
        def __new__(cls, class_name, bases, attrs):
            orig_attrs = attrs.copy()
            if attrs['__module__'] != cls.__module__:
                Meta = attrs.get('Meta')
                if Meta is None:
                    class Meta:
                        proxy = True
                    attrs['Meta'] = Meta
                else:
                    Meta.proxy = True
            try:
                return models.base.ModelBase.__new__(cls, class_name, bases, attrs)
            except FieldError:
                return models.base.ModelBase.__new__(cls, class_name, bases, orig_attrs)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']


class GalleryBase(ModelBase):

    def __init__(cls, class_name, bases, attrs):
        if [b for b in bases if isinstance(b, GalleryBase)]:
            try:
                membership_class = getattr(cls, 'Membership')
            except AttributeError:
                raise MembershipClassNotDefined('%s must define a Membership class.' % class_name)
            try:
                gallery_meta = getattr(cls, 'GalleryMeta')
            except AttributeError:
                raise GalleryMetaNotDefined('%s must define GalleryMeta.' % class_name)
            try:
                member_models = getattr(gallery_meta, 'member_models')
            except AttributeError:
                raise MemberModelsNotDefined('%s.GalleryMeta must define a list of member_models.' % class_name)

            gallery_meta.gallery_class = cls
            cls._gallery_meta = gallery_meta

            # Don't inherit Membership classes.
            try:
                del attrs['Membership']
            except KeyError:
                pass
            try:
                delattr(cls, 'Membership')
            except AttributeError:
                pass

            membership_class_name = '%sMembership' % class_name
            membership_verbose_name = '%s Membership' % cls._meta.verbose_name

            if (membership_class is Gallery.Membership):
                _app_label = cls._meta.app_label
                module_name = '%s.models' % _app_label
                module = importlib.import_module(module_name)

                class DynamicMembership(Gallery.Membership):
                    class __metaclass__(Gallery.Membership.__metaclass__):
                        def __new__(cls, name, bases, attrs):
                            attrs['__module__'] = module_name
                            return Gallery.Membership.__metaclass__.__new__(cls,
                                membership_class_name, bases, attrs)
                    class Meta:
                        app_label = _app_label
                        verbose_name = membership_verbose_name

                membership_class = DynamicMembership

            # Augment the membership class with the relational fields. You can
            # "opt out" of this by not extending Gallery.Membership
            # TODO: Make this less magical.
            if issubclass(membership_class, Gallery.Membership):
                _update_membership(membership_class, cls)

            setattr(cls, 'Membership', DynamicMembership)

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
    }
    for k, v in fields.items():
        v.contribute_to_class(membership, k)


class Gallery(models.Model):
    __metaclass__ = GalleryBase

    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

    class Membership(models.Model):
        object_id = models.PositiveIntegerField()
        item = generic.GenericForeignKey('content_type', 'object_id')
        sort_order = models.IntegerField(default=0)

        def __unicode__(self):
            return str(self.item)

        class Meta:
            ordering = ['sort_order']
            abstract = True

    class GalleryMeta:
        pass

    class Meta:
        abstract = True
