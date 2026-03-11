from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import UserProfile, Quiz, Question, UserResponse, QuizSession
from .serializers import (
    UserProfileSerializer, QuizSerializer, QuestionSerializer, 
    UserResponseSerializer, QuizSessionSerializer, AdaptiveQuestionRequestSerializer,
    AnswerSubmissionSerializer
)
from .ai_service import AIQuestionService


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quiz.objects.filter(is_active=True)
    serializer_class = QuizSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['post'])
    def start_session(self, request, pk=None):
        quiz = self.get_object()
        
        # Get or create user profile
        user_profile, created = UserProfile.objects.get_or_create(
            user=request.user if request.user.is_authenticated else User.objects.get(username='anonymous')
        )
        
        # Create new quiz session
        session = QuizSession.objects.create(
            user=request.user if request.user.is_authenticated else User.objects.get(username='anonymous'),
            quiz=quiz
        )
        
        serializer = QuizSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def adaptive_question(self, request, pk=None):
        quiz = self.get_object()
        
        # Get user skill level
        if request.user.is_authenticated:
            user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
            skill_level = user_profile.skill_level
        else:
            skill_level = 0.5  # Default for anonymous users
        
        # Get excluded question IDs
        exclude_ids = request.query_params.getlist('exclude_ids', [])
        exclude_ids = [int(id) for id in exclude_ids if id.isdigit()]
        
        # Find appropriate question based on skill level
        question = self._get_adaptive_question(quiz, skill_level, exclude_ids)
        
        if not question:
            return Response(
                {"message": "No more questions available"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = QuestionSerializer(question)
        return Response(serializer.data)

    def _get_adaptive_question(self, quiz, skill_level, exclude_ids):
        questions = quiz.questions.filter(is_active=True).exclude(id__in=exclude_ids)
        
        if not questions.exists():
            return None
        
        # Find question closest to user's skill level
        closest_question = None
        smallest_diff = float('inf')
        
        for question in questions:
            diff = abs(question.difficulty_level - skill_level)
            if diff < smallest_diff:
                smallest_diff = diff
                closest_question = question
        
        return closest_question


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.filter(is_active=True)
    serializer_class = QuestionSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        question = self.get_object()
        serializer = AnswerSubmissionSerializer(data=request.data)
        
        if serializer.is_valid():
            user_answer = serializer.validated_data['user_answer']
            response_time = serializer.validated_data['response_time']
            
            # Create user response
            user_response = UserResponse.objects.create(
                user=request.user if request.user.is_authenticated else User.objects.get(username='anonymous'),
                question=question,
                user_answer=user_answer,
                response_time=response_time,
                is_correct=question.check_answer(user_answer)
            )
            
            # Return response with feedback
            response_data = {
                'is_correct': user_response.is_correct,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'user_response_id': user_response.id
            }
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizSessionViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuizSession.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        session = self.get_object()
        session.end_time = timezone.now()
        session.is_completed = True
        session.calculate_score()
        
        serializer = QuizSessionSerializer(session)
        return Response(serializer.data)


class AdaptiveQuizView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = AdaptiveQuestionRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            quiz_id = serializer.validated_data['quiz_id']
            user_skill_level = serializer.validated_data['user_skill_level']
            exclude_ids = serializer.validated_data['exclude_question_ids']
            
            quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
            
            # Try to generate question using AI service first
            ai_service = AIQuestionService()
            try:
                ai_question = ai_service.generate_adaptive_question(
                    user_skill_level=user_skill_level,
                    quiz_category=quiz.category,
                    excluded_topics=[]
                )
                
                if ai_question:
                    # Create a temporary question object for serialization
                    temp_question = {
                        'id': None,  # Will be generated when saved
                        'question_text': ai_question['question_text'],
                        'question_type': ai_question['question_type'],
                        'difficulty_level': ai_question['difficulty_level'],
                        'options': ai_question.get('options'),
                        'explanation': ai_question.get('explanation'),
                        'is_active': True,
                        'source': ai_question.get('source', 'ai_service')
                    }
                    
                    return Response(temp_question)
                    
            except Exception as e:
                print(f"⚠️ AI question generation failed: {e}")
            
            # Fallback to database questions
            question = self._get_adaptive_question(quiz, user_skill_level, exclude_ids)
            
            if not question:
                return Response(
                    {"message": "No more questions available"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = QuestionSerializer(question)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_adaptive_question(self, quiz, skill_level, exclude_ids):
        questions = quiz.questions.filter(is_active=True).exclude(id__in=exclude_ids)
        
        if not questions.exists():
            return None
        
        # Find question closest to user's skill level
        closest_question = None
        smallest_diff = float('inf')
        
        for question in questions:
            diff = abs(question.difficulty_level - skill_level)
            if diff < smallest_diff:
                smallest_diff = diff
                closest_question = question
        
        return closest_question


class GenerateAIQuestionView(APIView):
    """
    Dedicated endpoint for AI-generated questions using Google Gemini
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            ai_service = AIQuestionService()
            
            # Get parameters from request
            user_skill_level = request.data.get('user_skill_level', 0.5)
            topic = request.data.get('topic', None)
            quiz_category = request.data.get('quiz_category', 'Aviation')
            
            # Generate AI question
            ai_question = ai_service.generate_adaptive_question(
                user_skill_level=user_skill_level,
                quiz_category=quiz_category,
                excluded_topics=[]
            )
            
            if ai_question:
                return Response({
                    'success': True,
                    'question': ai_question,
                    'message': 'Question generated successfully using Google Gemini'
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to generate question'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error generating question: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Get recent responses
        recent_responses = UserResponse.objects.filter(
            user=request.user
        ).order_by('-timestamp')[:10]
        
        # Get quiz sessions
        sessions = QuizSession.objects.filter(
            user=request.user,
            is_completed=True
        ).order_by('-start_time')[:5]
        
        data = {
            'user_profile': UserProfileSerializer(user_profile).data,
            'recent_responses': UserResponseSerializer(recent_responses, many=True).data,
            'recent_sessions': QuizSessionSerializer(sessions, many=True).data,
        }
        
        return Response(data)


class CreateSampleDataView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Create sample quiz
        quiz, created = Quiz.objects.get_or_create(
            title="Flight Dispatcher Fundamentals",
            defaults={
                'description': 'Test your knowledge of flight dispatcher operations and procedures',
                'category': 'Aviation',
                'difficulty_level': 0.5
            }
        )
        
        if created:
            # Create sample questions
            questions_data = [
                {
                    'question_text': 'What is the primary responsibility of a flight dispatcher?',
                    'question_type': 'multiple_choice',
                    'difficulty_level': 0.3,
                    'correct_answer': 'A',
                    'options': ['A. Ensure safe and efficient flight operations', 'B. Pilot the aircraft', 'C. Handle passenger check-in', 'D. Manage airport security'],
                    'explanation': 'Flight dispatchers are responsible for planning, monitoring, and assisting in flight operations to ensure safety and efficiency.'
                },
                {
                    'question_text': 'True or False: A flight dispatcher must have the same level of knowledge as a pilot regarding aircraft performance.',
                    'question_type': 'true_false',
                    'difficulty_level': 0.5,
                    'correct_answer': 'True',
                    'explanation': 'Flight dispatchers must have comprehensive knowledge equivalent to pilots regarding aircraft performance, navigation, and regulations.'
                },
                {
                    'question_text': 'What weather information is most critical for flight planning?',
                    'question_type': 'short_answer',
                    'difficulty_level': 0.7,
                    'correct_answer': 'wind',
                    'explanation': 'Wind conditions at various altitudes are critical for flight planning, affecting fuel consumption, flight time, and route selection.'
                }
            ]
            
            for q_data in questions_data:
                Question.objects.create(quiz=quiz, **q_data)
        
        return Response({
            'message': 'Sample data created successfully',
            'quiz_id': quiz.id,
            'question_count': quiz.questions.count()
        })
