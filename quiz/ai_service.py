import random
import json
import os
from typing import List, Dict, Optional
from .models import Quiz, Question

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AIQuestionService:
    """
    AI service for generating adaptive questions and managing difficulty levels.
    Now integrated with Google Gemini API for dynamic question generation.
    """

    def __init__(self):
        self.flight_dispatcher_topics = [
            "Flight Planning",
            "Weather Analysis", 
            "Aircraft Performance",
            "Navigation",
            "Air Traffic Control",
            "Emergency Procedures",
            "Regulations",
            "Communication Protocols",
            "Weight and Balance",
            "Fuel Management"
        ]
        
        # Initialize Gemini if available
        self.gemini_model = None
        if GEMINI_AVAILABLE:
            api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    # Use the correct model name for the current API version
                    self.gemini_model = genai.GenerativeModel('models/gemini-2.5-flash')
                    print("✅ Google Gemini API initialized successfully with gemini-2.5-flash")
                except Exception as e:
                    print(f"⚠️ Failed to initialize Gemini API: {e}")
                    # Try alternative model names
                    try:
                        self.gemini_model = genai.GenerativeModel('models/gemini-2.0-flash')
                        print("✅ Google Gemini API initialized with gemini-2.0-flash")
                    except Exception as e2:
                        try:
                            self.gemini_model = genai.GenerativeModel('models/gemini-flash-latest')
                            print("✅ Google Gemini API initialized with gemini-flash-latest")
                        except Exception as e3:
                            print(f"⚠️ Failed to initialize all Gemini models: {e3}")
            else:
                print("⚠️ No Gemini API key found in environment variables")
        else:
            print("⚠️ Google Generative AI package not installed")

    def generate_adaptive_question(self, 
                                 user_skill_level: float, 
                                 quiz_category: str,
                                 excluded_topics: List[str] = None) -> Optional[Dict]:
        """
        Generate a question adapted to the user's skill level.
        Uses Google Gemini API for dynamic question generation.
        """
        
        if excluded_topics is None:
            excluded_topics = []

        available_topics = [topic for topic in self.flight_dispatcher_topics 
                          if topic not in excluded_topics]
        
        if not available_topics:
            return None

        # Select topic based on skill level
        if user_skill_level < 0.3:
            # Beginner level - basic concepts
            topic = random.choice(available_topics[:3])
            difficulty_label = "beginner"
        elif user_skill_level < 0.7:
            # Intermediate level - mixed concepts
            topic = random.choice(available_topics[3:7])
            difficulty_label = "intermediate"
        else:
            # Advanced level - complex scenarios
            topic = random.choice(available_topics[7:])
            difficulty_label = "advanced"

        # Try to generate question using Gemini first
        if self.gemini_model:
            try:
                return self._generate_gemini_question(topic, difficulty_label, user_skill_level)
            except Exception as e:
                print(f"⚠️ Gemini API failed, falling back to static questions: {e}")
        
        # Fallback to static question generation
        return self._create_static_question(topic, user_skill_level)

    def _generate_gemini_question(self, topic: str, difficulty_label: str, skill_level: float) -> Dict:
        """Generate question using Google Gemini API."""
        
        prompt = f"""
        Generate a flight dispatcher certification question about {topic} at {difficulty_label} level.
        
        Skill level: {skill_level:.2f} (0.0 = beginner, 1.0 = expert)
        
        Requirements:
        1. Create a realistic flight operations scenario
        2. Make it multiple choice with 4 options (A, B, C, D)
        3. Include a clear, concise explanation
        4. Ensure the difficulty matches the skill level
        5. Focus on practical knowledge used by real flight dispatchers
        
        Format your response as JSON:
        {{
            "question_text": "Your question here",
            "question_type": "multiple_choice",
            "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
            "correct_answer": "A",
            "explanation": "Detailed explanation of why this is correct"
        }}
        
        Only return the JSON, no other text.
        """
        
        response = self.gemini_model.generate_content(prompt)
        
        # Parse the response
        try:
            # Extract JSON from response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            question_data = json.loads(response_text)
            
            # Add metadata
            question_data.update({
                "difficulty_level": skill_level,
                "topic": topic,
                "source": "google_gemini"
            })
            
            return question_data
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse Gemini response as JSON: {e}")
            print(f"Raw response: {response.text}")
            raise Exception("Invalid JSON response from Gemini")
        except Exception as e:
            print(f"⚠️ Error processing Gemini response: {e}")
            raise

    def _create_static_question(self, topic: str, skill_level: float) -> Dict:
        """Create a static question as fallback when Gemini is unavailable."""
        
        if skill_level < 0.4:
            difficulty = "easy"
        elif skill_level < 0.7:
            difficulty = "medium"
        else:
            difficulty = "hard"
            
        return self._create_question_data(topic, skill_level)

    def _create_question_data(self, topic: str, difficulty: float) -> Dict:
        """Create question data based on topic and difficulty."""
        
        question_templates = {
            "Flight Planning": {
                "easy": {
                    "question": "What is the primary purpose of a flight plan?",
                    "type": "multiple_choice",
                    "options": [
                        "A. Provide information to air traffic control",
                        "B. Calculate fuel requirements",
                        "C. Ensure safety and efficiency",
                        "D. All of the above"
                    ],
                    "correct": "D",
                    "explanation": "A flight plan serves multiple purposes including ATC notification, fuel calculation, and ensuring overall flight safety and efficiency."
                },
                "medium": {
                    "question": "When planning a flight, which factor has the greatest impact on fuel consumption?",
                    "type": "multiple_choice",
                    "options": [
                        "A. Aircraft weight",
                        "B. Wind conditions",
                        "C. Altitude",
                        "D. Temperature"
                    ],
                    "correct": "B",
                    "explanation": "Wind conditions, particularly headwinds or tailwinds, have the most significant impact on fuel consumption during flight."
                },
                "hard": {
                    "question": "Calculate the required fuel for a flight with 1000 NM distance, 200 KTAS cruise speed, 50 NM headwind component, and 2 hours reserve fuel, given a burn rate of 1000 lbs/hour.",
                    "type": "short_answer",
                    "correct": "3000",
                    "explanation": "Ground speed = 200 - 50 = 150 KTAS. Flight time = 1000/150 = 6.67 hours. Trip fuel = 6.67 × 1000 = 6670 lbs. Total fuel = 6670 + 2000 = 8670 lbs (approximately 3000 gallons for jet aircraft)."
                }
            },
            "Weather Analysis": {
                "easy": {
                    "question": "True or False: Cumulonimbus clouds are associated with severe weather.",
                    "type": "true_false",
                    "correct": "True",
                    "explanation": "Cumulonimbus clouds are tall, dense clouds associated with thunderstorms, heavy rain, and severe weather conditions."
                },
                "medium": {
                    "question": "What weather phenomenon is most dangerous to aircraft during takeoff and landing?",
                    "type": "multiple_choice",
                    "options": [
                        "A. Fog",
                        "B. Wind shear",
                        "C. Light rain",
                        "D. High temperature"
                    ],
                    "correct": "B",
                    "explanation": "Wind shear can cause sudden changes in aircraft performance and is particularly hazardous during takeoff and landing phases."
                },
                "hard": {
                    "question": "Given the following METAR: KLAX 151751Z 26015G25KT 10SM FEW030 SCT050 BKN120 23/15 A2992 RMK AO2 SLP215 T02330150, what is the wind direction and speed?",
                    "type": "short_answer",
                    "correct": "260 degrees at 15 knots",
                    "explanation": "The wind group '26015G25KT' indicates wind from 260 degrees (west) at 15 knots with gusts to 25 knots."
                }
            }
        }

        # Get question template or create a generic one
        if topic in question_templates:
            if difficulty < 0.4:
                template = question_templates[topic]["easy"]
            elif difficulty < 0.7:
                template = question_templates[topic]["medium"]
            else:
                template = question_templates[topic]["hard"]
        else:
            template = self._create_generic_question(topic, difficulty)

        return {
            "question_text": template["question"],
            "question_type": template["type"],
            "difficulty_level": difficulty,
            "options": template.get("options"),
            "correct_answer": template["correct"],
            "explanation": template["explanation"],
            "topic": topic
        }

    def _create_generic_question(self, topic: str, difficulty: float) -> Dict:
        """Create a generic question when specific templates are not available."""
        
        return {
            "question": f"What is the most important consideration in {topic} for flight operations?",
            "type": "short_answer",
            "correct": "safety",
            "explanation": f"In {topic}, safety is always the primary consideration for flight operations.",
        }

    def analyze_user_performance(self, 
                                responses: List[Dict]) -> Dict:
        """
        Analyze user responses to determine performance patterns.
        """
        if not responses:
            return {
                "accuracy": 0.0,
                "average_response_time": 0.0,
                "strengths": [],
                "weaknesses": [],
                "recommended_difficulty": 0.5
            }

        correct_responses = sum(1 for r in responses if r.get("is_correct", False))
        total_responses = len(responses)
        accuracy = correct_responses / total_responses if total_responses > 0 else 0.0
        
        avg_response_time = sum(r.get("response_time", 0) for r in responses) / total_responses
        
        # Analyze by topic (if available)
        topic_performance = {}
        for response in responses:
            topic = response.get("topic", "General")
            if topic not in topic_performance:
                topic_performance[topic] = {"correct": 0, "total": 0}
            topic_performance[topic]["total"] += 1
            if response.get("is_correct", False):
                topic_performance[topic]["correct"] += 1

        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        for topic, perf in topic_performance.items():
            if perf["total"] >= 3:  # Only consider topics with enough data
                accuracy = perf["correct"] / perf["total"]
                if accuracy >= 0.8:
                    strengths.append(topic)
                elif accuracy <= 0.4:
                    weaknesses.append(topic)

        # Recommend difficulty based on performance
        if accuracy >= 0.8:
            recommended_difficulty = min(1.0, 0.5 + 0.2)
        elif accuracy >= 0.6:
            recommended_difficulty = 0.5
        else:
            recommended_difficulty = max(0.0, 0.5 - 0.2)

        return {
            "accuracy": accuracy,
            "average_response_time": avg_response_time,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommended_difficulty": recommended_difficulty,
            "topic_performance": topic_performance
        }

    def generate_personalized_feedback(self, 
                                     user_profile: Dict,
                                     recent_responses: List[Dict]) -> str:
        """
        Generate personalized feedback based on user performance.
        """
        analysis = self.analyze_user_performance(recent_responses)
        
        feedback = []
        
        # Overall performance
        if analysis["accuracy"] >= 0.8:
            feedback.append("Excellent work! You're demonstrating strong knowledge.")
        elif analysis["accuracy"] >= 0.6:
            feedback.append("Good progress! Keep practicing to improve further.")
        else:
            feedback.append("Keep working on the fundamentals. Practice makes perfect!")
        
        # Specific strengths
        if analysis["strengths"]:
            feedback.append(f"Strengths: {', '.join(analysis['strengths'])}")
        
        # Areas for improvement
        if analysis["weaknesses"]:
            feedback.append(f"Focus areas: {', '.join(analysis['weaknesses'])}")
        
        # Response time feedback
        if analysis["average_response_time"] > 30:
            feedback.append("Try to answer questions more quickly while maintaining accuracy.")
        
        return " ".join(feedback)

    def suggest_study_materials(self, 
                              weaknesses: List[str],
                              skill_level: float) -> List[Dict]:
        """
        Suggest study materials based on user weaknesses and skill level.
        """
        materials = {
            "Flight Planning": [
                {"title": "FAA Flight Planning Handbook", "type": "book", "difficulty": "beginner"},
                {"title": "Advanced Flight Planning Techniques", "type": "video", "difficulty": "advanced"},
            ],
            "Weather Analysis": [
                {"title": "Aviation Weather Services", "type": "online_course", "difficulty": "intermediate"},
                {"title": "METAR/TAF Interpretation Guide", "type": "guide", "difficulty": "beginner"},
            ],
            "Aircraft Performance": [
                {"title": "Aircraft Performance Charts", "type": "reference", "difficulty": "intermediate"},
                {"title": "Weight and Balance Calculations", "type": "practice", "difficulty": "beginner"},
            ]
        }
        
        suggestions = []
        for weakness in weaknesses:
            if weakness in materials:
                # Filter materials by difficulty level
                suitable_materials = materials[weakness]
                if skill_level < 0.4:
                    suitable_materials = [m for m in suitable_materials if m["difficulty"] == "beginner"]
                elif skill_level < 0.7:
                    suitable_materials = [m for m in suitable_materials if m["difficulty"] in ["beginner", "intermediate"]]
                else:
                    suitable_materials = [m for m in suitable_materials if m["difficulty"] in ["intermediate", "advanced"]]
                
                suggestions.extend(suitable_materials[:2])  # Limit to 2 per weakness
        
        return suggestions