from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import get_connection, init_db
from admin import router as admin_router

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

app.include_router(admin_router)


#items = []
"""
class Item(BaseModel):
    text: str = None
    is_done: bool = False


@app.get("/")
def root():
    return {"Hello": "World"}


@app.post("/items")
def create_item(item: Item):
    items.append(item)
    return items


@app.get("/items", response_model=list[Item])
def list_items(limit: int = 10):
    return items[:limit]


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    if item_id < len(items):
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail="Item not found")
"""