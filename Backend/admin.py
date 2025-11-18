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
    group_name: str | None = None
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
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'admin', 'teacher', or 'student'.")

    try:
        if role == "admin":
            cursor.execute(
                "INSERT INTO users (full_name, password, role) VALUES (?, ?, ?)",
                (user.full_name, user.password, role)
            )
        else:
            if not user.group_id:
                conn.close()
                raise HTTPException(status_code=400, detail="Group ID required")

            cursor.execute("SELECT id FROM groups WHERE id = ?", (user.group_id,))
            result = cursor.fetchone()

            if not result:
                conn.close()
                raise HTTPException(status_code=404, detail="Group not found")

            cursor.execute(
                "INSERT INTO users (full_name, password, role, group_id) VALUES (?, ?, ?, ?)",
                (user.full_name, user.password, role, user.group_id)
            )

        conn.commit()
        return {"message": "User added successfully."}
    finally:
        conn.close()


@router.delete("/delete_user/{user_id}")
def deleteUser(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return {"message": "User deleted successfully."}
        else:
            return {"message": "User not found."}
    finally:
        conn.close()


@router.patch("/change_user/{user_id}")
def changeUser(user_id: int, user: UserUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="User not found")
        
        fields = []
        values = []
        
        if user.full_name:
            fields.append("full_name = ?")
            values.append(user.full_name)
        
        if user.password:
            fields.append("password = ?")
            values.append(user.password)
        
        if user.role:
            role = user.role.lower()
            if role not in ["admin", "teacher", "student"]:
                raise HTTPException(status_code=400, detail="Invalid role. Must be 'admin', 'teacher', or 'student'.")
            fields.append("role = ?")
            values.append(role)

        if user.group_id is not None:
            cursor.execute("SELECT id FROM groups WHERE id = ?", (user.group_id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Group not found")
            fields.append("group_id = ?")
            values.append(user.group_id)
        
        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        sql = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        values.append(user_id)

        cursor.execute(sql, tuple(values))
        conn.commit()
        return {"message": "User updated successfully."}
        
    finally:
        conn.close()


@router.post("/create_group")
def createGroup(group: GroupCreate):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM groups WHERE group_name = ?", (group.group_name,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Group with that name already exists.")

        cursor.execute("SELECT id FROM users WHERE full_name = ? AND (role = 'teacher' OR role = 'admin')", (group.curator_name,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="No teacher found with that name.")
        

        curator_id = result[0]
        cursor.execute("INSERT INTO groups (group_name, curator_id) VALUES (?, ?)", (group.group_name, curator_id))
        conn.commit()
        return {"message": "Group created successfully."}
        
    finally:
        conn.close()


@router.patch("/change_group/{group_name}")
def changeGroup(group_name: str, group: GroupChange):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM groups WHERE group_name = ?", (group_name,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Group not found")
        
        updated = False
        if group.group_name:
            cursor.execute("UPDATE groups SET group_name = ? WHERE group_name = ?", (group.group_name, group_name))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Group with that name already exists.")
            cursor.execute("UPDATE groups SET group_name = ? WHERE group_name = ?", (group.group_name, group_name))
            updated = True

        if group.curator_name:
            cursor.execute("SELECT id FROM users WHERE full_name = ? AND role = 'teacher'", (group.curator_name,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Curator not found")
            cursor.execute("UPDATE groups SET curator_id = ? WHERE group_name = ?", (result[0], group_name))
            updated = True
        
        if not updated:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        conn.commit()
        return {"message": "Group updated successfully."}

    finally:
        conn.close()


@router.delete("/delete_group/{group_name}")
def deleteGroup(group_name: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM groups WHERE group_name = ?", (group_name,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM groups WHERE group_name = ?", (group_name,))
            conn.commit()
            return {"message": "Group deleted successfully."}
        else:
            return {"message": "No group found with that name."}
    
    finally:
        conn.close()


@router.post("/add_subject")
def add_subject(subject: SubjectCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (subject.subject_name,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Subject with that name already exists.")

        cursor.execute(
            "INSERT INTO subjects (subject_name) VALUES (?)", (subject.subject_name,)
        )
        conn.commit()
        return {"message": "Subject added successfully."}
    finally:
        conn.close()



@router.patch("/change_subject/{subject_name}")
def changeSubject(subject_name: str, subject: SubjectChange):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (subject_name,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Subject not found")
        
        if not subject.subject_name:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (subject.subject_name,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="A subject with the new name already exists.")
        
        cursor.execute("UPDATE subjects SET subject_name = ? WHERE subject_name = ?", (subject.subject_name, subject_name))
        conn.commit()
        return {"message": "Subject updated successfully."}
    finally:
        conn.close()


@router.delete("/delete_subject/{subject_name}")
def deleteSubject(subject_name: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM subjects WHERE subject_name = ?", (subject_name,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM subjects WHERE subject_name = ?", (subject_name,))
            conn.commit()
            return {"message": "Subject deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail="No subject found with that name.")
    finally:
        conn.close()