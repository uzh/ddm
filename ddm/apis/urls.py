from django.urls import path

from ddm.apis import views


app_name = 'ddm_apis'
urlpatterns = [
    path(
        'project/<slug:project_url_id>/overview',
        views.ProjectDetailApiView.as_view(),
        name='project_overview'
    ),
    path(
        'project/<slug:project_url_id>/donations',
        views.ProjectDonationsListView.as_view(),
        name='donations'
    ),
    path(
        'project/<slug:project_url_id>/details/download',
        views.DownloadProjectDetailsView.as_view(),
        name='download_project_details'
    ),
    path(
        'project/<slug:project_url_id>/data/delete',
        views.DeleteProjectData.as_view(),
        name='project_data_delete'
    ),
    path(
        'project/<slug:project_url_id>/responses',
        views.ResponsesApiView.as_view(),
        name='responses'
    ),
    path(
        'project/<slug:project_url_id>/participant/<slug:participant_id>/delete',
        views.DeleteParticipantAPI.as_view(),
        name='participant_delete'
    ),
]
