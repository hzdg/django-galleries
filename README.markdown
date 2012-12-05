Django-Galleries
======================

This is a base class to bring in galleries to sites. Currently supports photos
and embedded videos. This app mostly has abstract models for you to use and
append too for custom thumbnail sizes, photo-sizes.


Example:
------------------------------

```py
# models.py
from galleries.models import Gallery, EmbedModel, ImageModel
from imagekit.models import ImageSpec
from imagekit.processors import Crop

class YouTubeVideo(EmbedModel):
    thumbnail = models.ProcessedImageField([Crop(60, 60)],
                                            upload_to='gallery_posters')

class Photo(ImageModel)
    thumbnail = models.ImageSpec([Crop(60, 60)], image_field='original_image')


class ApartmentGallery(Gallery):

    class GalleryMeta:
        member_models = [Photo, YouTubeVideo]


# admin.py
from .models import ApartmentGallery
from galleries.admin import register_gallery_admin

register_gallery_admin(ApartmentGallery)


# settings.py
INSTALLED_APPS = (
    'imagekit',
    ...
)
```

This should register you new app with our galleries models and include the
thumbnail preview.
