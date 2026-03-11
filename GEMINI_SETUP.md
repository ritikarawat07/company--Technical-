# Google Gemini API Integration Setup Guide

## 🚀 Overview

Your AI Adaptive Flight Dispatcher Quiz now supports Google Gemini API for dynamic question generation! The system will automatically use Gemini when available and fall back to static questions when not.

## 📋 Setup Instructions

### 1. Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Configure the API Key

#### Option A: Environment Variables (Recommended)
```bash
# Windows PowerShell
$env:GEMINI_API_KEY = "your-api-key-here"

# Windows Command Prompt
set GEMINI_API_KEY=your-api-key-here

# Linux/Mac
export GEMINI_API_KEY=your-api-key-here
```

#### Option B: .env File
1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

### 3. Test the Integration

Run the test script to verify everything is working:
```bash
python test_gemini.py
```

## 🎯 How It Works

### Question Generation Flow
1. **Primary**: Google Gemini API generates dynamic questions
2. **Fallback**: Static questions from the database
3. **Final Fallback**: Hardcoded template questions

### AI Question Features
- **Adaptive Difficulty**: Questions match user skill level (0.0-1.0)
- **Topic Variety**: 10 flight dispatcher topics covered
- **Realistic Scenarios**: Practical flight operations questions
- **Instant Generation**: No need to pre-create questions

## 📊 API Endpoints

### Generate AI Question
```http
POST /api/quiz/generate-ai-question/
Content-Type: application/json

{
    "user_skill_level": 0.5,
    "quiz_category": "Aviation",
    "topic": "Weather Analysis"
}
```

### Adaptive Quiz (with AI fallback)
```http
POST /api/quiz/adaptive/
Content-Type: application/json

{
    "quiz_id": 1,
    "user_skill_level": 0.5,
    "exclude_question_ids": [1, 2, 3]
}
```

## 🔧 Features

### ✅ What's Implemented
- Google Gemini API integration
- Automatic fallback to static questions
- Adaptive difficulty matching
- Topic-based question generation
- Error handling and logging
- Frontend integration with priority for AI questions

### 🎯 Supported Question Types
- Multiple Choice (4 options)
- True/False
- Short Answer

### 📚 Flight Dispatcher Topics
1. Flight Planning
2. Weather Analysis
3. Aircraft Performance
4. Navigation
5. Air Traffic Control
6. Emergency Procedures
7. Regulations
8. Communication Protocols
9. Weight and Balance
10. Fuel Management

## 🚨 Troubleshooting

### Common Issues

#### "No API key found"
- Ensure you've set the `GEMINI_API_KEY` environment variable
- Check your `.env` file if using one
- Restart your Django server after setting the key

#### "Gemini API failed"
- Check your internet connection
- Verify your API key is valid
- Check if you've exceeded API quotas
- Monitor console logs for specific error messages

#### "Invalid JSON response"
- This can happen with malformed API responses
- The system will automatically fall back to static questions
- Check the Django logs for details

### Debug Mode
Enable debug logging by setting:
```python
# In quiz/ai_service.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Usage Statistics

The system tracks:
- Question source (Gemini vs static)
- API success/failure rates
- Response times
- Error types

Monitor these in your Django admin panel under API logs.

## 🔮 Future Enhancements

### Planned Features
- [ ] Question caching to reduce API calls
- [ ] Custom prompt templates
- [ ] Multiple AI model support
- [ ] Question quality scoring
- [ ] Bulk question generation

### Advanced Configuration
You can customize the AI prompts by editing the `_generate_gemini_question` method in `quiz/ai_service.py`.

## 📞 Support

If you encounter issues:
1. Check the test script output: `python test_gemini.py`
2. Review Django logs: `python manage.py runserver --verbosity=2`
3. Verify API key at: https://makersuite.google.com/app/apikey

## 🎉 Success Indicators

You'll know it's working when you see:
- ✅ "Google Gemini API initialized successfully" in console
- ✅ "Generated AI question using Google Gemini" in browser console
- ✅ Dynamic questions that change each time
- ✅ Questions marked with source: "google_gemini"

---

**Note**: The system is designed to work seamlessly with or without the Gemini API. Static questions ensure the quiz remains functional even if AI generation fails.
