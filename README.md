# AI Adaptive Flight Dispatcher Quiz

An intelligent, adaptive quiz system designed specifically for flight dispatcher training and certification. The system uses AI-powered algorithms to adjust question difficulty based on user performance, providing an optimal learning experience.

## Features

### 🎯 Adaptive Difficulty
- Questions automatically adjust to user skill level
- Personalized learning paths based on performance
- Real-time skill assessment and progression

### 📊 Comprehensive Analytics
- Detailed performance tracking
- Response time analysis
- Strength and weakness identification
- Progress monitoring over time

### 🧠 AI-Powered Intelligence
- Smart question selection algorithms
- Performance pattern recognition
- Personalized recommendations
- Study material suggestions

### 🎨 Modern Interface
- Responsive design for all devices
- Intuitive user experience
- Real-time feedback and explanations
- Beautiful, accessible UI

## Technology Stack

- **Backend**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Database**: SQLite (development)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Styling**: Modern CSS with animations and transitions

## Project Structure

```
AI_Adaptive_Flight_Dispatcher_Quiz/
├── quiz_system/           # Django project configuration
│   ├── __init__.py
│   ├── settings.py        # Project settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── quiz/                 # Main quiz application
│   ├── __init__.py
│   ├── admin.py          # Django admin configuration
│   ├── apps.py           # App configuration
│   ├── models.py         # Database models
│   ├── serializers.py    # API serializers
│   ├── views.py          # API views and logic
│   ├── urls.py           # App URL configuration
│   └── ai_service.py     # AI adaptive learning service
├── templates/            # HTML templates
│   └── index.html        # Main application template
├── static/              # Static files
│   └── styles.css       # Application styles
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI_Adaptive_Flight_Dispatcher_Quiz
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main application: http://127.0.0.1:8000/
   - Admin interface: http://127.0.0.1:8000/admin/
   - API endpoints: http://127.0.0.1:8000/api/quiz/

## Usage

### For Students/Learners

1. **Start a Quiz**: Click "Start Quiz" on the main page
2. **Answer Questions**: The system will present questions adapted to your skill level
3. **View Feedback**: Receive immediate feedback with explanations
4. **Track Progress**: Monitor your performance in the statistics section

### For Administrators

1. **Access Admin Panel**: Go to `/admin/` and log in with superuser credentials
2. **Manage Quizzes**: Create and edit quiz content
3. **Add Questions**: Add questions with different difficulty levels
4. **Monitor Users**: View user performance and statistics

## API Endpoints

### Quiz Management
- `GET /api/quiz/quizzes/` - List all available quizzes
- `GET /api/quiz/quizzes/{id}/` - Get quiz details
- `POST /api/quiz/quizzes/{id}/start_session/` - Start a new quiz session

### Adaptive Questions
- `POST /api/quiz/adaptive/` - Get adaptive question based on skill level
- `POST /api/quiz/questions/{id}/submit_answer/` - Submit answer and get feedback

### User Statistics
- `GET /api/quiz/stats/` - Get user performance statistics
- `GET /api/quiz/profiles/` - Get user profile information

### Sample Data
- `POST /api/quiz/create-sample-data/` - Create sample quiz and questions

## Models

### Quiz
- Title and description
- Category and difficulty level
- Associated questions

### Question
- Question text and type (multiple choice, true/false, short answer)
- Difficulty level (0.0 - 1.0)
- Correct answer and options
- Explanations for learning

### User Profile
- Skill level tracking
- Performance statistics
- Response history

### User Response
- Question and user answer
- Correct/incorrect status
- Response time tracking

### Quiz Session
- Start and end times
- Score calculation
- Completion status

## Adaptive Algorithm

The system uses a sophisticated adaptive algorithm that:

1. **Assesses User Skill Level**: Maintains a dynamic skill level (0.0 - 1.0)
2. **Selects Appropriate Questions**: Chooses questions matching user ability
3. **Updates Performance**: Adjusts skill level based on answers
4. **Provides Feedback**: Offers personalized learning recommendations

### Skill Level Calculation
- Correct answers increase skill level (+0.05)
- Incorrect answers decrease skill level (-0.03)
- Skill level is bounded between 0.0 and 1.0

## Question Types

### Multiple Choice
- Four options with one correct answer
- Immediate feedback with explanation
- Suitable for factual knowledge

### True/False
- Binary choice questions
- Quick assessment of understanding
- Good for concept verification

### Short Answer
- Open-ended responses
- Case-insensitive matching
- Tests deeper understanding

## Frontend Features

### Responsive Design
- Mobile-friendly interface
- Tablet and desktop optimization
- Touch-friendly interactions

### Real-time Updates
- Progress tracking
- Live score updates
- Immediate feedback display

### Accessibility
- WCAG 2.1 compliance
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support

## Configuration

### Environment Variables
Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Settings
- Development: SQLite (default)
- Production: PostgreSQL recommended
- Configure in `quiz_system/settings.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Testing

Run the test suite:
```bash
python manage.py test
```

## Deployment

### Production Considerations
- Set `DEBUG = False` in settings
- Configure proper database
- Set up static file serving
- Configure security settings
- Set up monitoring and logging

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Future Enhancements

### Planned Features
- [ ] User authentication system
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration with learning management systems
- [ ] Mobile app development
- [ ] Real-time collaboration features
- [ ] Gamification elements
- [ ] Export functionality for results

### AI Improvements
- [ ] Machine learning integration
- [ ] Natural language processing
- [ ] Predictive analytics
- [ ] Personalized learning paths
- [ ] Intelligent tutoring system

---

**Note**: This is an educational project designed for flight dispatcher training. The adaptive algorithms provide a foundation for intelligent learning systems and can be extended for various educational domains.
