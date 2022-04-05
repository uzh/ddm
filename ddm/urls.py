from django.urls import path, include

from ddm.views import research_interface
from ddm.views import (
    DataUpload, ProjectEntry, QuestionnaireDisplay, ProjectExit
)


participation_patterns = [
    path(r'intro/', ProjectEntry.as_view(), name='project-entry'),
    path(r'data-donation/', DataUpload.as_view(), name='data-donation'),
    path(r'questionnaire/', QuestionnaireDisplay.as_view(), name='questionnaire'),
    path(r'end/', ProjectExit.as_view(), name='project-exit')
]

researcher_patterns = [
    path(r'projects/', research_interface.ProjectList.as_view(), name='project-list'),
    path(r'projects/create', research_interface.ProjectCreate.as_view(), name='project-create'),
    path(r'projects/<int:pk>', research_interface.ProjectDetail.as_view(), name='project-detail'),
    path(r'projects/<int:pk>/edit', research_interface.ProjectEdit.as_view(), name='project-edit'),
    path(r'projects/<int:pk>/delete', research_interface.ProjectDelete.as_view(), name='project-delete')
]

urlpatterns = [
    path(r'<slug:slug>/', include(participation_patterns)),
    path(r'', include(researcher_patterns))
]
