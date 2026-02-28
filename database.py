import sqlite3
from datetime import datetime

def init_db():
    """Initialize SQLite database for quiz results"""
    conn = sqlite3.connect('study_buddy.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_quiz_result(topic, difficulty, score, total):
    """Save quiz result to database"""
    conn = sqlite3.connect('study_buddy.db')
    c = conn.cursor()
    
    percentage = (score / total) * 100 if total > 0 else 0
    
    c.execute('''
        INSERT INTO quiz_results (topic, difficulty, score, total_questions, percentage)
        VALUES (?, ?, ?, ?, ?)
    ''', (topic, difficulty, score, total, percentage))
    
    conn.commit()
    conn.close()

def get_quiz_history():
    """Retrieve quiz history"""
    conn = sqlite3.connect('study_buddy.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT topic, difficulty, score, total_questions, percentage, timestamp
        FROM quiz_results
        ORDER BY timestamp DESC
        LIMIT 20
    ''')
    
    results = c.fetchall()
    conn.close()
    
    return results

def get_performance_stats():
    """Get overall performance statistics"""
    conn = sqlite3.connect('study_buddy.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            COUNT(*) as total_quizzes,
            AVG(percentage) as avg_score,
            MAX(percentage) as best_score,
            MIN(percentage) as lowest_score
        FROM quiz_results
    ''')
    
    stats = c.fetchone()
    conn.close()
    
    return stats

def get_performance_by_difficulty():
    """Get average performance by difficulty level"""
    conn = sqlite3.connect('study_buddy.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            difficulty,
            AVG(percentage) as avg_score,
            COUNT(*) as quiz_count
        FROM quiz_results
        GROUP BY difficulty
        ORDER BY 
            CASE difficulty
                WHEN 'Easy' THEN 1
                WHEN 'Intermediate' THEN 2
                WHEN 'Advanced' THEN 3
            END
    ''')
    
    results = c.fetchall()
    conn.close()
    
    return results

def get_score_distribution():
    """Get distribution of scores"""
    conn = sqlite3.connect('study_buddy.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            CASE 
                WHEN percentage >= 90 THEN 'Excellent'
                WHEN percentage >= 70 THEN 'Good'
                ELSE 'Needs Review'
            END as category,
            COUNT(*) as count
        FROM quiz_results
        GROUP BY category
        ORDER BY
            CASE category
                WHEN 'Excellent' THEN 1
                WHEN 'Good' THEN 2
                ELSE 3
            END
    ''')
    
    results = c.fetchall()
    conn.close()
    
    return results

def get_recent_trend(limit=5):
    """Get recent quiz trend"""
    conn = sqlite3.connect('study_buddy.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT percentage, timestamp
        FROM quiz_results
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    results = c.fetchall()
    conn.close()
    
    return results