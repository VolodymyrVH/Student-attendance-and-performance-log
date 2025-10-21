import sqlite3

conn = sqlite3.connect("sql/database.db")
cursor = conn.cursor()


#checking creating of tables
#cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#print(cursor.fetchall())

#adding some data
#cursor.execute("""
#INSERT INTO users (full_name, password, role)
#               VALUES 
#                    ('Admin Test', '1234', 'admin'),
#                    ('Student', '4321', 'student'),
#                    ('Teacher', '1234', 'teacher');
#               """)
#conn.commit()
#cursor.execute("SELECT full_name, role FROM users WHERE role='admin';")
#print(cursor.fetchall())

#cheking tables
#cursor.execute("SELECT * FROM users")
#print(cursor.fetchall())

def addUser():
    name = input("Enter username: ")
    password = input("Enter password: ")
    role = input("Enter role: ")

    cursor.execute(f"""
    INSERT INTO users (full_name, password, role)
                VALUES 
                        ('{name}', '{password}', '{role}');
                """)
    conn.commit()

def deleteUser():
    deleteName = input("Enter username to delete: ")
    cursor.execute("DELETE FROM users WHERE full_name = ?", (deleteName,))
    conn.commit()


#addUser()
cursor.execute("SELECT * FROM users")
print(cursor.fetchall())

deleteUser()
cursor.execute("SELECT * FROM users")
print(cursor.fetchall())

conn.commit()
conn.close()