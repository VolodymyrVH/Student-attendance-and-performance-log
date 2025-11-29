import sqlite3
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from database import get_connection, init_db

router = APIRouter(prefix="/student", tags=["student"])


@router.get("/lessons/{teacher_name}")
def get_lessons_by_teacher(teacher_name: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT l.id, s.subject_name, u.full_name, l.lesson_date, l.time, l.room, l.topic, l.type
            FROM lessons l
            JOIN subjects s ON l.subject_id = s.id
            JOIN users u ON l.teacher_id = u.id
            WHERE u.full_name = ?
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
                "type": r[7]
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


@router.get("/get_group/{group_id}")
def getGroup(group_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, group_name, curator_id FROM groups WHERE id = ?",
            (group_id,)
        )
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Group not found")

        return {
            "id": row[0],
            "group_name": row[1],
            "curator_id": row[2]
        }

    finally:
        conn.close()


@router.get("/get_user/{user_id}")
def getUser(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, full_name, role, group_id FROM users WHERE id = ?", 
            (user_id,)
        )
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": row[0],
            "full_name": row[1],
            "role": row[2],
            "group_id": row[3]
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


@router.get("/grades")
def get_my_grades(student_id: int, subject_name: str | None = None):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT full_name FROM users WHERE id = ? AND role = 'student'", (student_id,))
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        student_name = student[0]

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
            cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (subject_name,))
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
