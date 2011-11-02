from .models import Portfolio, PhotoAlbum
from galleries.admin import register_gallery_admin


register_gallery_admin(Portfolio)
register_gallery_admin(PhotoAlbum)
