#!/usr/bin/env python
"""
Test script to verify Google Gemini API integration
"""

import os
import sys
import django

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quiz_system.settings')
django.setup()

from quiz.ai_service import AIQuestionService

def test_gemini_integration():
    """Test the Gemini API integration"""
    print("🧪 Testing Google Gemini API Integration...")
    print("=" * 50)
    
    # Initialize AI service
    ai_service = AIQuestionService()
    
    # Check if Gemini is available
    if ai_service.gemini_model:
        print("✅ Gemini API is initialized and ready!")
        
        # Test question generation
        print("\n📝 Testing question generation...")
        try:
            question = ai_service.generate_adaptive_question(
                user_skill_level=0.5,
                quiz_category="Aviation",
                excluded_topics=[]
            )
            
            if question:
                print("✅ Question generated successfully!")
                print(f"📋 Question: {question.get('question_text', 'N/A')}")
                print(f"🎯 Topic: {question.get('topic', 'N/A')}")
                print(f"📊 Difficulty: {question.get('difficulty_level', 'N/A')}")
                print(f"🔍 Source: {question.get('source', 'N/A')}")
                return True
            else:
                print("❌ Failed to generate question")
                return False
                
        except Exception as e:
            print(f"❌ Error generating question: {e}")
            return False
    else:
        print("❌ Gemini API is not initialized")
        print("\n🔧 To set up Gemini API:")
        print("1. Get an API key from: https://makersuite.google.com/app/apikey")
        print("2. Set environment variable: export GEMINI_API_KEY=your_key_here")
        print("3. Or create a .env file with GEMINI_API_KEY=your_key_here")
        return False

def test_static_fallback():
    """Test static question fallback"""
    print("\n🔄 Testing static question fallback...")
    
    # Temporarily disable Gemini
    ai_service = AIQuestionService()
    original_model = ai_service.gemini_model
    ai_service.gemini_model = None
    
    try:
        question = ai_service.generate_adaptive_question(
            user_skill_level=0.5,
            quiz_category="Aviation",
            excluded_topics=[]
        )
        
        if question:
            print("✅ Static fallback question generated successfully!")
            print(f"📋 Question: {question.get('question_text', 'N/A')}")
            return True
        else:
            print("❌ Failed to generate static fallback question")
            return False
            
    except Exception as e:
        print(f"❌ Error with static fallback: {e}")
        return False
    finally:
        # Restore original model
        ai_service.gemini_model = original_model

if __name__ == "__main__":
    print("🚀 AI Adaptive Flight Dispatcher Quiz - Gemini API Test")
    print("=" * 60)
    
    # Test environment variables
    gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if gemini_key:
        print(f"✅ API key found: {gemini_key[:10]}...{gemini_key[-4:]}")
    else:
        print("⚠️ No API key found in environment variables")
    
    # Run tests
    gemini_success = test_gemini_integration()
    static_success = test_static_fallback()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Gemini API: {'✅ PASS' if gemini_success else '❌ FAIL'}")
    print(f"   Static Fallback: {'✅ PASS' if static_success else '❌ FAIL'}")
    
    if gemini_success or static_success:
        print("\n🎉 Integration is working! Your quiz system can generate questions.")
    else:
        print("\n⚠️ Integration needs attention. Check the error messages above.")
