import streamlit as st
import sqlite3
import random
import time
from datetime import datetime

# ------------------------
# Connect to SQLite DB
# ------------------------
conn = sqlite3.connect("quizwhiz.db", check_same_thread=False)
cursor = conn.cursor()

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
# Title and quiz join
# ------------------------
st.title("🧠 QuizWiz - Online Quiz Platform")

# Quiz link input
quiz_id = st.text_input("Enter Quiz Link / ID", value="QZ1001")

# User name input
username = st.text_input("Enter Your Name")

# Join quiz button
if st.button("Join Quiz"):
    if username.strip() == "":
        st.warning("Please enter your name to join the quiz!")
    else:
        st.session_state['quiz_started'] = True
        st.session_state['username'] = username
        st.session_state['quiz_id'] = quiz_id
        st.session_state['question_index'] = 0
        st.session_state['score'] = 0
        st.session_state['answer_times'] = []
        # Fetch 10 random questions for this quiz
        cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 10")
        st.session_state['questions'] = cursor.fetchall()
        st.session_state['start_time'] = time.time()
        st.success(f"Welcome {username}! Quiz {quiz_id} is starting...")

# ------------------------
# Quiz display
# ------------------------
if st.session_state['quiz_started']:

    questions = st.session_state['questions']
    idx = st.session_state['question_index']

    if idx < len(questions):
        q = questions[idx]
        question_id = q[0]
        question_text = q[1]
        options = [q[2], q[3], q[4], q[5]]
        correct_option = q[6]

        # Shuffle options
        shuffled_options = options.copy()
        random.shuffle(shuffled_options)

        st.write(f"**Q{idx+1}: {question_text}**")
        answer = st.radio("Select your answer:", shuffled_options, key=idx)

        if st.button("Submit Answer"):
            # Calculate time taken
            time_taken = time.time() - st.session_state['start_time']
            st.session_state['answer_times'].append(time_taken)

            # Scoring logic
            points = 0
            if answer == correct_option:
                points = 2 if time_taken <= 10 else 1  # fast correct: 2 pts, else 1
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

            # Reset timer and move to next question
            st.session_state['start_time'] = time.time()
            st.session_state['question_index'] += 1
            st.experimental_rerun()

    else:
        st.success(f"Quiz Completed! Your Score: {st.session_state['score']} / {len(questions)*2}")

        # ------------------------
        # Display leaderboard
        # ------------------------
        st.subheader("🏆 Leaderboard")
        cursor.execute("""
            SELECT username, SUM(score) as total_score
            FROM responses
            WHERE quiz_id = ?
            GROUP BY username
            ORDER BY total_score DESC
        """, (st.session_state['quiz_id'],))
        leaderboard = cursor.fetchall()
        for i, row in enumerate(leaderboard, start=1):
            st.write(f"{i}. {row[0]} - {row[1]} points")
