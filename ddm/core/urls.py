from django.urls import path, include
from django.views.generic import RedirectView

from ddm.datadonation.apis import DonationsAPI
from ddm.participation.apis import DeleteParticipantAPI
from ddm.projects.apis import ProjectDataAPI, DeleteProjectData
from ddm.questionnaire.apis import ResponsesAPI


api_patterns = (
    [
        path('project/<int:pk>/data', ProjectDataAPI.as_view(), name='project_data'),
        path('project/<int:pk>/data/delete', DeleteProjectData.as_view(), name='project_data_delete'),
        path('project/<int:pk>/donations', DonationsAPI.as_view(), name='donations'),
        path('project/<int:pk>/responses', ResponsesAPI.as_view(), name='responses'),
        path('project/<int:pk>/participant/<slug:participant_id>/delete', DeleteParticipantAPI.as_view(), name='participant_delete')
    ],
    'ddm_apis'
)

urlpatterns = [
    path(r'', RedirectView.as_view(pattern_name='ddm_projects:list'), name='ddm_landing'),
    path(r'studies/<slug:slug>/', include('ddm.participation.urls', namespace='participation')),
    path(r'projects/', include('ddm.projects.urls', namespace='ddm_projects')),
    path(r'projects/<int:project_pk>/questionnaire/', include('ddm.questionnaire.urls', namespace='questionnaire')),
    path(r'projects/<int:project_pk>/data-donation/', include('ddm.datadonation.urls', namespace='datadonation')),
    path(r'', include('ddm.logging.urls', namespace='ddm_logs')),
    path(r'', include('ddm.auth.urls', namespace='ddm_auth')),
    path(r'api/', include(api_patterns))
]
