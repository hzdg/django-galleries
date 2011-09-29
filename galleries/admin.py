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


def create_gallery_membership_inline(membership_class):
    class GalleryMembershipInline(GenericCollectionTabularInline):
        model = membership_class
    return GalleryMembershipInline


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


# Admins are automatically registered for all Gallery subclasses and member
# models. If you want to provide a custom admin, you can unregister these and
# then register your own.
for subclass in Gallery.__subclasses__():
    class SubclassGalleryAdmin(GalleryAdmin):
        model = subclass
    for member_model in subclass._gallery_meta.member_models:
        class MemberModelAdmin(admin.ModelAdmin):
            model = member_model
        admin.site.register(member_model, MemberModelAdmin)
    admin.site.register(subclass, SubclassGalleryAdmin)
