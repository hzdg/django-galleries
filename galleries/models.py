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
        image_field = 'original_image'


def create_image_model(app_label, class_name, specs, verbose_name=None):
    _app_label = app_label
    _verbose_name = verbose_name
    
    # Currently, ImageKit requires that you specify a module containing the
    # specs. We could use our own metaclass to override this behavior, but
    # programmatically generating a specs module is less likely to cause issues
    # with future versions of IK.
    spec_module_name = 'galleries.specs.dynamic.%s.%s' % (app_label, class_name.lower())
    parts = spec_module_name.split('.')
    for i in range(len(parts)):
        module_name = '.'.join(parts[0:i+1])
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            module = sys.modules[module_name] = imp.new_module(module_name)
    for spec in specs:
        setattr(module, spec.name(), spec)
    
    class DynamicImageModel(ImageModel):
        class __metaclass__(ImageModel.__metaclass__):
            def __new__(cls, old_class_name, bases, attrs):
                return ImageModel.__metaclass__.__new__(cls, class_name, bases, attrs)
        
        class IKOptions:
            spec_module = spec_module_name
            image_field = 'original_image'
            cache_filename_format = '%s/%s/' % (app_label, class_name.lower()) \
                + '/%(filename)s_%(specname)s.%(extension)s'
        
        class Meta:
            app_label = _app_label
            verbose_name = _verbose_name
            proxy = True

    return DynamicImageModel


def create_sizes_image_model(app_label, class_name, sizes, verbose_name=None):
    """Create an image model that exposes different sizes of the image.
    
    Keword arguments:
    app_label -- the app label to use for the new image model
    class_name -- the name of the new image model
    sizes -- a dictionary whose keys are the names of properties to create on
        the image model and values are the corresponding sizes: tuples in the
        form (width, height).

    """
    specs = []
    for name, size in sizes.items():
        w, h = size

        class ResizeProcessor(processors.Resize):
            width = w
            height = h
            crop = True

        class Spec(ImageSpec): # TODO: Expose a way to set this base class.
            access_as = name
            processors = [ResizeProcessor]

        specs.append(Spec)

    return create_image_model(app_label, class_name, specs, verbose_name)


def create_membership_model(app_label, class_name, gallery_model, member_models, verbose_name=None):
    _app_label = app_label
    _verbose_name = verbose_name
    member_choices = Q()
    for member_model in member_models:
        member_choices |= Q(app_label=member_model._meta.app_label,
            model=member_model._meta.module_name)
    
    # TODO: Pull this out so that people can make their own custom membership classes without having to rewire everything.
    class DynamicGalleryMembership(models.Model):
        gallery = models.ForeignKey(gallery_model, related_name='memberships')
        content_type = models.ForeignKey(ContentType,
                limit_choices_to=member_choices)
        object_id = models.PositiveIntegerField()
        item = generic.GenericForeignKey('content_type', 'object_id')
        sort_order = models.IntegerField(default=0)

        def __unicode__(self):
            return str(self.item)

        class __metaclass__(ModelBase):
            def __new__(cls, old_class_name, bases, attrs):
                return ModelBase.__new__(cls, class_name, bases, attrs)

        class Meta:
            app_label = _app_label
            verbose_name = _verbose_name
            ordering = ['sort_order']

    return DynamicGalleryMembership


class GalleryBase(ModelBase):
    def __init__(cls, class_name, bases, attrs):
        if [b for b in bases if isinstance(b, GalleryBase)]:
            opts = getattr(cls, 'GalleryOptions', None)
            app_label = cls._meta.app_label

            member_models = getattr(opts, 'member_models', None) or []
            extra_image_sizes = getattr(opts, 'extra_image_sizes', None)

            # Create an additional member model based on the info in extra_image_sizes
            if extra_image_sizes:
                image_model_name = '%sImage' % class_name
                image_model_verbose_name = '%s Image' % cls._meta.verbose_name
                image_model = create_sizes_image_model(app_label,
                        image_model_name, extra_image_sizes,
                        image_model_verbose_name)
                member_models.append(image_model)

            if not member_models:
                raise Exception('Your Gallery must declare member_models or extra_image_sizes in its GalleryOptions.')

            membership_model = getattr(opts, 'membership_model', None)
            if not membership_model:
                membership_model_name = '%sMembership' % class_name
                membership_model_verbose_name = '%s Membership' % cls._meta.verbose_name
                membership_model = create_membership_model(app_label, membership_model_name,
                    cls, member_models, verbose_name=membership_model_verbose_name)
            
            cls._gallery_meta = type('GalleryMeta', (object,), {
                'membership_model': membership_model,
                'member_models': member_models,
            })
            cls.Membership = cls._gallery_meta.membership_model

        return ModelBase.__init__(cls, class_name, bases, attrs)


class Gallery(models.Model):
    __metaclass__ = GalleryBase

    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title
