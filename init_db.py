import sqlite3
import csv

# 1. Connect to database (will create if not exists)
conn = sqlite3.connect("quizwhiz.db")
cursor = conn.cursor()

# 2. Create questions table
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

# 3. Open CSV and insert questions
with open("questions.csv", newline='', encoding='utf-8') as csvfile:
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

# 4. Save and close connection
conn.commit()
conn.close()

print("✅ Questions imported successfully!")
