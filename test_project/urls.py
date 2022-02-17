from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView
from django.views.generic import ListView

import json
from ddm.models import Questionnaire
from ddm.views import DataUpload, QuestionnaireDisplay
class TestView(ListView):
    model = Questionnaire
    template_name = 'ddm/test.html'
    context_object_name = 'questionnaire_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'] = {
            'questionnaire_list': [
                {'pk': 1, 'name': 'q1', 'description': 'q1-descr'},
                {'pk': 2, 'name': 'q2', 'description': 'q1-descr'}
            ]
        }
        print(context)
        return context


urlpatterns = [
    path(r'admin/', admin.site.urls),
    path('', include('ddm.urls')),
    #path(r'vq/', TemplateView.as_view(template_name='ddm/test.html'), name='vq'),
    path(r'vq/', DataUpload.as_view()),
    path(r'quest/', QuestionnaireDisplay.as_view())
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
