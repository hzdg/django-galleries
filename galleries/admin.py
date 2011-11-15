# Thanks to Corey Oordt 
# http://opensource.washingtontimes.com/blog/2009/jan/12/generic-collections-django/
from django.contrib import admin
from .models import Gallery
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


class GenericCollectionInlineModelAdmin(admin.options.InlineModelAdmin):
    ct_field = "content_type"
    ct_fk_field = "object_id"
    
    def __init__(self, parent_model, admin_site):
        super(GenericCollectionInlineModelAdmin, self).__init__(parent_model, admin_site)
        ctypes = ContentType.objects.all().order_by('id').values_list('id', 'app_label','model')
        elements = ["%s: '%s/%s'" % (id, app_label, model) for id, app_label, model in ctypes]
        self.content_types = "{%s}" % ",".join(elements)
        
    def get_formset(self, request, obj=None):
        result = super(GenericCollectionInlineModelAdmin, self).get_formset(request, obj)
        result.content_types = self.content_types
        result.ct_fk_field = self.ct_fk_field
        return result


class GenericCollectionTabularInline(GenericCollectionInlineModelAdmin):
    template = 'galleries/admin/edit_inline/gen_coll_tabular.html'


# TODO: update template 
class GenericCollectionStackedInline(GenericCollectionInlineModelAdmin):
    template = 'galleries/admin/edit_inline/gen_coll_stacked.html'


class GalleryMembershipInline(GenericCollectionTabularInline):
    pass


def create_gallery_membership_inline(membership_class):
    return type('%sInline' % membership_class.__name__,
            (GalleryMembershipInline,), dict(model=membership_class))


class GalleryAdminBase(admin.ModelAdmin.__metaclass__):
    def __init__(cls, class_name, bases, attrs):
        if [b for b in bases if isinstance(b, GalleryAdminBase)]:
            if 'inlines' not in attrs:
                membership_inline = create_gallery_membership_inline(attrs['model'].Membership)
                cls.inlines = [membership_inline]
        return admin.ModelAdmin.__metaclass__.__init__(cls, class_name, bases, attrs)


class GalleryAdmin(admin.ModelAdmin):
    __metaclass__ = GalleryAdminBase

    class Media:
            js = [settings.STATIC_URL + 'galleries/js/genericcollection.js']


def register_gallery_admin(gallery_class, admin_class=None):
    """Registers an admin for a gallery. If none is provided, a GalleryAdmin
    will be created. Also registers admins for the member models, since those
    are required for the gallery admin to work.

    """
    if not admin_class:
        admin_class = type('GalleryAdmin', (GalleryAdmin,),
                dict(model=gallery_class))
    admin.site.register(gallery_class, admin_class)

    # Register the members
    for member in gallery_class._gallery_meta.member_models:
        try:
            admin.site.unregister(member)
        except admin.sites.NotRegistered:
            pass
        admin.site.register(member, type('GalleryMemberAdmin',
                (admin.ModelAdmin,), dict(model=member)))
