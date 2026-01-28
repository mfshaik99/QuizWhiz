import sqlite3
import csv
import os

# Database file name
DB_FILE = "quizwhiz.db"

# Remove old database if exists (fresh start)
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print("Old quizwhiz.db removed.")

# Connect to SQLite (creates DB automatically)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create questions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_option TEXT,
    topic TEXT,
    difficulty TEXT
)
""")

# CSV file path
CSV_FILE = "questions.csv"

# Check if CSV exists
if not os.path.exists(CSV_FILE):
    print(f"❌ CSV file '{CSV_FILE}' not found! Please upload it to the repo.")
else:
    # Read CSV and insert into DB
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor.execute("""
            INSERT INTO questions 
            (question, option_a, option_b, option_c, option_d, correct_option, topic, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['question'],
                row['option_a'],
                row['option_b'],
                row['option_c'],
                row['option_d'],
                row['correct_option'],
                row['topic'],
                row['difficulty']
            ))

    conn.commit()
    print(f"✅ quizwhiz.db created successfully with questions from {CSV_FILE}!")

conn.close()
