from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skill_level = models.FloatField(default=0.5)  # 0.0 to 1.0
    total_questions_answered = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Skill Level: {self.skill_level:.2f}"

    def update_skill_level(self, is_correct):
        self.total_questions_answered += 1
        if is_correct:
            self.correct_answers += 1
            # Increase skill level for correct answers
            self.skill_level = min(1.0, self.skill_level + 0.05)
        else:
            # Decrease skill level for incorrect answers
            self.skill_level = max(0.0, self.skill_level - 0.03)
        self.save()


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    difficulty_level = models.FloatField(default=0.5)  # 0.0 to 1.0
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty_level = models.FloatField(default=0.5)  # 0.0 to 1.0
    correct_answer = models.TextField()
    options = models.JSONField(null=True, blank=True)  # For multiple choice
    explanation = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question_text[:50]}..."

    def check_answer(self, user_answer):
        return user_answer.strip().lower() == self.correct_answer.strip().lower()


class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.TextField()
    is_correct = models.BooleanField()
    response_time = models.FloatField()  # Time taken in seconds
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question.question_text[:30]}... - {'Correct' if self.is_correct else 'Incorrect'}"

    class Meta:
        ordering = ['-timestamp']


class QuizSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {'Completed' if self.is_completed else 'In Progress'}"

    def calculate_score(self):
        responses = UserResponse.objects.filter(
            user=self.user,
            question__quiz=self.quiz,
            timestamp__gte=self.start_time
        )
        self.total_questions = responses.count()
        self.score = responses.filter(is_correct=True).count()
        self.save()
        return self.score
