from django.urls import path

from ddm.projects import views
from ddm.projects.transfer import views as transfer_views

app_name = "ddm_projects"
urlpatterns = [
    path(r"", views.ProjectList.as_view(), name="list"),
    path(r"create/", views.ProjectCreate.as_view(), name="create"),
    path(r"import/", transfer_views.ProjectImportView.as_view(), name="import"),
    path(r"<slug:project_url_id>/", views.ProjectDetail.as_view(), name="detail"),
    path(
        r"<slug:project_url_id>/export/",
        transfer_views.ProjectExportView.as_view(),
        name="export",
    ),
    path(
        r"<slug:project_url_id>/copy/",
        transfer_views.ProjectCopyView.as_view(),
        name="copy",
    ),
    # Project settings
    path(
        r"<slug:project_url_id>/edit/public-information",
        views.ProjectEditPublicInformation.as_view(),
        name="edit_public_information",
    ),
    path(
        r"<slug:project_url_id>/edit/url-parameter",
        views.ProjectEditUrlParameter.as_view(),
        name="edit_url_parameter",
    ),
    path(
        r"<slug:project_url_id>/edit/redirect",
        views.ProjectEditRedirectConfiguration.as_view(),
        name="edit_redirect_configuration",
    ),
    path(
        r"<slug:project_url_id>/edit/branding",
        views.ProjectEditBranding.as_view(),
        name="edit_branding",
    ),
    path(
        r"<slug:project_url_id>/delete/", views.ProjectDelete.as_view(), name="delete"
    ),
    path(
        r"<slug:project_url_id>/briefing/",
        views.BriefingEdit.as_view(),
        name="briefing_edit",
    ),
    path(
        r"<slug:project_url_id>/debriefing/",
        views.DebriefingEdit.as_view(),
        name="debriefing_edit",
    ),
    path(
        r"<slug:project_url_id>/edit-translations/",
        views.ProjectEditCustomUploaderTranslations.as_view(),
        name="edit_translations",
    ),
]
