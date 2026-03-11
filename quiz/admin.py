from django.contrib import admin
from .models import UserProfile, Quiz, Question, UserResponse, QuizSession


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill_level', 'total_questions_answered', 'correct_answers', 'updated_at']
    list_filter = ['skill_level', 'created_at']
    search_fields = ['user__username']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty_level', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'difficulty_level']
    search_fields = ['title', 'description']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'quiz', 'question_type', 'difficulty_level', 'is_active']
    list_filter = ['question_type', 'difficulty_level', 'is_active', 'quiz']
    search_fields = ['question_text', 'quiz__title']


@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'is_correct', 'response_time', 'timestamp']
    list_filter = ['is_correct', 'timestamp', 'question__quiz']
    search_fields = ['user__username', 'question__question_text']


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'total_questions', 'is_completed', 'start_time']
    list_filter = ['is_completed', 'start_time', 'quiz']
    search_fields = ['user__username', 'quiz__title']
