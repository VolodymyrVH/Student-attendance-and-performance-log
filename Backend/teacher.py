import sqlite3

conn = sqlite3.connect("sql/database.db")
cursor = conn.cursor()


def createLesson():
    subject_name = input("Enter subject name: ")

    cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (subject_name,))
    subject = cursor.fetchone()
    if not subject:
        print("No subject found with that name.")
        return
    subject_id = subject[0]

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
        INSERT INTO lessons (subject_id, teacher_id, lesson_date, time, room, topic, type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (subject_id, teacher_id, lesson_date, time, room, topic, typeLesson))
    lesson_id = cursor.lastrowid

    groups_input = input("Enter group names (comma separated): ")
    group_names = [g.strip() for g in groups_input.split(",")]

    for group_name in group_names:
        cursor.execute("SELECT id FROM groups WHERE group_name = ?", (group_name,))
        group = cursor.fetchone()
        if not group:
            print(f"No group found with name '{group_name}', skipping.")
            continue
        group_id = group[0]

        cursor.execute("INSERT INTO lesson_groups (lesson_id, group_id) VALUES (?, ?)", (lesson_id, group_id))

    conn.commit()
    print("Lesson was successfully created with all groups!")


def changeLesson():
    subject_name = input("Enter subject name: ")

    cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (subject_name,))
    subject = cursor.fetchone()
    if not subject:
        print("No subject found with that name.")
        return
    subject_id = subject[0]

    lesson_date = input("Enter current lesson date (YYYY-MM-DD): ")
    time = input("Enter current time (e.g. 10:00): ")

    cursor.execute("""
        SELECT id FROM lessons
        WHERE subject_id = ? AND lesson_date = ? AND time = ?
    """, (subject_id, lesson_date, time))
    lesson = cursor.fetchone()
    if not lesson:
        print("No lesson found with those details.")
        return
    lesson_id = lesson[0]

    changing = input("What do you want to change? (date / time / room / topic / type): ").lower()

    if changing == "date":
        new_value = input("Enter new lesson date (YYYY-MM-DD): ")
        cursor.execute("UPDATE lessons SET lesson_date = ? WHERE id = ?", (new_value, lesson_id))
    elif changing == "time":
        new_value = input("Enter new time (e.g. 10:00): ")
        cursor.execute("UPDATE lessons SET time = ? WHERE id = ?", (new_value, lesson_id))
    elif changing == "room":
        new_value = input("Enter new room: ")
        cursor.execute("UPDATE lessons SET room = ? WHERE id = ?", (new_value, lesson_id))
    elif changing == "topic":
        new_value = input("Enter new topic: ")
        cursor.execute("UPDATE lessons SET topic = ? WHERE id = ?", (new_value, lesson_id))
    elif changing == "type":
        new_value = input("Enter new type (lecture / practice / lab): ").lower()
        if new_value not in ("lecture", "practice", "lab"):
            print("Invalid type of lesson.")
            return
        cursor.execute("UPDATE lessons SET type = ? WHERE id = ?", (new_value, lesson_id))
    else:
        print("Invalid field to change.")
        return

    conn.commit()
    print("Lesson was successfully updated!")


def deleteLesson():
    subject_name = input("Enter subject name: ")

    cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (subject_name,))
    subject = cursor.fetchone()
    if not subject:
        print("No subject found with that name.")
        return
    subject_id = subject[0]

    lesson_date = input("Enter lesson date (YYYY-MM-DD): ")
    time = input("Enter time (e.g. 10:00): ")

    cursor.execute("""
        SELECT id FROM lessons
        WHERE subject_id = ? AND lesson_date = ? AND time = ?
    """, (subject_id, lesson_date, time))
    lesson = cursor.fetchone()
    if not lesson:
        print("No lesson found with those details.")
        return
    lesson_id = lesson[0]

    cursor.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
    conn.commit()
    print("Lesson was successfully deleted!")


def markAttendance():
    subject_name = input("Enter subject name: ")
    cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (subject_name,))
    subject = cursor.fetchone()
    if not subject:
        print("No subject found with that name.")
        return
    subject_id = subject[0]

    lesson_date = input("Enter lesson date (YYYY-MM-DD): ")
    time = input("Enter time (e.g. 10:00): ")

    cursor.execute("""
        SELECT id FROM lessons
        WHERE subject_id = ? AND lesson_date = ? AND time = ?
    """, (subject_id, lesson_date, time))
    lesson = cursor.fetchone()
    if not lesson:
        print("No lesson found with those details.")
        return
    lesson_id = lesson[0]

    student_name = input("Enter student full name: ")
    cursor.execute("SELECT id FROM users WHERE full_name = ? AND role = 'student'", (student_name,))
    student = cursor.fetchone()
    if not student:
        print("No student found with that name.")
        return
    student_id = student[0]

    attendance = input("Enter attendance status (present / absent): ").lower()
    if attendance not in ("present", "absent"):
        print("Invalid attendance status.")
        return

    cursor.execute(
        "INSERT OR REPLACE INTO attendance (lesson_id, student_id, status) VALUES (?, ?, ?)",
        (lesson_id, student_id, attendance)
    )
    conn.commit()
    print("Attendance was successfully marked!")


def addGrade():
    subject_name = input("Enter subject name: ")
    cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (subject_name,))
    subject = cursor.fetchone()
    if not subject:
        print("No subject found with that name.")
        return
    subject_id = subject[0]

    student_name = input("Enter student full name: ")
    cursor.execute("SELECT id FROM users WHERE full_name = ? AND role = 'student'", (student_name,))
    student = cursor.fetchone()
    if not student:
        print("No student found with that name.")
        return
    student_id = student[0]

    grade = input("Enter grade: ").upper()
    date = input("Enter grade date (YYYY-MM-DD): ")

    cursor.execute(
        "INSERT INTO grades (student_id, subject_id, grade, date) VALUES (?, ?, ?, ?)",
        (student_id, subject_id, grade, date)
    )
    conn.commit()
    print("Grade was successfully added!")


def changeGrade():
    subject_name = input("Enter subject name: ")
    cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (subject_name,))
    subject = cursor.fetchone()
    if not subject:
        print("No subject found with that name.")
        return
    subject_id = subject[0]

    student_name = input("Enter student full name: ")
    cursor.execute("SELECT id FROM users WHERE full_name = ? AND role = 'student'", (student_name,))
    student = cursor.fetchone()
    if not student:
        print("No student found with that name.")
        return
    student_id = student[0]

    date = input("Enter grade date (YYYY-MM-DD): ")
    new_grade = input("Enter new grade: ").upper()

    cursor.execute(
        "UPDATE grades SET grade = ? WHERE student_id = ? AND subject_id = ? AND date = ?",
        (new_grade, student_id, subject_id, date)
    )
    conn.commit()
    print("Grade was successfully updated!")


def deleteGrade():
    subject_name = input("Enter subject name: ")
    cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (subject_name,))
    subject = cursor.fetchone()
    if not subject:
        print("No subject found with that name.")
        return
    subject_id = subject[0]

    student_name = input("Enter student full name: ")
    cursor.execute("SELECT id FROM users WHERE full_name = ? AND role = 'student'", (student_name,))
    student = cursor.fetchone()
    if not student:
        print("No student found with that name.")
        return
    student_id = student[0]

    date = input("Enter grade date (YYYY-MM-DD): ")

    cursor.execute(
        "DELETE FROM grades WHERE student_id = ? AND subject_id = ? AND date = ?",
        (student_id, subject_id, date)
    )
    conn.commit()
    print("Grade was successfully deleted!")

