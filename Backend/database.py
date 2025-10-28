import sqlite3
import os

path = "sql"
os.makedirs(path, exist_ok=True)

conn = sqlite3.connect(f"{path}/database.db")

conn.execute("PRAGMA foreign_keys = ON;")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL UNIQUE,
    curator_id INTEGER,
    FOREIGN KEY (curator_id) REFERENCES users(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'teacher', 'admin')),
    group_id INTEGER,
    FOREIGN KEY (group_id) REFERENCES groups(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT NOT NULL,
    UNIQUE(subject_name)
);
""")

cursor.execute("""
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    lesson_date DATE NOT NULL,
    time TEXT NOT NULL,
    room TEXT NOT NULL,
    topic TEXT NOT NULL,
    type TEXT CHECK (type IN ('lecture', 'practice', 'lab')),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT CHECK (status IN ('present', 'absent')),
    UNIQUE(lesson_id, student_id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id),
    FOREIGN KEY (student_id) REFERENCES users(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    grade TEXT NOT NULL,
    date DATE NOT NULL,
    UNIQUE(student_id, subject_id, date),
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS subject_teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (teacher_id) REFERENCES users(id),
    UNIQUE(subject_id, teacher_id)
);
""")

cursor.execute("""
CREATE TABLE lesson_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id),
    FOREIGN KEY (group_id) REFERENCES groups(id),
    UNIQUE(lesson_id, group_id)
);
""")

conn.commit()
conn.close()
