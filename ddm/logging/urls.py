from django.urls import path

from ddm.logging import views
from ddm.logging.api.views import EventLogAPIView, ExceptionAPI, ExceptionLogAPIView

app_name = "ddm_logging"
urlpatterns = [
    path(
        "projects/<slug:project_url_id>/logs/events",
        views.EventLogsListView.as_view(),
        name="project_event_logs",
    ),
    path(
        "projects/<slug:project_url_id>/logs/exceptions",
        views.ExceptionLogsListView.as_view(),
        name="project_exception_logs",
    ),
    path(
        "<slug:project_url_id>/api/exceptions/",
        ExceptionAPI.as_view(),
        name="exceptions_api",
    ),
    path(
        "projects/<str:project_url_id>/logs/api/events/",
        EventLogAPIView.as_view(),
        name="event_logs_api",
    ),
    path(
        "projects/<str:project_url_id>/logs/api/exceptions/",
        ExceptionLogAPIView.as_view(),
        name="exception_logs_api",
    ),
]
