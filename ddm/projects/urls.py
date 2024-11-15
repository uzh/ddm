from django.urls import path

from ddm.projects import views


app_name = 'ddm_projects'
urlpatterns = [
    path(r'', views.ProjectList.as_view(), name='list'),
    path(r'create/', views.ProjectCreate.as_view(), name='create'),
    path(r'<int:pk>/', views.ProjectDetail.as_view(), name='detail'),
    path(r'<int:pk>/edit/', views.ProjectEdit.as_view(), name='edit'),
    path(r'<int:pk>/delete/', views.ProjectDelete.as_view(), name='delete'),
    path(r'<int:pk>/briefing/', views.BriefingEdit.as_view(), name='briefing_edit'),
    path(r'<int:pk>/debriefing/', views.DebriefingEdit.as_view(), name='debriefing_edit'),
]
