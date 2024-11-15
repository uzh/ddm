from django.urls import path

from ddm.logging import views
from ddm.logging import apis


app_name = 'ddm_logging'
urlpatterns = [
    path(r'projects/<int:project_pk>/logs/', views.ProjectLogsView.as_view(), name='project_logs'),
    path(r'<int:pk>/exceptions/', apis.ExceptionAPI.as_view(), name='exceptions_api'),
]
