import sqlite3
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from database import get_connection, init_db

router = APIRouter(prefix="/teacher", tags=["teacher"])


class LessonCreate(BaseModel):
    subject_name: str
    teacher_name: str
    type: str
    lesson_date: str
    time: str
    room: str
    topic: str
    groups: list[str]


class LessonChange(BaseModel):
    subject_name: str | None = None
    teacher_name: str | None = None
    type: str | None = None
    lesson_date: str | None = None
    time: str | None = None
    room: str | None = None
    topic: str | None = None
    groups: list[str] | None = None
    field: str | None = None
    new_value: str | None = None


class AttendanceMark(BaseModel):
    lesson_name: str
    student_name: str
    status: str


class GradeAdd(BaseModel):
    subject_name: str
    student_name: str
    grade: str
    date: str


class GradeChange(BaseModel):
    subject_name: str | None = None
    student_name: str | None = None
    date: str | None = None
    new_grade: str | None = None


@router.get("/lessons/{teacher_name}")
def get_lessons_by_teacher(teacher_name: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT l.id, s.subject_name, u.full_name, l.lesson_date, l.time, l.room,
                l.topic, l.type,
                GROUP_CONCAT(g.group_name)
            FROM lessons l
            JOIN subjects s ON l.subject_id = s.id
            JOIN users u ON l.teacher_id = u.id
            LEFT JOIN lesson_groups lg ON lg.lesson_id = l.id
            LEFT JOIN groups g ON g.id = lg.group_id
            WHERE u.full_name = ?
            GROUP BY l.id
            """,
            (teacher_name,)
        )
        rows = cursor.fetchall()

        lessons = [
            {
                "lesson_id": r[0],
                "subject_name": r[1],
                "teacher": r[2],
                "date": r[3],
                "time": r[4],
                "room": r[5],
                "topic": r[6],
                "type": r[7],
                "groups": r[8] if r[8] else ""
            }
            for r in rows
        ]

        return lessons

    finally:
        conn.close()


@router.get("/lesson/{lesson_id}")
def get_lesson(lesson_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT l.id, s.subject_name, u.full_name, l.lesson_date, l.time, l.room, l.topic, l.type
            FROM lessons l
            JOIN subjects s ON l.subject_id = s.id
            JOIN users u ON l.teacher_id = u.id
            WHERE l.id = ?
            """,
            (lesson_id,)
        )
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Lesson not found")

        return {
            "lesson_id": row[0],
            "subject_name": row[1],
            "teacher": row[2],
            "date": row[3],
            "time": row[4],
            "room": row[5],
            "topic": row[6],
            "type": row[7]
        }

    finally:
        conn.close()


@router.post("/create_lesson")
def create_lesson(lesson: LessonCreate):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (lesson.subject_name,))
        subject = cursor.fetchone()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        subject_id = subject[0]

        cursor.execute(
            """
            SELECT id FROM users
            WHERE full_name = ? AND role = 'teacher'
            """,
            (lesson.teacher_name,)
        )
        teacher = cursor.fetchone()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not assigned to this subject")
        teacher_id = teacher[0]

        type_lesson = lesson.type.lower()
        if type_lesson not in ("lecture", "practice", "lab"):
            raise HTTPException(status_code=400, detail="Invalid lesson type")

        cursor.execute(
            """
            INSERT INTO lessons (subject_id, teacher_id, lesson_date, time, room, topic, type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (subject_id, teacher_id, lesson.lesson_date, lesson.time, lesson.room, lesson.topic, type_lesson)
        )
        lesson_id = cursor.lastrowid

        for group_name in lesson.groups:
            cursor.execute("SELECT id FROM groups WHERE group_name = ?", (group_name,))
            group = cursor.fetchone()
            if not group:
                continue
            group_id = group[0]
            cursor.execute(
                "INSERT OR IGNORE INTO lesson_groups (lesson_id, group_id) VALUES (?, ?)",
                (lesson_id, group_id)
            )

        conn.commit()
        return {"message": "Lesson was successfully created", "lesson_id": lesson_id}
    finally:
        conn.close()


@router.patch("/change_lesson")
def change_lesson(lesson_id: int, change: LessonChange):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Lesson not found")

        fields = []
        values = []

        if change.subject_name:
            cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (change.subject_name,))
            s = cursor.fetchone()
            if not s:
                raise HTTPException(status_code=404, detail="Subject not found")
            fields.append("subject_id = ?")
            values.append(s[0])

        if change.teacher_name:
            subject_id = values[fields.index("subject_id = ?")] if "subject_id = ?" in fields else existing["subject_id"]
            cursor.execute(
                "SELECT u.id FROM users u JOIN subject_teachers st ON st.teacher_id = u.id WHERE u.full_name = ? AND st.subject_id = ?",
                (change.teacher_name, subject_id)
            )
            t = cursor.fetchone()
            if not t:
                raise HTTPException(status_code=404, detail="Teacher not assigned to this subject")
            fields.append("teacher_id = ?")
            values.append(t[0])

        if change.type:
            t = change.type.lower()
            if t not in ("lecture", "practice", "lab"):
                raise HTTPException(status_code=400, detail="Invalid lesson type")
            fields.append("type = ?")
            values.append(t)

        if change.lesson_date:
            fields.append("lesson_date = ?")
            values.append(change.lesson_date)

        if change.time:
            fields.append("time = ?")
            values.append(change.time)

        if change.room:
            fields.append("room = ?")
            values.append(change.room)

        if change.topic:
            fields.append("topic = ?")
            values.append(change.topic)

        if fields:
            sql = f"UPDATE lessons SET {', '.join(fields)} WHERE id = ?"
            values.append(lesson_id)
            cursor.execute(sql, tuple(values))

        if change.groups is not None:
            cursor.execute("DELETE FROM lesson_groups WHERE lesson_id = ?", (lesson_id,))
            for group_name in change.groups:
                cursor.execute("SELECT id FROM groups WHERE group_name = ?", (group_name,))
                group = cursor.fetchone()
                if not group:
                    continue
                cursor.execute("INSERT OR IGNORE INTO lesson_groups (lesson_id, group_id) VALUES (?, ?)", (lesson_id, group[0]))

        conn.commit()
        return {"message": "Lesson updated successfully"}
    finally:
        conn.close()


@router.delete("/delete_lesson/{lesson_id}")
def delete_lesson(lesson_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM lessons WHERE id = ?", (lesson_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Lesson not found")
        cursor.execute("DELETE FROM lesson_groups WHERE lesson_id = ?", (lesson_id,))
        cursor.execute("DELETE FROM attendance WHERE lesson_id = ?", (lesson_id,))
        cursor.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
        conn.commit()
        return {"message": "Lesson deleted successfully"}
    finally:
        conn.close()


@router.get("/lesson_groups/{lesson_id}")
def get_lesson_groups(lesson_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT g.group_name
            FROM lesson_groups lg
            JOIN groups g ON lg.group_id = g.id
            WHERE lg.lesson_id = ?
            """,
            (lesson_id,)
        )
        rows = cursor.fetchall()

        return {"lesson_id": lesson_id, "groups": [r[0] for r in rows]}

    finally:
        conn.close()


@router.get("/lesson_students/{lesson_id}")
def get_lesson_students(lesson_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT u.full_name
            FROM lesson_groups lg
            JOIN users u ON lg.group_id = u.group_id
            WHERE lg.lesson_id = ? AND u.role = 'student'
            """,
            (lesson_id,)
        )
        rows = cursor.fetchall()

        return {
            "lesson_id": lesson_id,
            "students": [r[0] for r in rows]
        }

    finally:
        conn.close()


@router.get("/attendance/{lesson_id}")
def get_attendance(lesson_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT u.full_name, a.status
            FROM attendance a
            JOIN users u ON a.student_id = u.id
            WHERE a.lesson_id = ?
            """,
            (lesson_id,)
        )
        rows = cursor.fetchall()

        return {
            "lesson_id": lesson_id,
            "attendance": [
                {"student": r[0], "status": r[1]} for r in rows
            ]
        }

    finally:
        conn.close()


@router.post("/mark_attendance")
def mark_attendance(mark: AttendanceMark):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM lessons WHERE id = ?", (mark.lesson_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Lesson not found")

        cursor.execute(
            "SELECT id FROM users WHERE full_name = ? AND role = 'student'",
            (mark.student_name,)
        )
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        student_id = student[0]

        status = mark.status.lower()
        if status not in ("present", "absent"):
            raise HTTPException(status_code=400, detail="Invalid status: present/absent only")

        cursor.execute(
            """
            INSERT INTO attendance (lesson_id, student_id, status)
            VALUES (?, ?, ?)
            ON CONFLICT(lesson_id, student_id)
            DO UPDATE SET status = excluded.status
            """,
            (mark.lesson_id, student_id, status)
        )

        conn.commit()
        return {"message": "Attendance marked successfully"}

    finally:
        conn.close()


@router.get("/grades")
def get_student_grades(student_name: str, subject_name: str | None = None):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id FROM users WHERE full_name = ? AND role = 'student'",
            (student_name,)
        )
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        student_id = student[0]

        if subject_name is None:
            cursor.execute(
                """
                SELECT s.subject_name, g.grade, g.date
                FROM grades g
                JOIN subjects s ON g.subject_id = s.id
                WHERE g.student_id = ?
                """,
                (student_id,)
            )
        else:
            cursor.execute(
                "SELECT id FROM subjects WHERE subject_name = ?",
                (subject_name,)
            )
            subject = cursor.fetchone()
            if not subject:
                raise HTTPException(status_code=404, detail="Subject not found")
            subject_id = subject[0]

            cursor.execute(
                """
                SELECT s.subject_name, g.grade, g.date
                FROM grades g
                JOIN subjects s ON g.subject_id = s.id
                WHERE g.student_id = ? AND g.subject_id = ?
                """,
                (student_id, subject_id)
            )

        rows = cursor.fetchall()

        return {
            "student": student_name,
            "grades": [
                {"subject": r[0], "grade": r[1], "date": r[2]}
                for r in rows
            ]
        }

    finally:
        conn.close()


@router.post("/add_grade")
def add_grade(g: GradeAdd):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (g.subject_name,))
        subject = cursor.fetchone()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        subject_id = subject[0]

        cursor.execute("SELECT id FROM users WHERE full_name = ? AND role = 'student'", (g.student_name,))
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        student_id = student[0]

        grade_value = g.grade
        date = g.date

        cursor.execute(
            "INSERT INTO grades (student_id, subject_id, grade, date) VALUES (?, ?, ?, ?)",
            (student_id, subject_id, grade_value, date)
        )
        conn.commit()
        return {"message": "Grade added successfully"}
    finally:
        conn.close()


@router.patch("/change_grade")
def change_grade(g: GradeChange):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (g.subject_name,))
        subject = cursor.fetchone()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        subject_id = subject[0]

        cursor.execute("SELECT id FROM users WHERE full_name = ? AND role = 'student'", (g.student_name,))
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        student_id = student[0]

        cursor.execute(
            "UPDATE grades SET grade = ? WHERE student_id = ? AND subject_id = ? AND date = ?",
            (g.new_grade, student_id, subject_id, g.date)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Grade entry not found")
        conn.commit()
        return {"message": "Grade updated successfully"}
    finally:
        conn.close()


@router.delete("/delete_grade/{grade_id}")
def delete_grade(grade_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM grades WHERE id = ?", (grade_id,))
        grade = cursor.fetchone()

        if not grade:
            raise HTTPException(status_code=404, detail="Grade not found")

        cursor.execute("DELETE FROM grades WHERE id = ?", (grade_id,))
        conn.commit()

        return {"message": "Grade deleted successfully"}
    finally:
        conn.close()


