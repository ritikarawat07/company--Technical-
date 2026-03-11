from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet, QuizViewSet, QuestionViewSet, QuizSessionViewSet,
    AdaptiveQuizView, UserStatsView, CreateSampleDataView, GenerateAIQuestionView
)

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='userprofile')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'sessions', QuizSessionViewSet, basename='quizsession')

urlpatterns = [
    path('', include(router.urls)),
    path('adaptive/', AdaptiveQuizView.as_view(), name='adaptive-quiz'),
    path('generate-ai-question/', GenerateAIQuestionView.as_view(), name='generate-ai-question'),
    path('stats/', UserStatsView.as_view(), name='user-stats'),
    path('create-sample-data/', CreateSampleDataView.as_view(), name='create-sample-data'),
]
