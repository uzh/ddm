from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path(r'', RedirectView.as_view(pattern_name='ddm_projects:list'), name='ddm_landing'),
    path(r'studies/<slug:slug>/',
         include('ddm.participation.urls', namespace='ddm_participation')),
    path(r'projects/',
         include('ddm.projects.urls', namespace='ddm_projects')),
    path(r'projects/<slug:project_url_id>/questionnaire/',
         include('ddm.questionnaire.urls', namespace='ddm_questionnaire')),
    path(r'projects/<slug:project_url_id>/data-donation/',
         include('ddm.datadonation.urls', namespace='ddm_datadonation')),
    path(r'', include('ddm.logging.urls', namespace='ddm_logging')),
    path(r'', include('ddm.auth.urls', namespace='ddm_auth')),
    path(r'api/', include('ddm.apis.urls', namespace='ddm_apis')),
]
