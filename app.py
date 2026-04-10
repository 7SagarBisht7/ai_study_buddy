import streamlit as st
import os
import pandas as pd
import time  # Added for retry delays
from database import (
    init_db, 
    save_quiz_result, 
    get_quiz_history, 
    get_performance_stats,
    get_performance_by_difficulty,
    get_score_distribution,
    get_recent_trend
)
from ai_helper import (
    explain_concept, 
    summarize_content, 
    generate_quiz, 
    generate_flashcards,
    extract_key_points
)
from pdf_processor import extract_text_from_pdf

# Page configuration
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide"
)

# Initialize database
init_db()

# --- NEW: CACHED AI WRAPPERS ---
# This prevents 429 errors by not re-running the API if the input hasn't changed
@st.cache_data(show_spinner=False)
def get_cached_explanation(topic, difficulty):
    return explain_concept(topic, difficulty)

@st.cache_data(show_spinner=False)
def get_cached_summary(content, difficulty):
    return summarize_content(content, difficulty)

@st.cache_data(show_spinner=False)
def get_cached_quiz(content, difficulty, num):
    return generate_quiz(content, difficulty, num)

@st.cache_data(show_spinner=False)
def get_cached_flashcards(content, difficulty, num):
    return generate_flashcards(content, difficulty, num)

@st.cache_data(show_spinner=False)
def get_cached_points(content, difficulty):
    return extract_key_points(content, difficulty)

# --- NEW: ERROR HANDLING HELPER ---
def handle_ai_response(response_data):
    """Checks for 503/429 errors and provides UI feedback"""
    if isinstance(response_data, str):
        if "503" in response_data or "high demand" in response_data:
            st.error("🚦 Gemini is experiencing high demand (Error 503). Retrying in 5 seconds...")
            time.sleep(5)
            st.rerun()
        elif "429" in response_data or "RESOURCE_EXHAUSTED" in response_data:
            st.warning("⏳ Quota reached. Please wait a moment before trying again.")
            return None
    return response_data

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .flashcard {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #1E88E5;
    }
    .quiz-option {
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        cursor: pointer;
    }
    .correct {
        background-color: #c8e6c9;
        border-left: 4px solid #4caf50;
    }
    .incorrect {
        background-color: #ffcdd2;
        border-left: 4px solid #f44336;
    }
    
    /* Professional Dashboard Styles */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin: 10px 0;
    }
    
    .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .metric-card-orange {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    
    .metric-card-purple {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-delta {
        font-size: 0.85rem;
        margin-top: 5px;
    }
    
    .insight-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #1E88E5;
        margin: 15px 0;
    }
    
    .insight-card-success {
        border-left-color: #4caf50;
        background: linear-gradient(to right, #f0fff4 0%, #ffffff 100%);
    }
    
    .insight-card-warning {
        border-left-color: #ff9800;
        background: linear-gradient(to right, #fffbf0 0%, #ffffff 100%);
    }
    
    .insight-card-info {
        border-left-color: #2196f3;
        background: linear-gradient(to right, #f0f7ff 0%, #ffffff 100%);
    }
    
    .quiz-history-item {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
        border-left: 4px solid #ddd;
        transition: all 0.3s ease;
    }
    
    .quiz-history-item:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .quiz-history-excellent {
        border-left-color: #4caf50;
        background: linear-gradient(to right, #f1f8f4 0%, #ffffff 100%);
    }
    
    .quiz-history-good {
        border-left-color: #ffc107;
        background: linear-gradient(to right, #fffbf0 0%, #ffffff 100%);
    }
    
    .quiz-history-review {
        border-left-color: #f44336;
        background: linear-gradient(to right, #fff5f5 0%, #ffffff 100%);
    }
    
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 25px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .stat-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 5px;
    }
    
    .badge-excellent {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    
    .badge-good {
        background-color: #fff9c4;
        color: #f57f17;
    }
    
    .badge-review {
        background-color: #ffebee;
        color: #c62828;
    }
    
    .chart-container {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<h1 class="main-header">📚 AI-Powered Study Buddy</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your personal learning assistant for smarter studying</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # --- ADDED: GitHub Repo Link Button ---
    st.link_button(
        "💻 View Source on GitHub", 
        "https://github.com/7SagarBisht7/ai_study_buddy",
        use_container_width=True
    )
    st.divider()
    # --------------------------------------
    
    # New Chat Button at the top
    st.markdown("### 💬 Session Management")
    
    if st.button(" New Chat", use_container_width=True, type="primary"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.cache_data.clear()  # Clear cache for fresh starts
        st.rerun()
    
    st.markdown("""
    <div style="background-color: white; color:black; padding: 10px; border-radius: 8px; margin: 10px 0; font-size: 0.85rem;">
        <strong>💡 Quick Tip:</strong> Use "New Chat" to start a fresh learning session!
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Input method
    input_method = st.radio("📥 Input Method:", ["Text Input", "PDF Upload"])
    
    # Difficulty level
    difficulty = st.selectbox(
        "📚 Learning Level:",
        ["Easy", "Intermediate", "Advanced"],
        help="Choose the complexity level for explanations and quizzes"
    )
    
    st.divider()
    
    # Quick Stats Section
    st.markdown("### 📊 Quick Stats")
    
    stats = get_performance_stats()
    if stats and stats[0] > 0:
        # Create compact metric cards
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; color: white; margin-bottom: 10px;">
            <div style="font-size: 0.75rem; opacity: 0.9;">TOTAL QUIZZES</div>
            <div style="font-size: 1.8rem; font-weight: bold;">{stats[0]}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 15px; border-radius: 10px; color: white; margin-bottom: 10px;">
            <div style="font-size: 0.75rem; opacity: 0.9;">AVERAGE SCORE</div>
            <div style="font-size: 1.8rem; font-weight: bold;">{stats[1]:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 15px; border-radius: 10px; color: white; margin-bottom: 10px;">
            <div style="font-size: 0.75rem; opacity: 0.9;">BEST SCORE</div>
            <div style="font-size: 1.8rem; font-weight: bold;">{stats[2]:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("📝 No quiz history yet.")
    
    st.divider()
    
    # Session Info
    st.markdown("### 🔧 Session Info")
    
    # Check if there's active content
    has_content = False
    content_type = "None"
    
    if 'quiz_questions' in st.session_state:
        has_content = True
        content_type = "Quiz Active"
    elif 'flashcards' in st.session_state:
        has_content = True
        content_type = "Flashcards Active"
    
    if has_content:
        st.markdown(f"""
        <div style="background-color: #fff3cd; padding: 10px; border-radius: 8px; border-left: 4px solid #ffc107;">
            <strong>📌 Current Session:</strong><br>
            <span style="color: #856404;">{content_type}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background-color: #d1ecf1; padding: 10px; border-radius: 8px; border-left: 4px solid #17a2b8;">
            <strong>📌 Session Status:</strong><br>
            <span style="color: #0c5460;">Ready for new content</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📖", help="Go to Explain tab", use_container_width=True):
            st.info("Switch to 'Explain' tab above!")
    
    with col2:
        if st.button("❓", help="Go to Quiz tab", use_container_width=True):
            st.info("Switch to 'Quiz' tab above!")
    
    st.divider()
    
    # Help & Info
    st.markdown("### ℹ️ Help")
    
    with st.expander("🎯 How to Use"):
        st.markdown("""
        **Getting Started:**
        1. Enter a topic or upload PDF
        2. Select difficulty level
        3. Choose a tab (Explain, Quiz, etc.)
        4. Start learning!
        """)
    
    st.divider()
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 10px; font-size: 0.75rem; color: #666;">
        <strong>AI Study Buddy</strong><br>
        Powered by Gemini 2.5 Flash<br>
        v1.0.0
    </div>
    """, unsafe_allow_html=True)

# Main content area
if input_method == "Text Input":
    topic = st.text_area(
        "Enter topic or paste your notes:",
        height=150,
        placeholder="e.g., Photosynthesis, Newton's Laws, Machine Learning Basics..."
    )
    content = topic
else:
    uploaded_file = st.file_uploader("Upload PDF file", type=['pdf'])
    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            content = extract_text_from_pdf(uploaded_file)
            st.success(f"✅ Extracted {len(content)} characters from PDF")
    else:
        content = None

# Tabs for different features
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📖 Explain", "📝 Summary", "❓ Quiz", "🎴 Flashcards", "🔑 Key Points", "📈 Progress"
])

# Tab 1: Explain Concept
with tab1:
    st.header("Concept Explanation")
    
    if st.button("Generate Explanation", key="explain_btn", type="primary"):
        if content:
            with st.spinner(f"Generating {difficulty.lower()} level explanation..."):
                raw_exp = get_cached_explanation(content, difficulty)
                explanation = handle_ai_response(raw_exp)
                if explanation:
                    st.markdown(explanation)
        else:
            st.warning("Please enter a topic or upload a PDF first!")

# Tab 2: Summary
with tab2:
    st.header("Content Summary")
    
    if st.button("Generate Summary", key="summary_btn", type="primary"):
        if content:
            with st.spinner("Creating summary..."):
                raw_sum = get_cached_summary(content, difficulty)
                summary = handle_ai_response(raw_sum)
                if summary:
                    st.markdown(summary)
        else:
            st.warning("Please enter content or upload a PDF first!")

# Tab 3: Quiz
with tab3:
    st.header("Test Your Knowledge")
    
    num_questions = st.slider("Number of questions:", 3, 10, 5)
    
    if st.button("Generate Quiz", key="quiz_btn", type="primary"):
        if content:
            with st.spinner("Creating quiz questions..."):
                raw_quiz = get_cached_quiz(content, difficulty, num_questions)
                questions = handle_ai_response(raw_quiz)
                
                if questions and not isinstance(questions, str):
                    st.session_state['quiz_questions'] = questions
                    st.session_state['quiz_answers'] = {}
                    st.session_state['quiz_submitted'] = False
                    st.rerun()
                elif isinstance(questions, str):
                    st.error("Failed to generate quiz. Model busy or quota reached.")
        else:
            st.warning("Please enter a topic or upload a PDF first!")
    
    # Display quiz if generated
    if 'quiz_questions' in st.session_state and st.session_state['quiz_questions']:
        questions = st.session_state['quiz_questions']
        
        if not st.session_state.get('quiz_submitted', False):
            with st.form("quiz_form"):
                for i, q in enumerate(questions):
                    st.subheader(f"Question {i+1}")
                    st.write(q['question'])
                    
                    answer = st.radio(
                        "Select your answer:",
                        options=list(q['options'].keys()),
                        format_func=lambda x: f"{x}: {q['options'][x]}",
                        key=f"q_{i}"
                    )
                    st.session_state['quiz_answers'][i] = answer
                
                submit = st.form_submit_button("Submit Quiz", type="primary")
                
                if submit:
                    st.session_state['quiz_submitted'] = True
                    st.rerun()
        else:
            # Show results
            score = 0
            for i, q in enumerate(questions):
                user_answer = st.session_state['quiz_answers'].get(i)
                correct = q['correct_answer']
                
                st.subheader(f"Question {i+1}")
                st.write(q['question'])
                
                if user_answer == correct:
                    score += 1
                    st.markdown(f'<div class="quiz-option correct">✅ Your answer: {user_answer} - Correct!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="quiz-option incorrect">❌ Your answer: {user_answer} - Incorrect</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="quiz-option correct">✅ Correct answer: {correct}</div>', unsafe_allow_html=True)
                
                st.info(f"💡 {q['explanation']}")
                st.divider()
            
            percentage = (score / len(questions)) * 100
            st.success(f"### Final Score: {score}/{len(questions)} ({percentage:.1f}%)")
            
            save_quiz_result(content[:100] if content else "Quiz", difficulty, score, len(questions))
            
            if st.button("Take Another Quiz"):
                del st.session_state['quiz_questions']
                del st.session_state['quiz_answers']
                del st.session_state['quiz_submitted']
                st.rerun()

# Tab 4: Flashcards
with tab4:
    st.header("Study Flashcards")
    
    num_cards = st.slider("Number of flashcards:", 3, 10, 5, key="flashcard_slider")
    
    if st.button("Generate Flashcards", key="flashcard_btn", type="primary"):
        if content:
            with st.spinner("Creating flashcards..."):
                raw_flash = get_cached_flashcards(content, difficulty, num_cards)
                flashcards = handle_ai_response(raw_flash)
                
                if flashcards and not isinstance(flashcards, str):
                    st.session_state['flashcards'] = flashcards
                    st.session_state['show_answers'] = [False] * len(flashcards)
                    st.rerun()
        else:
            st.warning("Please enter a topic or upload a PDF first!")
    
    if 'flashcards' in st.session_state:
        flashcards = st.session_state['flashcards']
        for i, card in enumerate(flashcards):
            with st.container():
                st.markdown(f'<div class="flashcard">', unsafe_allow_html=True)
                st.subheader(f"Card {i+1}")
                st.write(f"**Q:** {card['front']}")
                if st.button(f"Show Answer", key=f"show_{i}"):
                    st.session_state['show_answers'][i] = not st.session_state['show_answers'][i]
                if st.session_state['show_answers'][i]:
                    st.write(f"**A:** {card['back']}")
                st.markdown('</div>', unsafe_allow_html=True)

# Tab 5: Key Points
with tab5:
    st.header("Key Points")
    
    if st.button("Extract Key Points", key="keypoints_btn", type="primary"):
        if content:
            with st.spinner("Extracting key points..."):
                raw_pts = get_cached_points(content, difficulty)
                key_points = handle_ai_response(raw_pts)
                if key_points:
                    st.markdown(key_points)
        else:
            st.warning("Please enter content or upload a PDF first!")

# Tab 6: Progress Tracking
with tab6:
    st.markdown('<p class="section-header">📊 Learning Performance Dashboard</p>', unsafe_allow_html=True)
    
    history = get_quiz_history()
    stats = get_performance_stats()
    
    if history and stats and stats[0] > 0:
        st.markdown("### Key Metrics Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'<div class="metric-card metric-card-purple"><div class="metric-label">Total Quizzes</div><div class="metric-value">{stats[0]}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card metric-card-blue"><div class="metric-label">Average Score</div><div class="metric-value">{stats[1]:.1f}%</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card metric-card-green"><div class="metric-label">Best Score</div><div class="metric-value">{stats[2]:.1f}%</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card metric-card-orange"><div class="metric-label">Range</div><div class="metric-value">{stats[2]-stats[3]:.1f}%</div></div>', unsafe_allow_html=True)

        # Charts logic from original code...
        df_history = pd.DataFrame(history, columns=['Topic', 'Difficulty', 'Score', 'Total', 'Percentage', 'Timestamp'])
        st.line_chart(df_history.set_index('Timestamp')['Percentage'])
    else:
        st.info("Begin your learning adventure by taking a quiz!")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Built with ❤️ using Streamlit & Google Gemini 2.5 Flash</p>
</div>
""", unsafe_allow_html=True)
