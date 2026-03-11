from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Quiz, Question, UserResponse, QuizSession


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    accuracy_percentage = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['user', 'skill_level', 'total_questions_answered', 'correct_answers', 
                  'accuracy_percentage', 'created_at', 'updated_at']

    def get_accuracy_percentage(self, obj):
        if obj.total_questions_answered == 0:
            return 0
        return round((obj.correct_answers / obj.total_questions_answered) * 100, 2)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'difficulty_level', 
                  'options', 'explanation', 'is_active']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Don't include correct_answer in the response
        return data


class QuestionDetailSerializer(QuestionSerializer):
    correct_answer = serializers.CharField(read_only=True)

    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ['correct_answer']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'category', 'difficulty_level', 
                  'is_active', 'questions', 'question_count', 'created_at']

    def get_question_count(self, obj):
        return obj.questions.filter(is_active=True).count()


class UserResponseSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserResponse
        fields = ['id', 'user', 'question', 'user_answer', 'is_correct', 
                  'response_time', 'timestamp']

    def create(self, validated_data):
        question = validated_data['question']
        user_answer = validated_data['user_answer']
        
        # Check if the answer is correct
        is_correct = question.check_answer(user_answer)
        validated_data['is_correct'] = is_correct
        
        # Create the response
        response = super().create(validated_data)
        
        # Update user's skill level
        user_profile, created = UserProfile.objects.get_or_create(
            user=validated_data['user']
        )
        user_profile.update_skill_level(is_correct)
        
        return response


class QuizSessionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    quiz = QuizSerializer(read_only=True)
    score_percentage = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = QuizSession
        fields = ['id', 'user', 'quiz', 'start_time', 'end_time', 'score', 
                  'total_questions', 'score_percentage', 'duration', 'is_completed']

    def get_score_percentage(self, obj):
        if obj.total_questions == 0:
            return 0
        return round((obj.score / obj.total_questions) * 100, 2)

    def get_duration(self, obj):
        if obj.end_time and obj.start_time:
            duration = obj.end_time - obj.start_time
            return str(duration).split('.')[0]  # Remove microseconds
        return "In Progress"


class AdaptiveQuestionRequestSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    user_skill_level = serializers.FloatField(min_value=0.0, max_value=1.0)
    exclude_question_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[]
    )


class AnswerSubmissionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    user_answer = serializers.CharField()
    response_time = serializers.FloatField(min_value=0.0)
