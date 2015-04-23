from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.base import ModelBase
from django.db.models import Q

try:
    import importlib
except ImportError:
    from django.utils import importlib


class GalleryMetaNotDefined(Exception):
    "The gallery is missing the required meta class."
    pass


class MemberModelsNotDefined(Exception):
    "The gallery options do not define a list of allowed member models."
    pass


class MembershipClassNotDefined(Exception):
    "The gallery does not define a membership class."
    pass


class ImageModelBase(type(models.Model)):
    def __new__(self, class_name, bases, attrs):
        """Since ``ImageModel`` is not abstract, Django will automatically add a
        ``OneToOneField`` on base classes pointing back to it. Unfortunately,
        it doesn't set a ``related_name``, which means the default is used.

        Since the default is generated using only the model class name, if you
        have two models with the same name in different apps, you will have a
        conflict. So we create our own ``OneToOneField`` with a more
        descriptive ``related_name``.
        """
        if [b for b in bases if isinstance(b, ImageModelBase)]:
            has_parent_link = False

            for field in attrs.values():
                if hasattr(field, 'parent_link'):
                    has_parent_link = True
                    break

            if not has_parent_link:
                field = models.OneToOneField(bases[0], parent_link=True,
                        related_name='%(app_label)s_%(class)s')

                # This is needed to set the related_name.
                # By default this attribute is not in the attributes dict
                attrs['%s_ptr' % (class_name)] = field

        return type(models.Model).__new__(self, class_name, bases,
                attrs)


class ImageModel(models.Model):
    """
    This model is deprecated

    It's recommended that you just define your own member models.
    """
    __metaclass__ = ImageModelBase
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    original_image = models.ImageField(upload_to='galleries', max_length=255)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']


class EmbedModel(models.Model):
    """
    This model is deprecated

    It's recommended that you just define your own member models.

    Allow the insert of emebed codes in the model
    """
    __metaclass__ = ImageModelBase
    title = models.CharField(max_length=50)
    embed_code = models.TextField()

    def __unicode__(self):
        return self.title


def get_default(member_models, member_choices):
    if len(member_models) == 1 and ContentType.objects.filter(member_choices).exists():
        default_content = ContentType.objects.filter(member_choices)
        return default_content[0]
    return None

def _create_membership_class(class_name, verbose_name, app_label, module_name,
        member_models, abstract, gallery_class):
    """Creates a membership class to relate a gallery with its member models.

    """

    _app_label = app_label
    _verbose_name = verbose_name
    _abstract = abstract

    class Meta(Gallery.BaseMembership.Meta):
        abstract = _abstract
        app_label = _app_label
        verbose_name = _verbose_name

    member_choices = Q()
    for member_model in member_models:
        member_choices |= Q(app_label=member_model._meta.app_label, model=member_model._meta.module_name)

    return type(
        class_name,
        (Gallery.BaseMembership,),
        dict(
            gallery=models.ForeignKey(gallery_class,
                                      related_name='memberships'),
            content_type=models.ForeignKey(ContentType,
                    default=get_default(member_models, member_choices),
                    blank=True,
                    limit_choices_to=member_choices),
            __module__=module_name,
            Meta=Meta,
        )
    )


class GalleryBase(ModelBase):

    def __init__(cls, class_name, bases, attrs):
        # Don't execute for Gallery itself
        if [b for b in bases if isinstance(b, GalleryBase)]:
            try:
                gallery_meta = getattr(cls, 'GalleryMeta')
            except AttributeError:
                raise GalleryMetaNotDefined('%s must define GalleryMeta.' %
                                            class_name)
            try:
                member_models = getattr(gallery_meta, 'member_models')
            except AttributeError:
                raise MemberModelsNotDefined(
                    '%s.GalleryMeta must define a list of member_models.' %
                    class_name)

            gallery_meta.gallery_class = cls
            cls._gallery_meta = gallery_meta

            membership_verbose_name = '%s Membership' % cls._meta.verbose_name
            custom_membership = getattr(gallery_meta, 'membership_class', None)

            if custom_membership:
                membership_class_name = '%sBaseMembership' % class_name
            else:
                membership_class_name = '%sMembership' % class_name

            module_name = cls.__module__
            membership_class = _create_membership_class(
                    class_name=membership_class_name,
                    verbose_name=membership_verbose_name,
                    app_label=cls._meta.app_label,
                    module_name=module_name,
                    member_models=member_models,
                    abstract=bool(custom_membership),
                    gallery_class=cls,
            )

            if custom_membership:
                cls.BaseMembership = membership_class
                module = importlib.import_module(module_name)

                class Descriptor(object):
                    def __get__(self, instance, owner):
                        return getattr(module, custom_membership)
                cls.Membership = Descriptor()
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
            return unicode(self.item)

        class Meta:
            ordering = ['sort_order']
            abstract = True

    class GalleryMeta:
        pass

    class Meta:
        abstract = True
