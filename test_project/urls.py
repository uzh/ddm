from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView


class VueView(TemplateView):
    """View that is integrated into the admin panel.
    """
    template_name = 'ddm/questionnaire.html'


urlpatterns = [
    path(r'admin/', admin.site.urls),
    path('', include('ddm.urls')),
    path('vq', VueView.as_view(), name='vq'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
