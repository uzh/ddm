from django.urls import path, include
from django.views.generic import RedirectView

from ddm.datadonation.apis import DonationsAPI
from ddm.participation.apis import DeleteParticipantAPI
from ddm.projects.apis import ProjectDataAPI, DeleteProjectData
from ddm.questionnaire.apis import ResponsesAPI


api_patterns = (
    [
        path('project/<slug:project_url_id>/data', ProjectDataAPI.as_view(), name='project_data'),
        path('project/<slug:project_url_id>/data/delete', DeleteProjectData.as_view(), name='project_data_delete'),
        path('project/<slug:project_url_id>/donations', DonationsAPI.as_view(), name='donations'),
        path('project/<slug:project_url_id>/responses', ResponsesAPI.as_view(), name='responses'),
        path('project/<slug:project_url_id>/participant/<slug:participant_id>/delete', DeleteParticipantAPI.as_view(), name='participant_delete')
    ],
    'ddm_apis'
)

urlpatterns = [
    path(r'', RedirectView.as_view(pattern_name='ddm_projects:list'), name='ddm_landing'),
    path(r'studies/<slug:slug>/', include('ddm.participation.urls', namespace='ddm_participation')),
    path(r'projects/', include('ddm.projects.urls', namespace='ddm_projects')),
    path(r'projects/<slug:project_url_id>/questionnaire/', include('ddm.questionnaire.urls', namespace='ddm_questionnaire')),
    path(r'projects/<slug:project_url_id>/data-donation/', include('ddm.datadonation.urls', namespace='ddm_datadonation')),
    path(r'', include('ddm.logging.urls', namespace='ddm_logging')),
    path(r'', include('ddm.auth.urls', namespace='ddm_auth')),
    path(r'api/', include(api_patterns))
]
