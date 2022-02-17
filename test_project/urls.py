from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from ddm.views import (
    DataUpload, ProjectEntry, QuestionnaireDisplay, ProjectExit
)

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path('', include('ddm.urls')),
    path(r'<slug:slug>/intro/', ProjectEntry.as_view(), name='project-entry'), # TODO: Move this to the DDM module.
    path(r'<slug:slug>/data-donation/', DataUpload.as_view(), name='data-donation'),  # TODO: Move this to the DDM module.
    path(r'<slug:slug>/questionnaire/', QuestionnaireDisplay.as_view(), name='questionnaire'),  # TODO: Move this to the DDM module.
    path(r'<slug:slug>/end/', ProjectExit.as_view(), name='project-exit'),  # TODO: Move this to the DDM module.
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
