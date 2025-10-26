import sqlite3

conn = sqlite3.connect("sql/database.db")
cursor = conn.cursor()

def addUser():
    name = input("Enter username: ")
    password = input("Enter password: ")
    role = input("Enter role (admin / teacher / student): ").lower()

    if role == "admin":
        cursor.execute(
            "INSERT INTO users (full_name, password, role) VALUES (?, ?, ?)",
            (name, password, role)
        )

    else:
        group = input("Enter group name: ")

        cursor.execute("SELECT id FROM groups WHERE group_name = ?", (group,))
        result = cursor.fetchone()

        if result:
            group_id = result[0]
            cursor.execute(
                "INSERT INTO users (full_name, password, role, group_id) VALUES (?, ?, ?, ?)",
                (name, password, role, group_id)
            )
        else:
            print("No group found with that name.")
            return

    conn.commit()
    print("User added successfully.")


def deleteUser():
    deleteName = input("Enter username to delete: ")
    cursor.execute("SELECT id FROM users WHERE full_name = ?", (deleteName,))
    if cursor.fetchone():
        cursor.execute("DELETE FROM users WHERE full_name = ?", (deleteName,))
        conn.commit()
        print("User deleted successfully.")
    else:
        print("No User found with that name.")


def changeUser():
    name = input("Enter username to change something: ")
    changing = input("What do you want to change in this user? (Name / Password / Role / Group): ").lower()

    if changing == "name":
        new_value = input("Enter new name: ")
        cursor.execute("UPDATE users SET full_name = ? WHERE full_name = ?", (new_value, name))

    elif changing == "password":
        new_value = input("Enter new password: ")
        cursor.execute("UPDATE users SET password = ? WHERE full_name = ?", (new_value, name))

    elif changing == "role":
        new_value = input("Enter new role (admin / teacher / student): ")
        cursor.execute("UPDATE users SET role = ? WHERE full_name = ?", (new_value, name))

    elif changing == "group":
        new_group = input("Enter new group name: ")
        cursor.execute("SELECT id FROM groups WHERE group_name = ?", (new_group,))
        result = cursor.fetchone()

        if result:
            group_id = result[0]
            cursor.execute("UPDATE users SET group_id = ? WHERE full_name = ?", (group_id, name))
        else:
            print("No group found with that name.")
            return

    else:
        print("Invalid option")
        return

    conn.commit()
    print("User updated successfully.")


def createGroup():
    name = input("Enter name of the group: ")
    curator_name = input("Enter curator name for the group: ")

    cursor.execute("SELECT id FROM groups WHERE group_name = ?", (name,))
    if cursor.fetchone():
        print("Group with this name already exists.")
        return

    cursor.execute("SELECT id FROM users WHERE full_name = ? AND role = 'teacher'", (curator_name,))
    result = cursor.fetchone()

    if result:
        curator_id = result[0]
        cursor.execute("INSERT INTO groups (group_name, curator_id) VALUES (?, ?)", (name, curator_id))
        conn.commit()
        print("Group created successfully.")
    else:
        print("No teacher found with that name.")


def changeGroup():
    name = input("Enter group name to change something: ")
    changing = input("What do you want to change in this group? (Name / Curator): ").lower()

    if changing == "name":
        new_value = input("Enter new group name: ")
        cursor.execute("UPDATE groups SET group_name = ? WHERE group_name = ?", (new_value, name))

    elif changing == "curator":
        new_curator = input("Enter new curator full name: ")
        cursor.execute("SELECT id FROM users WHERE full_name = ? AND role = 'teacher'", (new_curator,))
        result = cursor.fetchone()

        if result:
            curator_id = result[0]
            cursor.execute("UPDATE groups SET curator_id = ? WHERE group_name = ?", (curator_id, name))
        else:
            print("No teacher found with that name.")
            return

    else:
        print("Invalid option")
        return

    conn.commit()
    print("Group updated successfully.")


def deleteGroup():
    deleteName = input("Enter group name to delete: ")
    cursor.execute("SELECT id FROM groups WHERE group_name = ?", (deleteName,))
    if cursor.fetchone():
        cursor.execute("DELETE FROM groups WHERE group_name = ?", (deleteName,))
        conn.commit()
        print("Group deleted successfully.")
    else:
        print("No group found with that name.")


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


#def changeSubject():
#def deleteSubject():
#def changeAttendacne():


#cursor.execute("SELECT * FROM users")
#print(cursor.fetchall())

#addUser()
#deleteUser()
#cursor.execute("SELECT * FROM users")
#print(cursor.fetchall())

#changeUser()
#cursor.execute("SELECT * FROM users")
#print(cursor.fetchall())

#createGroup()

#cursor.execute("SELECT * FROM users")
#print(cursor.fetchall())
#cursor.execute("SELECT * FROM groups")
#print(cursor.fetchall())

#changeGroup()
#cursor.execute("SELECT * FROM users")
#print(cursor.fetchall())
#cursor.execute("SELECT * FROM groups")
#print(cursor.fetchall())