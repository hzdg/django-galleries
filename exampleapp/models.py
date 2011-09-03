from galleries.models import Gallery


class PhotoAlbum(Gallery):
    class GalleryOptions:
        extra_image_sizes = {
            'thumbnail': (10, 10),
            'full': (100, 100),
        }
    class Meta:
        verbose_name = 'Photo Album'