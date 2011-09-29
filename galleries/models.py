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

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']


class ProxyImageModel(ImageModel):
    class Meta:
        proxy = True


def _create_membership_class(class_name, verbose_name, app_label, module_name,
        module, member_models, abstract, gallery_class):

    _app_label = app_label
    _verbose_name = verbose_name
    _abstract = abstract

    member_choices = Q()
    for member_model in member_models:
        member_choices |= Q(app_label=member_model._meta.app_label,
                model=member_model._meta.module_name)

    class DynamicMembership(Gallery.BaseMembership):

        gallery = models.ForeignKey(gallery_class, related_name='memberships')
        content_type = models.ForeignKey(ContentType,
                limit_choices_to=member_choices)

        class __metaclass__(Gallery.BaseMembership.__metaclass__):
            def __new__(cls, name, bases, attrs):
                if not _abstract:
                    attrs['__module__'] = module_name
                return Gallery.BaseMembership.__metaclass__.__new__(cls, class_name,
                    bases, attrs)
        class Meta:
            abstract = _abstract
            app_label = _app_label
            verbose_name = _verbose_name

    return DynamicMembership


class GalleryBase(ModelBase):

    def __init__(cls, class_name, bases, attrs):
        if [b for b in bases if isinstance(b, GalleryBase)]: # Don't execute for Gallery itself
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

            membership_verbose_name = '%s Membership' % cls._meta.verbose_name
            custom_membership = getattr(gallery_meta, 'membership_class', None)

            if custom_membership:
                membership_class_name = '%sBaseMembership' % class_name
            else:
                membership_class_name = '%sMembership' % class_name

            module_name = cls.__module__
            module = importlib.import_module(module_name)

            membership_class = _create_membership_class(
                    class_name=membership_class_name,
                    verbose_name=membership_verbose_name,
                    app_label=cls._meta.app_label,
                    module_name=module_name,
                    module=module,
                    member_models=member_models,
                    abstract=bool(custom_membership),
                    gallery_class=cls,
            )

            if custom_membership:
                cls.BaseMembership = membership_class
                def getter(self):
                    return getattr(module, custom_membership)
                cls.Membership = property(getter)
            else:
                cls.Membership = membership_class

        ModelBase.__init__(cls, class_name, bases, attrs)


class Gallery(models.Model):
    __metaclass__ = GalleryBase

    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title

    class BaseMembership(models.Model):
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
