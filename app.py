import streamlit as st
import os
import pandas as pd
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
    
    # New Chat Button at the top
    st.markdown("### 💬 Session Management")
    
    if st.button(" New Chat", use_container_width=True, type="primary"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown("""
    <div style="background-color: black; padding: 10px; border-radius: 8px; margin: 10px 0; font-size: 0.85rem;">
        <strong>💡 Quick Tip:</strong> Use "New Chat" to start a fresh learning session with a new topic!
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
        st.info("📝 No quiz history yet. Take your first quiz to see stats!")
    
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
        
        **Features:**
        - 📖 Explain: Get AI explanations
        - 📝 Summary: Condense content
        - ❓ Quiz: Test knowledge
        - 🎴 Flashcards: Study cards
        - 🔑 Key Points: Extract main ideas
        - 📊 Progress: Track performance
        """)
    
    with st.expander("🔥 Pro Tips"):
        st.markdown("""
        - Start with Easy difficulty
        - Take multiple quizzes on same topic
        - Review wrong answers carefully
        - Use flashcards for memorization
        - Track progress regularly
        - Challenge yourself gradually
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
            with st.expander("Preview extracted text"):
                st.text(content[:500] + "..." if len(content) > 500 else content)
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
                explanation = explain_concept(content, difficulty)
                st.markdown(explanation)
        else:
            st.warning("Please enter a topic or upload a PDF first!")

# Tab 2: Summary
with tab2:
    st.header("Content Summary")
    
    if st.button("Generate Summary", key="summary_btn", type="primary"):
        if content:
            with st.spinner("Creating summary..."):
                summary = summarize_content(content, difficulty)
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
                questions = generate_quiz(content, difficulty, num_questions)
                
                if questions:
                    st.session_state['quiz_questions'] = questions
                    st.session_state['quiz_answers'] = {}
                    st.session_state['quiz_submitted'] = False
                    st.rerun()
                else:
                    st.error("Failed to generate quiz. Please try again.")
        else:
            st.warning("Please enter a topic or upload a PDF first!")
    
    # Display quiz if generated
    if 'quiz_questions' in st.session_state and st.session_state['quiz_questions']:
        questions = st.session_state['quiz_questions']
        
        if not st.session_state.get('quiz_submitted', False):
            # Quiz form
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
            
            # Final score
            percentage = (score / len(questions)) * 100
            st.success(f"### Final Score: {score}/{len(questions)} ({percentage:.1f}%)")
            
            # Save to database
            save_quiz_result(
                topic=content[:100] if content else "Quiz",
                difficulty=difficulty,
                score=score,
                total=len(questions)
            )
            
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
                flashcards = generate_flashcards(content, difficulty, num_cards)
                
                if flashcards:
                    st.session_state['flashcards'] = flashcards
                    st.session_state['show_answers'] = [False] * len(flashcards)
                    st.rerun()
                else:
                    st.error("Failed to generate flashcards. Please try again.")
        else:
            st.warning("Please enter a topic or upload a PDF first!")
    
    # Display flashcards
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
                key_points = extract_key_points(content, difficulty)
                st.markdown(key_points)
        else:
            st.warning("Please enter content or upload a PDF first!")

# Tab 6: Progress Tracking
# Tab 6: Progress Tracking - Professional Dashboard
with tab6:
    st.markdown('<p class="section-header">📊 Learning Performance Dashboard</p>', unsafe_allow_html=True)
    
    history = get_quiz_history()
    stats = get_performance_stats()
    
    if history and stats and stats[0] > 0:
        
        # ============== TOP METRICS ROW ==============
        st.markdown("### Key Metrics Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card metric-card-purple">
                <div class="metric-label">Total Quizzes</div>
                <div class="metric-value">{stats[0]}</div>
                <div class="metric-delta">🎯 Keep learning!</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_score = stats[1]
            delta_symbol = "📈" if avg_score >= 70 else "📊"
            st.markdown(f"""
            <div class="metric-card metric-card-blue">
                <div class="metric-label">Average Score</div>
                <div class="metric-value">{avg_score:.1f}%</div>
                <div class="metric-delta">{delta_symbol} {'+' if avg_score >= 70 else ''}{avg_score - 70:.1f}% from target</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card metric-card-green">
                <div class="metric-label">Best Performance</div>
                <div class="metric-value">{stats[2]:.1f}%</div>
                <div class="metric-delta">🏆 Personal Best</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            improvement = stats[2] - stats[3]
            st.markdown(f"""
            <div class="metric-card metric-card-orange">
                <div class="metric-label">Score Range</div>
                <div class="metric-value">{improvement:.1f}%</div>
                <div class="metric-delta">💪 Growth potential</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ============== CHARTS ROW ==============
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### 📈 Performance Trend Over Time")
            
            # Prepare data for line chart
            df_history = pd.DataFrame(
                history,
                columns=['Topic', 'Difficulty', 'Score', 'Total', 'Percentage', 'Timestamp']
            )
            df_history['Quiz Number'] = range(len(df_history), 0, -1)
            
            # Create line chart data
            chart_data = df_history[['Quiz Number', 'Percentage']].sort_values('Quiz Number')
            
            st.line_chart(
                chart_data.set_index('Quiz Number'),
                use_container_width=True,
                height=280,
                color='#1E88E5'
            )
            
            st.caption("🎯 **Target: 70%** | Track your learning journey and identify patterns")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("#### 🎯 Performance by Difficulty")
            
            # Calculate averages by difficulty
            df_by_diff = df_history.groupby('Difficulty')['Percentage'].mean().reset_index()
            df_by_diff.columns = ['Difficulty', 'Average Score']
            
            # Create bar chart
            st.bar_chart(
                df_by_diff.set_index('Difficulty'),
                use_container_width=True,
                height=280,
                color='#4CAF50'
            )
            
            st.caption("📊 Compare mastery across difficulty levels")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ============== SCORE DISTRIBUTION & RECENT HISTORY ==============
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown('<p class="section-header">🏅 Score Distribution</p>', unsafe_allow_html=True)
            
            # Calculate score ranges
            excellent = len([h for h in history if h[4] >= 90])
            good = len([h for h in history if 70 <= h[4] < 90])
            needs_improvement = len([h for h in history if h[4] < 70])
            
            total_quizzes = stats[0]
            
            st.markdown(f"""
            <div class="insight-card insight-card-success">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 0.9rem; color: #666;">🌟 Excellent (90%+)</div>
                        <div style="font-size: 1.8rem; font-weight: bold; color: #2e7d32;">{excellent}</div>
                    </div>
                    <div style="font-size: 1.2rem; color: #4caf50;">
                        {(excellent/total_quizzes*100):.0f}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="insight-card insight-card-warning">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 0.9rem; color: #666;">✅ Good (70-89%)</div>
                        <div style="font-size: 1.8rem; font-weight: bold; color: #f57f17;">{good}</div>
                    </div>
                    <div style="font-size: 1.2rem; color: #ff9800;">
                        {(good/total_quizzes*100):.0f}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="insight-card insight-card-info">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 0.9rem; color: #666;">📚 Review (<70%)</div>
                        <div style="font-size: 1.8rem; font-weight: bold; color: #c62828;">{needs_improvement}</div>
                    </div>
                    <div style="font-size: 1.2rem; color: #f44336;">
                        {(needs_improvement/total_quizzes*100):.0f}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Visual distribution bar
            st.markdown(f"""
            <div style="margin-top: 20px;">
                <div style="background-color: #f5f5f5; border-radius: 10px; overflow: hidden; height: 30px; display: flex;">
                    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); width: {(excellent/total_quizzes*100):.1f}%; display: flex; align-items: center; justify-content: center; color: white; font-size: 0.75rem; font-weight: bold;">
                        {excellent if excellent > 0 else ''}
                    </div>
                    <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); width: {(good/total_quizzes*100):.1f}%; display: flex; align-items: center; justify-content: center; color: white; font-size: 0.75rem; font-weight: bold;">
                        {good if good > 0 else ''}
                    </div>
                    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); width: {(needs_improvement/total_quizzes*100):.1f}%; display: flex; align-items: center; justify-content: center; color: white; font-size: 0.75rem; font-weight: bold;">
                        {needs_improvement if needs_improvement > 0 else ''}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown('<p class="section-header">📚 Recent Quiz History</p>', unsafe_allow_html=True)
            
            # Display recent quizzes
            for i, record in enumerate(history[:6]):
                topic, diff, score, total, percentage, timestamp = record
                
                # Determine style based on performance
                if percentage >= 90:
                    card_class = "quiz-history-excellent"
                    badge_class = "badge-excellent"
                    icon = "🟢"
                    badge_text = "Excellent"
                elif percentage >= 70:
                    card_class = "quiz-history-good"
                    badge_class = "badge-good"
                    icon = "🟡"
                    badge_text = "Good"
                else:
                    card_class = "quiz-history-review"
                    badge_class = "badge-review"
                    icon = "🔴"
                    badge_text = "Needs Review"
                
                topic_display = topic[:45] + "..." if len(topic) > 45 else topic
                
                st.markdown(f"""
                <div class="quiz-history-item {card_class}">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <div style="font-weight: 600; font-size: 0.95rem; color: #2c3e50; margin-bottom: 5px;">
                                {icon} {topic_display}
                            </div>
                            <div style="font-size: 0.8rem; color: #7f8c8d;">
                                📅 {timestamp}
                            </div>
                        </div>
                        <div style="text-align: right; margin-left: 15px;">
                            <div style="font-size: 1.4rem; font-weight: bold; color: #2c3e50;">
                                {percentage:.0f}%
                            </div>
                            <div style="font-size: 0.75rem; color: #7f8c8d;">
                                {score}/{total} • {diff}
                            </div>
                            <span class="stat-badge {badge_class}">{badge_text}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ============== INSIGHTS & RECOMMENDATIONS ==============
        st.markdown('<p class="section-header">💡 AI-Powered Learning Insights</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Best difficulty level
            if len(df_by_diff) > 0:
                best_difficulty = df_by_diff.loc[df_by_diff['Average Score'].idxmax(), 'Difficulty']
                best_score = df_by_diff['Average Score'].max()
                
                st.markdown(f"""
                <div class="insight-card insight-card-success">
                    <h4 style="color: #2e7d32; margin-top: 0;">🎯 Strength Area</h4>
                    <p style="font-size: 0.9rem; color: #666;">You excel at <strong>{best_difficulty}</strong> level</p>
                    <div style="font-size: 2rem; font-weight: bold; color: #2e7d32; margin: 10px 0;">
                        {best_score:.1f}%
                    </div>
                    <p style="font-size: 0.85rem; color: #4caf50; margin: 0;">
                        ✨ Keep challenging yourself at this level!
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Growth area
            if len(df_by_diff) > 1:
                worst_difficulty = df_by_diff.loc[df_by_diff['Average Score'].idxmin(), 'Difficulty']
                worst_score = df_by_diff['Average Score'].min()
                
                st.markdown(f"""
                <div class="insight-card insight-card-warning">
                    <h4 style="color: #f57f17; margin-top: 0;">📈 Growth Opportunity</h4>
                    <p style="font-size: 0.9rem; color: #666;">Focus more on <strong>{worst_difficulty}</strong> level</p>
                    <div style="font-size: 2rem; font-weight: bold; color: #f57f17; margin: 10px 0;">
                        {worst_score:.1f}%
                    </div>
                    <p style="font-size: 0.85rem; color: #ff9800; margin: 0;">
                        💪 Practice makes perfect - you've got this!
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="insight-card insight-card-info">
                    <h4 style="color: #2196f3; margin-top: 0;">🎓 Explore More</h4>
                    <p style="font-size: 0.9rem; color: #666;">Try different difficulty levels</p>
                    <p style="font-size: 0.85rem; color: #2196f3; margin: 15px 0 0 0;">
                        🚀 Challenge yourself to grow!
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            # Recent trend
            if len(history) >= 3:
                recent_3 = [h[4] for h in history[:3]]
                trend_avg = sum(recent_3) / len(recent_3)
                
                if trend_avg > avg_score:
                    st.markdown(f"""
                    <div class="insight-card insight-card-success">
                        <h4 style="color: #2e7d32; margin-top: 0;">📈 Trending Up!</h4>
                        <p style="font-size: 0.9rem; color: #666;">Last 3 quizzes average</p>
                        <div style="font-size: 2rem; font-weight: bold; color: #2e7d32; margin: 10px 0;">
                            {trend_avg:.1f}%
                        </div>
                        <p style="font-size: 0.85rem; color: #4caf50; margin: 0;">
                            🚀 Above your overall average! Great momentum!
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                elif trend_avg >= avg_score - 5:
                    st.markdown(f"""
                    <div class="insight-card insight-card-info">
                        <h4 style="color: #2196f3; margin-top: 0;">💪 Stay Consistent</h4>
                        <p style="font-size: 0.9rem; color: #666;">Last 3 quizzes average</p>
                        <div style="font-size: 2rem; font-weight: bold; color: #2196f3; margin: 10px 0;">
                            {trend_avg:.1f}%
                        </div>
                        <p style="font-size: 0.85rem; color: #2196f3; margin: 0;">
                            ⚡ Keep up the good work!
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="insight-card insight-card-warning">
                        <h4 style="color: #f57f17; margin-top: 0;">🎯 Refocus Time</h4>
                        <p style="font-size: 0.9rem; color: #666;">Last 3 quizzes average</p>
                        <div style="font-size: 2rem; font-weight: bold; color: #f57f17; margin: 10px 0;">
                            {trend_avg:.1f}%
                        </div>
                        <p style="font-size: 0.85rem; color: #ff9800; margin: 0;">
                            📚 Review your study materials
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="insight-card insight-card-info">
                    <h4 style="color: #2196f3; margin-top: 0;">🎯 Keep Going!</h4>
                    <p style="font-size: 0.9rem; color: #666;">Complete more quizzes</p>
                    <p style="font-size: 0.85rem; color: #2196f3; margin: 15px 0 0 0;">
                        📊 Unlock trend analysis with more data
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ============== DETAILED STATISTICS ==============
        st.markdown('<p class="section-header">📊 Detailed Performance Statistics</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_questions = sum([h[3] for h in history])
            st.markdown(f"""
            <div class="insight-card">
                <div style="text-align: center;">
                    <div style="font-size: 0.85rem; color: #7f8c8d; text-transform: uppercase;">Questions Attempted</div>
                    <div style="font-size: 2rem; font-weight: bold; color: #2c3e50; margin: 10px 0;">{total_questions}</div>
                    <div style="font-size: 0.75rem; color: #95a5a6;">📝 Total</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_correct = sum([h[2] for h in history])
            st.markdown(f"""
            <div class="insight-card">
                <div style="text-align: center;">
                    <div style="font-size: 0.85rem; color: #7f8c8d; text-transform: uppercase;">Correct Answers</div>
                    <div style="font-size: 2rem; font-weight: bold; color: #27ae60; margin: 10px 0;">{total_correct}</div>
                    <div style="font-size: 0.75rem; color: #95a5a6;">✅ Right</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
            st.markdown(f"""
            <div class="insight-card">
                <div style="text-align: center;">
                    <div style="font-size: 0.85rem; color: #7f8c8d; text-transform: uppercase;">Overall Accuracy</div>
                    <div style="font-size: 2rem; font-weight: bold; color: #3498db; margin: 10px 0;">{overall_accuracy:.1f}%</div>
                    <div style="font-size: 0.75rem; color: #95a5a6;">🎯 Precision</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Most common difficulty
            difficulty_counts = {}
            for h in history:
                diff = h[1]
                difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
            
            if difficulty_counts:
                most_common = max(difficulty_counts, key=difficulty_counts.get)
                count = difficulty_counts[most_common]
                st.markdown(f"""
                <div class="insight-card">
                    <div style="text-align: center;">
                        <div style="font-size: 0.85rem; color: #7f8c8d; text-transform: uppercase;">Most Practiced</div>
                        <div style="font-size: 1.3rem; font-weight: bold; color: #9b59b6; margin: 10px 0;">{most_common}</div>
                        <div style="font-size: 0.75rem; color: #95a5a6;">🔥 {count} quizzes</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col5:
            # Study streak (quizzes in last 7 days)
            from datetime import datetime, timedelta
            week_ago = datetime.now() - timedelta(days=7)
            recent_quizzes = len([h for h in history if datetime.strptime(h[5], '%Y-%m-%d %H:%M:%S') > week_ago])
            
            st.markdown(f"""
            <div class="insight-card">
                <div style="text-align: center;">
                    <div style="font-size: 0.85rem; color: #7f8c8d; text-transform: uppercase;">This Week</div>
                    <div style="font-size: 2rem; font-weight: bold; color: #e74c3c; margin: 10px 0;">{recent_quizzes}</div>
                    <div style="font-size: 0.75rem; color: #95a5a6;">📅 Last 7 days</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
    else:
        # ============== EMPTY STATE - PROFESSIONAL ONBOARDING ==============
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white;">
            <h1 style="font-size: 3rem; margin-bottom: 10px;">🚀 Begin Your Learning Adventure</h1>
            <p style="font-size: 1.3rem; opacity: 0.9;">Transform your study habits with AI-powered insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="insight-card insight-card-info" style="text-align: center; min-height: 250px;">
                <div style="font-size: 4rem; margin-bottom: 15px;">📖</div>
                <h3 style="color: #2c3e50; margin-bottom: 15px;">Step 1: Learn</h3>
                <ul style="text-align: left; list-style-position: inside; color: #555; line-height: 2;">
                    <li>Enter any topic you want to master</li>
                    <li>Get AI-generated explanations</li>
                    <li>Review organized key points</li>
                    <li>Study at your own pace</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="insight-card insight-card-warning" style="text-align: center; min-height: 250px;">
                <div style="font-size: 4rem; margin-bottom: 15px;">❓</div>
                <h3 style="color: #2c3e50; margin-bottom: 15px;">Step 2: Practice</h3>
                <ul style="text-align: left; list-style-position: inside; color: #555; line-height: 2;">
                    <li>Generate custom quizzes instantly</li>
                    <li>Choose your difficulty level</li>
                    <li>Test your understanding</li>
                    <li>Learn from detailed explanations</li>
               </ul>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="insight-card insight-card-success" style="text-align: center; min-height: 250px;">
                <div style="font-size: 4rem; margin-bottom: 15px;">📊</div>
                <h3 style="color: #2c3e50; margin-bottom: 15px;">Step 3: Track & Improve</h3>
                <ul style="text-align: left; list-style-position: inside; color: #555; line-height: 2;">
                    <li>Monitor your progress over time</li>
                    <li>Identify strengths and weaknesses</li>
                    <li>Get personalized insights</li>
                    <li>Achieve your learning goals</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_tip1, col_tip2 = st.columns(2)
    
    with col_tip1:
        st.markdown("""
        <div class="insight-card insight-card-success">
            <h4 style="color: #2e7d32;">💡 Pro Tip</h4>
            <p style="color: #555;">Start with <strong>Easy</strong> difficulty to build confidence, then progressively challenge yourself with <strong>Intermediate</strong> and <strong>Advanced</strong> levels!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_tip2:
        st.markdown("""
        <div class="insight-card insight-card-info">
            <h4 style="color: #2196f3;">🎯 Success Target</h4>
            <p style="color: #555;">Aim for <strong>70%+ average score</strong> across all difficulty levels to truly master any topic. Consistency is key!</p>
        </div>
        """, unsafe_allow_html=True)
# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Built with ❤️ using Streamlit & Google Gemini 2.5 Flash</p>
    <p>Your intelligent companion for effective self-study</p>
</div>
""", unsafe_allow_html=True)