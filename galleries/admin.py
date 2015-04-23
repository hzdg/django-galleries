"""
Thanks to Corey Oordt
    http://opensource.washingtontimes.com/
    blog/2009/jan/12/generic-collections-django/

"""
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from imagekit.admin import AdminThumbnail


class GenericCollectionInlineModelAdmin(admin.options.InlineModelAdmin):
    ct_field = "content_type"
    ct_fk_field = "object_id"

    def __init__(self, parent_model, admin_site):
        super(GenericCollectionInlineModelAdmin, self).__init__(parent_model,
                                                                admin_site)
        ctypes = ContentType.objects.all(
                    ).order_by('id').values_list('id', 'app_label', 'model')

        elements = ["%s: '%s/%s'" % (id, app_label, model) for id, app_label,
                    model in ctypes]
        self.content_types = "{%s}" % ",".join(elements)

    def get_formset(self, request, obj=None, **kwargs):
        result = super(GenericCollectionInlineModelAdmin, self
                      ).get_formset(request, obj=obj, **kwargs)

        result.content_types = self.content_types
        result.ct_fk_field = self.ct_fk_field
        result.ct_field = self.ct_field
        return result


class GenericCollectionTabularInline(GenericCollectionInlineModelAdmin):
    template = 'galleries/admin/edit_inline/gen_coll_tabular.html'


class GenericCollectionStackedInline(GenericCollectionInlineModelAdmin):
    template = 'galleries/admin/edit_inline/gen_coll_stacked.html'


class GalleryMembershipInline(GenericCollectionTabularInline):
    readonly_fields = ['thumbnail']
    list_editable = ('sort_order', )

    admin_thumbnail = AdminThumbnail('thumbnail')

    def thumbnail(self, obj):
        return self.admin_thumbnail(obj.item) if obj.item else ''


def create_gallery_membership_inline(membership_class):
    return type('%sInline' % membership_class.__name__,
            (GalleryMembershipInline,), dict(model=membership_class))


class GalleryAdminBase(type(admin.ModelAdmin)):
    def __init__(cls, class_name, bases, attrs):
        if [b for b in bases if isinstance(b, GalleryAdminBase)]:
            if 'inlines' not in attrs:
                membership_inline = create_gallery_membership_inline(
                    attrs['model'].Membership)

                cls.inlines = [membership_inline]
        return type(admin.ModelAdmin).__init__(cls, class_name, bases,
                                                       attrs)


class GalleryAdmin(admin.ModelAdmin):
    __metaclass__ = GalleryAdminBase

    class Media:
            js = [settings.STATIC_URL + 'galleries/js/genericcollection.js',
            'https://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js',
            ('https://ajax.googleapis.com/'
             'ajax/libs/jqueryui/1.8.10/jquery-ui.min.js'),
            settings.STATIC_URL + 'galleries/js/admin-list-reorder.js', ]


class MemberModelAdmin(admin.ModelAdmin):
    admin_thumbnail = AdminThumbnail(image_field='thumbnail')
    list_display = ('__unicode__', 'admin_thumbnail', )


def register_gallery_admin(gallery_class, admin_class=GalleryAdmin,
                           member_class=MemberModelAdmin):
    """
    Registers an admin for a gallery. If none is provided, a GalleryAdmin
    will be created. Also registers admins for the member models, since those
    are required for the gallery admin to work.
    """

    admin_class = type('GalleryAdmin', (admin_class,),
            dict(model=gallery_class))

    admin.site.register(gallery_class, admin_class)

    # Register the members
    for member in gallery_class._gallery_meta.member_models:

        try:
            admin.site.unregister(member)
        except admin.sites.NotRegistered:
            pass

        admin.site.register(member, type('GalleryMemberAdmin',
                (member_class,), dict(model=member)))
