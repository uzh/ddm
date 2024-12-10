from django.urls import path

from ddm.logging import views
from ddm.logging import apis


app_name = 'ddm_logging'
urlpatterns = [
    path(r'projects/<slug:project_url_id>/logs/', views.ProjectLogsView.as_view(), name='project_logs'),
    path(r'<slug:project_url_id>/exceptions/', apis.ExceptionAPI.as_view(), name='exceptions_api'),
]
