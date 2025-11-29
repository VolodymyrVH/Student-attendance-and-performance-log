from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_connection
import hashlib

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginData(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: LoginData):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password, role FROM users WHERE username = ?", (data.username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id, hashed_password, role = user
    if hashlib.sha256(data.password.encode()).hexdigest() != hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = f"fake-token-for-user-{user_id}"
    return {"token": token, "user_id": user_id, "role": role}
