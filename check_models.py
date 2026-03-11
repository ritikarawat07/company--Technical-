#!/usr/bin/env python
"""
Check available Gemini models
"""

import os
import sys

# Set API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyAJNh0oRUr5129wx9WIHsKGa9upVJQljek'

try:
    import google.generativeai as genai
    
    # Configure API
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    
    print("🔍 Checking available Gemini models...")
    print("=" * 50)
    
    # List available models
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
        else:
            print(f"❌ {model.name} (no generateContent)")
    
    print("\n" + "=" * 50)
    print("🎯 Testing model initialization...")
    
    # Try to initialize with different models
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro',
        'gemini-pro-vision'
    ]
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            print(f"✅ {model_name} - Available")
            
            # Test generation
            response = model.generate_content("Say 'Hello from Gemini!'")
            print(f"   📝 Response: {response.text[:50]}...")
            break
            
        except Exception as e:
            print(f"❌ {model_name} - Error: {str(e)[:50]}...")
    
except ImportError:
    print("❌ google.generativeai not installed")
except Exception as e:
    print(f"❌ Error: {e}")
