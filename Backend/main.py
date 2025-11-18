from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import get_connection, init_db
from admin import router as admin_router
from teacher import router as teacher_router

app = FastAPI(title="Student Attendance and Performance Log API")


@app.get("/users")
def get_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"users": users}


@app.get("/groups")
def get_groups():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM groups")
    groups = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"groups": groups}


@app.get("/subjects")
def get_subjects():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"subjects": subjects}

@app.get("/lessons")
def get_lessons():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lessons")
    lessons = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"lessons": lessons}

app.include_router(admin_router)
app.include_router(teacher_router)
