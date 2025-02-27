from django.urls import path

from ddm.auth import views


app_name = 'ddm_auth'
urlpatterns = [
    path(r'projects/<slug:project_url_id>/token/', views.ProjectTokenView.as_view(), name='project_token'),
    path(r'auth/no-permission/', views.DdmNoPermissionView.as_view(), name='no_permission'),
]
