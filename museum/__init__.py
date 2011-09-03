from .models import GalleryModel, ImageModel
from imagekit import processors
from imagekit.specs import ImageSpec


def create_image_model(*specs):
    class DynamicImageModel(ImageModel):
        class Meta:
            app_label = 'museum'
    
    DynamicImageModel._ik.specs = specs


def create_sizes_image_model(**kwargs):
    """Create an image model that exposes different sizes of the image. Argument
    keys are the names of properties to create on the image model and values are
    the corresponding sizes--tuples in the form (width, height).
    
    Example:
    image_model = create_sizes_image_model(thumbnail=(10, 10), full=(100, 100))
    
    """
    specs = []
    for name, size in kwargs.items():
        w, h = size

        class ResizeProcessor(processors.Resize):
            width = w
            height = h
        
        class Spec(ImageSpec): # TODO: Expose a way to set this base class.
            access_as = name
            processors = [ResizeProcessor]

        specs.append(Spec)

    return create_image_model(*specs)


def create_gallery_model(class_name):
    return 'GALLERY MODEL'


def create_membership_model(class_name, gallery_model, member_models):
    return 'MEMBERSHIP MODEL'


class GalleryBase(type):
    
    def __new__(cls, class_name, bases, attrs):
        if [b for b in bases if isinstance(b, GalleryBase)]:
            member_models = attrs.setdefault('member_models', [])
    
            # Create member models based on the info in extra_image_sizes
            if 'extra_image_sizes' in attrs:
                extra_image_sizes = attrs['extra_image_sizes']
                if extra_image_sizes:
                    image_model = create_sizes_image_model(**extra_image_sizes)
                    member_models.append(image_model)
                del attrs['extra_image_sizes']
        
            if not member_models:
                raise Exception('Your Gallery must declare member_models or extra_image_sizes.')
    
            gallery_model = attrs.setdefault('gallery_model',
                create_gallery_model('%sModel' % class_name))
    
            membership_model = attrs.setdefault('membership_model',
                create_membership_model('%sModelMembership' % class_name,
                    gallery_model, member_models))

        return type.__new__(cls, class_name, bases, attrs)


class Gallery(object):
    __metaclass__ = GalleryBase


def register_gallery(gallery_class):
    """Registers a gallery class. Normally you would autodiscover gallery
    classes, however there may be a situation where you want to omit galleries
    that would normally be autodiscovered. In that case, you can manually
    register each gallery (and not use autodiscover). This function is the
    single registration point for galleries, as it is used by autodiscover.
    
    """
    print 'Registering'
    print '\t%s' % gallery_class.gallery_model
    print '\t%s' % gallery_class.member_models
    print '\t%s' % gallery_class.membership_model


def autodiscover():
    import sys
    from django.conf import settings
    from django.utils.importlib import import_module
    import inspect

    for app in settings.INSTALLED_APPS:
        import_module(app)
        try:
            mod = import_module('%s.galleries' % app)
        except ImportError, err:
            # Only catch errors importing the module, not ImportErrors within
            # the imported module.
            try:
                sys.exc_traceback.tb_next.tb_next.tb_next
                raise err
            except AttributeError:
                continue

        for obj in [getattr(mod, p) for p in dir(mod)]:
            if inspect.isclass(obj) and obj is not Gallery and issubclass(obj, Gallery):
                register_gallery(obj)


autodiscover()
