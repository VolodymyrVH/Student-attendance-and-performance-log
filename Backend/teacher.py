import sqlite3

conn = sqlite3.connect("sql/database.db")
cursor = conn.cursor()

def createLesson():
    subject_name = input("Enter subject name: ")

    cursor.execute("SELECT id, group_id FROM subjects WHERE subject_name = ?", (subject_name,))
    subject = cursor.fetchone()
    if not subject:
        print("No subject found with that name.")
        return
    subject_id, group_id = subject

    teacher_name = input("Enter teacher name: ")
    cursor.execute("""
        SELECT u.id FROM users u
        JOIN subject_teachers st ON st.teacher_id = u.id
        WHERE u.full_name = ? AND st.subject_id = ?
    """, (teacher_name, subject_id))
    teacher = cursor.fetchone()
    if not teacher:
        print("This teacher is not assigned to that subject.")
        return
    teacher_id = teacher[0]

    typeLesson = input("Select type of lesson (lecture / practice / lab): ").lower()
    if typeLesson not in ("lecture", "practice", "lab"):
        print("Invalid type of lesson.")
        return

    lesson_date = input("Enter lesson date (YYYY-MM-DD): ")
    time = input("Enter time (e.g. 10:00): ")
    room = input("Enter room: ")
    topic = input("Enter topic of the lesson: ")

    cursor.execute("""
        INSERT INTO lessons (subject_id, group_id, teacher_id, lesson_date, time, room, topic, type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (subject_id, group_id, teacher_id, lesson_date, time, room, topic, typeLesson))

    conn.commit()
    print("Lesson was successfully created!")



def changeLesson()
def deleteLesson()
def markAttendance()
def addGrade()
def changeGrade()
def deleteGrade()