from django.views.generic import TemplateView
from .models import Portfolio, PhotoAlbum


class TestView(TemplateView):
    template_name = 'test/test.html'

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)
        context.update({
            'portfolio': Portfolio.objects.all()[0],
            'photo_album': PhotoAlbum.objects.all()[0],
        })
        return context
