import sqlite3

conn = sqlite3.connect("database.db")

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
    role TEXT NOT NULL CHECK (role IN ('student', 'teacher', 'admin')),
    group_id INTEGER,
    FOREIGN KEY (group_id) REFERENCES groups(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT NOT NULL,
    group_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    UNIQUE(subject_name, group_id),
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (teacher_id) REFERENCES users(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    lesson_date DATE NOT NULL,
    topic TEXT NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
)
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
CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    day_of_week TEXT NOT NULL CHECK (
        day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
    ),
    time TEXT NOT NULL,
    room TEXT NOT NULL,
    type TEXT CHECK (type IN ('lecture', 'practice', 'lab')),
    teacher_id INTEGER NOT NULL,
    UNIQUE(group_id, subject_id, day_of_week, time),
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (teacher_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()
