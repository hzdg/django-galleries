======================
Django-Galleries
======================

A set of utilities for creating gallery models and admin classes.


------------------------------
Example:
------------------------------


models.py
=========

Define models for all of the types you want to put in your gallery, then create
a ``Gallery`` subclass that specifies which models to allow for its members.

.. attention::

    In older versions, we recommended that you extend django-gallery's included
    ``ImageModel`` or ``EmbedModel`` classes if your gallery contained those
    types. Those models are now deprecated. Just define your own!

.. code:: python

    from galleries.models import Gallery
    from imagekit.models import ImageSpec
    from imagekit.processors import Crop


    class YouTubeVideo(models.Model):
        title = models.CharField(max_length=50)
        embed_code = models.TextField()
        thumbnail = models.ProcessedImageField([Crop(60, 60)],
                                                upload_to='gallery_posters')

    class Photo(models.Model)
        title = models.CharField(max_length=50)
        description = models.CharField(max_length=255, blank=True)
        original_image = models.ImageField(upload_to='galleries')
        thumbnail = models.ImageSpec([Crop(60, 60)], image_field='original_image')


    class ApartmentGallery(Gallery):

        class GalleryMeta:
            member_models = [Photo, YouTubeVideo]

The gallery class will automatically create a membership (through) model, which
will be accessible at ``ApartmentGallery.Membership``.


admin.py
========

.. code:: python

    from .models import ApartmentGallery
    from galleries.admin import register_gallery_admin

    register_gallery_admin(ApartmentGallery)


settings.py
===========

.. code:: python

    INSTALLED_APPS = (
        'imagekit',
        ...
    )

This should register you new app with our galleries models and include the
thumbnail preview.
