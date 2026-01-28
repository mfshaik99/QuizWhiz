import streamlit as st
import random
import time

# ------------------------
# Landing / Join Quiz
# ------------------------
def show_join_screen():
    st.title("🧠 QuizWhiz - Online Quiz Platform")
    quiz_id = st.text_input("Enter Quiz Link / ID", value="QW1001")
    username = st.text_input("Enter Your Name")
    join = st.button("Join Quiz")
    return quiz_id, username, join

# ------------------------
# Show a single question
# ------------------------
def show_question(q, idx, start_time):
    question_id = q[0]
    question_text = q[1]
    options = [q[2], q[3], q[4], q[5]]
    correct_option = q[6]

    # Shuffle options
    shuffled_options = options.copy()
    random.shuffle(shuffled_options)

    st.write(f"**Q{idx+1}: {question_text}**")
    answer = st.radio("Select your answer:", shuffled_options, key=idx)

    submit = st.button("Submit Answer")
    return answer, submit, shuffled_options, correct_option, question_id

# ------------------------
# Show final score
# ------------------------
def show_score(score, total):
    st.success(f"🎉 Quiz Completed! Your Score: {score} / {total}")

# ------------------------
# Show leaderboard
# ------------------------
def show_leaderboard(leaderboard):
    st.subheader("🏆 Leaderboard")
    for i, row in enumerate(leaderboard, start=1):
        st.write(f"{i}. {row[0]} - {row[1]} points")
