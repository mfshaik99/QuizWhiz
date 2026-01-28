import streamlit as st
import sqlite3
import time
from datetime import datetime
import random
import string
import ui  # UI components

# ------------------------
# Connect to SQLite DB
# ------------------------
conn = sqlite3.connect("quizwhiz.db", check_same_thread=False)
cursor = conn.cursor()

# ------------------------
# Auto-create DB if missing
# ------------------------
import os
if not os.path.exists("quizwhiz.db"):
    import init_db

# ------------------------
# Initialize session state
# ------------------------
if 'quiz_started' not in st.session_state:
    st.session_state['quiz_started'] = False
if 'question_index' not in st.session_state:
    st.session_state['question_index'] = 0
if 'score' not in st.session_state:
    st.session_state['score'] = 0
if 'questions' not in st.session_state:
    st.session_state['questions'] = []
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = 0
if 'answer_times' not in st.session_state:
    st.session_state['answer_times'] = []

# ------------------------
# Helper: Generate Unique Quiz ID
# ------------------------
def generate_quiz_id():
    return "QW" + ''.join(random.choices(string.digits, k=4))

# ------------------------
# Landing / Join Screen
# ------------------------
st.title("🧠 QuizWhiz - Online Quiz Platform")

# Option to create new quiz
create_new = st.button("Create New Quiz")
quiz_id_input = st.text_input("Or Enter Quiz Link / ID to Join")

username = st.text_input("Enter Your Name")

# Handle quiz creation
if create_new:
    if username.strip() == "":
        st.warning("Please enter your name to create a quiz!")
    else:
        quiz_id = generate_quiz_id()
        st.success(f"Quiz created! Your Quiz ID is: {quiz_id}")
        st.session_state['quiz_started'] = True
        st.session_state['username'] = username
        st.session_state['quiz_id'] = quiz_id
        st.session_state['question_index'] = 0
        st.session_state['score'] = 0
        st.session_state['answer_times'] = []
        # Fetch 10 random questions
        cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 10")
        st.session_state['questions'] = cursor.fetchall()
        st.session_state['start_time'] = time.time()
        st.experimental_rerun()

# Handle join existing quiz
elif st.button("Join Quiz"):
    if username.strip() == "":
        st.warning("Please enter your name!")
    elif quiz_id_input.strip() == "":
        st.warning("Please enter a Quiz ID!")
    else:
        quiz_id = quiz_id_input.strip()
        st.session_state['quiz_started'] = True
        st.session_state['username'] = username
        st.session_state['quiz_id'] = quiz_id
        st.session_state['question_index'] = 0
        st.session_state['score'] = 0
        st.session_state['answer_times'] = []
        # Fetch 10 random questions
        cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 10")
        st.session_state['questions'] = cursor.fetchall()
        st.session_state['start_time'] = time.time()
        st.success(f"Welcome {username}! Quiz {quiz_id} is starting...")
        st.experimental_rerun()

# ------------------------
# Quiz Display
# ------------------------
if st.session_state['quiz_started']:
    questions = st.session_state['questions']
    idx = st.session_state['question_index']

    if idx < len(questions):
        q = questions[idx]
        answer, submit, shuffled_options, correct_option, question_id = ui.show_question(q, idx, st.session_state['start_time'])

        if submit:
            time_taken = time.time() - st.session_state['start_time']
            st.session_state['answer_times'].append(time_taken)

            # Scoring: fast correct = 2 pts, else 1 pt
            points = 0
            if answer == correct_option:
                points = 2 if time_taken <= 10 else 1
            st.session_state['score'] += points

            # Save response to DB
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    quiz_id TEXT,
                    question_id INTEGER,
                    answer TEXT,
                    correct_option TEXT,
                    score INTEGER,
                    time_taken REAL,
                    timestamp TEXT
                )
            """)
            cursor.execute("""
                INSERT INTO responses (username, quiz_id, question_id, answer, correct_option, score, time_taken, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                st.session_state['username'],
                st.session_state['quiz_id'],
                question_id,
                answer,
                correct_option,
                points,
                time_taken,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()

            # Next question
            st.session_state['start_time'] = time.time()
            st.session_state['question_index'] += 1
            st.experimental_rerun()

    else:
        # Show final score
        ui.show_score(st.session_state['score'], len(questions)*2)

        # Show leaderboard
        cursor.execute("""
            SELECT username, SUM(score) as total_score
            FROM responses
            WHERE quiz_id = ?
            GROUP BY username
            ORDER BY total_score DESC
        """, (st.session_state['quiz_id'],))
        leaderboard = cursor.fetchall()
        ui.show_leaderboard(leaderboard)
