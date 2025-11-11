import sqlite3
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from database import get_connection, init_db

router = APIRouter(prefix="/admin", tags=["admin"])


class UserCreate(BaseModel):
    full_name: str
    password: str
    role: str
    group_id: int | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    password: str | None = None
    role: str | None = None
    group_id: int | None = None


class GroupCreate(BaseModel):
    group_name: str
    curator_name: str


class GroupChange(BaseModel):
    group_name: str
    curator_name: str | None = None


class SubjectCreate(BaseModel):
    subject_name: str


class SubjectChange(BaseModel):
    subject_name: str


@router.post("/add_user")
def addUser(user: UserCreate):
    conn = get_connection()
    cursor = conn.cursor()

    role = user.role.lower()

    if role not in ["admin", "teacher", "student"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'admin', 'teacher', or 'student'.")

    if role == "admin":
        cursor.execute(
            "INSERT INTO users (full_name, password, role) VALUES (?, ?, ?)",
            (user.full_name, user.password, role)
        )
    else:
        if not user.group_id:
            raise HTTPException(status_code=400, detail="Group ID required")

        cursor.execute("SELECT id FROM groups WHERE id = ?", (user.group_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Group not found")

        group_id = result[0]
        cursor.execute(
            "INSERT INTO users (full_name, password, role, group_id) VALUES (?, ?, ?, ?)",
            (user.full_name, user.password, role, group_id)
        )

    conn.commit()
    conn.close()
    return {"message": "User added successfully."}


@router.delete("/delete_user/{user_id}")
def deleteUser(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if cursor.fetchone():
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return {"message": "User deleted successfully."}
    else:
        return {"message": "User not found."}


@router.patch("/change_user/{user_id}")
def changeUser(user_id: int, user: UserUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.full_name:
        cursor.execute("UPDATE users SET full_name = ? WHERE id = ?", (user.full_name, user_id))
        return {"message": "User updated successfully."}
    
    if user.password:
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (user.password, user_id))
        return {"message": "User updated successfully."}
    
    if user.role:
        role = user.role.lower()
        if role not in ["admin", "teacher", "student"]:
            raise HTTPException(status_code=400, detail="Invalid role. Must be 'admin', 'teacher', or 'student'.")
        cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        return {"message": "User updated successfully."}

    if user.group_id is not None:
        cursor.execute("SELECT id FROM groups WHERE id = ?", (user.group_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Group not found")
        cursor.execute("UPDATE users SET group_id = ? WHERE id = ?", (user.group_id, user_id))
        return {"message": "User updated successfully."}


@router.post("/create_group")
def createGroup(group: GroupCreate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM groups WHERE group_name = ?", (group.group_name,))
    if cursor.fetchone():
        print("Group with this name already exists.")
        return

    cursor.execute("SELECT id FROM users WHERE full_name = ? AND role = 'teacher'", (group.curator_name,))
    result = cursor.fetchone()

    if result:
        curator_id = result[0]
        cursor.execute("INSERT INTO groups (group_name, curator_id) VALUES (?, ?)", (group.group_name, curator_id))
        conn.commit()
        return {"message": "Group created successfully."}
    else:
        return {"message": "No teacher found with that name."}


@router.patch("/change_group/{group_name}")
def changeGroup(group_name: str, group: GroupChange):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM groups WHERE group_name = ?", (group_name,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Group not found")

    if group.group_name:
        cursor.execute("UPDATE groups SET group_name = ? WHERE group_name = ?", (group.group_name, group_name))
        return {"message": "Group updated successfully."}

    if group.curator_name:
        cursor.execute("SELECT id FROM users WHERE full_name = ? AND role = 'teacher'", (group.curator_name,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Curator not found")
        cursor.execute("UPDATE groups SET curator_id = ? WHERE group_name = ?", (result[0], group_name))
        return {"message": "Group updated successfully."}
    conn.commit()
    return {"message": "Group updated successfully."}


@router.delete("/delete_group/{group_name}")
def deleteGroup(group_name: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM groups WHERE group_name = ?", (group_name,))
    if cursor.fetchone():
        cursor.execute("DELETE FROM groups WHERE group_name = ?", (group_name,))
        conn.commit()
        return {"message": "Group deleted successfully."}
    else:
        return {"message": "No group found with that name."}


def addSubject():
    name = input("Enter subject name: ")
    group_name = input("Enter group: ")
    teacher_name = input("Enter teacher: ")

    cursor.execute("SELECT id FROM groups WHERE group_name = ?", (group_name,))
    group_result = cursor.fetchone()
    if not group_result:
        print("No group found with that name.")
        return
    group_id = group_result[0]

    cursor.execute("SELECT id FROM users WHERE full_name = ? AND role = 'teacher'", (teacher_name,))
    teacher_result = cursor.fetchone()
    if not teacher_result:
        print("No teacher found with that name.")
        return
    teacher_id = teacher_result[0]

    cursor.execute(
        "INSERT INTO subjects (subject_name, group_id, teacher_id) VALUES (?, ?, ?)",
        (name, group_id, teacher_id)
    )
    conn.commit()
    print("Subject added successfully.")


def changeSubject():
    name = input("Enter subject name to change something: ")
    changing = input("What do you want to change in this group? (Name / Teacher): ").lower()

    if changing == "name":
        new_value = input("Enter new subject name: ")
        cursor.execute("UPDATE subjects SET subject_name = ? WHERE subject_name = ?", (new_value, name))

    elif changing == "teacher":
        new_teacher = input("Enter new teacher full name: ")
        cursor.execute("SELECT id FROM users WHERE full_name = ? AND role = 'teacher'", (new_teacher,))
        result = cursor.fetchone()

        if result:
            teacher_id = result[0]
            cursor.execute("UPDATE subjects SET teacher_id = ? WHERE subject_name = ?", (teacher_id, name))
        else:
            print("No teacher found with that name.")
            return

    else:
        print("Invalid option")
        return

    conn.commit()
    print("Subject updated successfully.")


def deleteSubject():
    deleteName = input("Enter subject name to delete: ")
    cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (deleteName,))
    if cursor.fetchone():
        cursor.execute("DELETE FROM subjects WHERE subject_name = ?", (deleteName,))
        conn.commit()
        print("Subject deleted successfully.")
    else:
        print("No subject found with that name.")

