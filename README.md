# 📚 AI-Powered Study Buddy

An intelligent learning assistant that transforms passive studying into active learning through AI-powered explanations, summaries, quizzes, and progress tracking.


## 🚀 Live Demo

The application is deployed on Streamlit Cloud and can be accessed here:  
👉[WEBSITE](https://aistudybuddy-sb.streamlit.app/)



## 🌟 Features

- **Concept Explanation**: Get level-appropriate explanations (Easy/Intermediate/Advanced)
- **Smart Summarization**: Summarize text notes or PDF documents
- **Interactive Quizzes**: Test your understanding with auto-generated questions
- **Flashcards**: Create study flashcards for effective memorization
- **Key Points Extraction**: Identify the most important concepts
- **Progress Tracking**: Monitor your quiz performance over time

## 🛠️ Tech Stack
- Frontend: Streamlit
- AI Model: Google Gemini 2.5 Flash
- PDF Processing: pypdf
- Database: SQLite
- Programming Language: Python 3.9+

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/ai-study-buddy.git
cd ai-study-buddy
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Gemini API key:
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file in the project root
   - Add: `GEMINI_API_KEY=your_api_key_here`

4. Run the application:
```bash
streamlit run app.py
```

## 🚀 Usage

1. Choose input method (Text or PDF)
2. Select difficulty level
3. Enter topic or upload PDF
4. Navigate through tabs:
   - **Explain**: Get detailed explanations
   - **Summary**: Generate concise summaries
   - **Quiz**: Test your knowledge
   - **Flashcards**: Create study cards
   - **Key Points**: Extract main concepts
   - **Progress**: Track your performance

## 📊 Database Schema

The app uses SQLite to store quiz results:
```sql
quiz_results (
    id INTEGER PRIMARY KEY,
    topic TEXT,
    difficulty TEXT,
    score INTEGER,
    total_questions INTEGER,
    percentage REAL,
    timestamp DATETIME
)
```
## 🤝 Contributing

Contributions, suggestions, and improvements are welcome. If you would like to enhance this project, feel free to open an issue or submit a pull request.

