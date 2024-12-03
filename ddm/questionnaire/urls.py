from django.urls import path

from ddm.questionnaire import views


app_name = 'ddm_questionnaire'
urlpatterns = [
    path(r'', views.QuestionnaireOverview.as_view(), name='overview'),
    path(r'<slug:question_type>/create/', views.QuestionCreate.as_view(), name='create'),
    path(r'<slug:question_type>/<int:pk>/edit/', views.QuestionEdit.as_view(), name='edit'),
    path(r'<slug:question_type>/<int:pk>/delete/', views.QuestionDelete.as_view(), name='delete'),
    path(r'<slug:question_type>/<int:pk>/items/', views.ItemEdit.as_view(), name='items'),
    path(r'<slug:question_type>/<int:pk>/scale/', views.ScaleEdit.as_view(), name='scale'),
]
