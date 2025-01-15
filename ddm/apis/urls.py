from django.urls import path

from ddm.participation.apis import DeleteParticipantAPI
from ddm.projects.apis import DeleteProjectData
from ddm.apis import views


app_name = 'ddm_apis'
urlpatterns = [
    path('project/<slug:project_url_id>/overview', views.ProjectDetailApiView.as_view(), name='project_overview'),
    path('project/<slug:project_url_id>/donations', views.ProjectDonationsListView.as_view(), name='donations'),
    path('project/<slug:project_url_id>/data/delete', DeleteProjectData.as_view(), name='project_data_delete'),
    path('project/<slug:project_url_id>/responses', views.ResponsesApiView.as_view(), name='responses'),
    path('project/<slug:project_url_id>/participant/<slug:participant_id>/delete', DeleteParticipantAPI.as_view(), name='participant_delete')
]
