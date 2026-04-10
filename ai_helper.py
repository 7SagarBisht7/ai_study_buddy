from google import genai
from google.genai import types
from google.api_core import exceptions
import os
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

# Initialize the client with automatic retry options
client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(
            attempts=2,
            initial_delay=2.0
        )
    )
)

# Model constants
PRIMARY_MODEL = "gemini-2.5-flash"
BACKUP_MODEL = "gemini-2.5-flash-lite"

def call_gemini_with_fallback(prompt):
    """
    Helper function to handle model switching.
    If PRIMARY_MODEL fails due to quota or server load, it tries BACKUP_MODEL.
    """
    try:
        # Attempt 1: Primary Model
        response = client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=prompt
        )
        return response.text
    except (exceptions.ResourceExhausted, exceptions.ServiceUnavailable):
        try:
            # Attempt 2: Backup Model (Lite)
            response = client.models.generate_content(
                model=BACKUP_MODEL,
                contents=prompt
            )
            # Add a small note so the user knows a fallback occurred
            return response.text + "\n\n*(Note: Optimized via Lite model due to high server demand)*"
        except Exception as fallback_error:
            return f"Error: Both models are currently unavailable. {str(fallback_error)}"
    except Exception as e:
        return f"Error: {str(e)}"

def explain_concept(topic, difficulty):
    """Generate level-appropriate explanation"""
    
    difficulty_prompts = {
        "Easy": "Explain this topic in very simple terms, as if teaching a beginner or high school student. Use everyday examples and avoid technical jargon.",
        "Intermediate": "Explain this topic with moderate depth, suitable for an undergraduate student. Include key concepts and some technical details.",
        "Advanced": "Provide a comprehensive, detailed explanation suitable for advanced students or professionals. Include technical terminology, nuances, and advanced concepts."
    }
    
    prompt = f"""{difficulty_prompts[difficulty]}

Topic: {topic}

Provide a clear, structured explanation with:
1. A brief introduction
2. Main concepts broken down into digestible points
3. Relevant examples
4. A concise summary

Keep the explanation focused and educational."""
    
    return call_gemini_with_fallback(prompt)

def summarize_content(content, difficulty):
    """Summarize text content based on difficulty level"""
    
    length_guide = {
        "Easy": "brief (3-5 bullet points)",
        "Intermediate": "moderate (5-8 key points)",
        "Advanced": "comprehensive (8-10 detailed points)"
    }
    
    prompt = f"""Summarize the following content at a {difficulty.lower()} level.
    
Create a {length_guide[difficulty]} summary that captures the essential information.

Content:
{content[:8000]}

Provide the summary in a clear, organized format."""
    
    return call_gemini_with_fallback(prompt)

def generate_quiz(topic, difficulty, num_questions=5):
    """Generate quiz questions"""
    
    prompt = f"""Create {num_questions} multiple-choice questions about: {topic}

Difficulty level: {difficulty}

For each question, provide:
1. The question text
2. Four answer options (A, B, C, D)
3. The correct answer (letter only)
4. A brief explanation of why that answer is correct

Format your response as a JSON array with this structure:
[
  {{
    "question": "Question text here?",
    "options": {{
      "A": "Option A text",
      "B": "Option B text",
      "C": "Option C text",
      "D": "Option D text"
    }},
    "correct_answer": "B",
    "explanation": "Explanation here"
  }}
]

Make questions challenging but fair for the {difficulty.lower()} level.
IMPORTANT: Return ONLY the JSON array, no other text."""
    
    text = call_gemini_with_fallback(prompt)
    
    if text.startswith("Error:"):
        print(text)
        return []
        
    # Clean the fallback note if it exists before parsing JSON
    if "*(Note:" in text:
        text = text.split("*(Note:")[0].strip()
        
    try:
        # Clean the response text
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            questions = json.loads(json_match.group())
            return questions
        else:
            print(f"Could not find JSON in response: {text[:200]}")
            return []
    except Exception as e:
        print(f"Error generating quiz: {str(e)}")
        return []

def generate_flashcards(topic, difficulty, num_cards=5):
    """Generate flashcards"""
    
    prompt = f"""Create {num_cards} flashcards about: {topic}

Difficulty level: {difficulty}

Each flashcard should have:
1. A clear, focused question or term on the front
2. A concise but complete answer on the back

Format as JSON:
[
  {{
    "front": "Question or term",
    "back": "Answer or definition"
  }}
]

Make them helpful for {difficulty.lower()} level study.
IMPORTANT: Return ONLY the JSON array, no other text."""
    
    text = call_gemini_with_fallback(prompt)
    
    if text.startswith("Error:"):
        print(text)
        return []
        
    # Clean the fallback note if it exists before parsing JSON
    if "*(Note:" in text:
        text = text.split("*(Note:")[0].strip()
        
    try:
        # Clean the response text
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            flashcards = json.loads(json_match.group())
            return flashcards
        else:
            print(f"Could not find JSON in response: {text[:200]}")
            return []
    except Exception as e:
        print(f"Error generating flashcards: {str(e)}")
        return []

def extract_key_points(content, difficulty):
    """Extract key points from content"""
    
    num_points = {
        "Easy": "5-7",
        "Intermediate": "7-10",
        "Advanced": "10-15"
    }
    
    prompt = f"""Extract {num_points[difficulty]} key points from this content.

Content:
{content[:8000]}

Format as a numbered list of the most important concepts, facts, or takeaways.
Make them concise but informative for {difficulty.lower()} level understanding."""
    
    return call_gemini_with_fallback(prompt)
