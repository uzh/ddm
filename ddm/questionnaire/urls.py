from django.urls import path

from ddm.questionnaire import views

app_name = "ddm_questionnaire"
urlpatterns = [
    path(r"", views.QuestionnaireOverview.as_view(), name="overview"),
    path(
        r"<slug:question_type>/create/", views.QuestionCreate.as_view(), name="create"
    ),
    path(
        r"<slug:question_type>/<int:pk>/edit/",
        views.QuestionEdit.as_view(),
        name="edit",
    ),
    path(
        r"<slug:question_type>/<int:pk>/delete/",
        views.QuestionDelete.as_view(),
        name="delete",
    ),
    path(
        r"<slug:question_type>/<int:pk>/filters/",
        views.FilterEditQuestion.as_view(),
        name="question_filters",
    ),
    path(
        r"<slug:question_type>/<int:question_pk>/item/<int:pk>/filters/",
        views.FilterEditItems.as_view(),
        name="item_filters",
    ),
]
