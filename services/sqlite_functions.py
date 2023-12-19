from flask import g
import sqlite3
import os
from services.general_functions import generate_user_id

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db_path = os.path.abspath('database/SQLite/users.db')
        db = g._database = sqlite3.connect(db_path)
        create_table(db)
    return db

def create_table(db):
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            firstname TEXT,
            lastname TEXT,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT
        );   
    ''')
    db.commit()

def check_user(email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f'''
        SELECT * FROM users WHERE email = ?
''', (email,))
    data = cursor.fetchone()
    db.commit()
    return data

def auth(email, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f'''
        SELECT id, firstname, lastname, email, role FROM users WHERE email = ? AND password = ?
    ''', (email, password))
    data = cursor.fetchone()
    db.commit()
    return data

def add_user(firstname,lastname,email,password, role):
    db = get_db()
    cursor = db.cursor()
    try:
        user_id = generate_user_id(email)
        print('generated user id:',user_id)
        # Adding user
        cursor.execute('''
            INSERT INTO users (id,firstname,lastname,email,password, role) VALUES (?,?,?,?,?,?); 
    ''', (user_id,firstname,lastname,email,password, role))
        db.commit()

        return user_id
    except:
        return False
    
def get_by_id(id):
    print(id)
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
            SELECT id, firstname, lastname, email, role FROM users where id = ?
''', (id,))
    data = cursor.fetchone()
    db.commit()
    return data


def existing_data(column):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f'''
        SELECT {column} FROM users
''')
    data = cursor.fetchall()
    db.commit
    print(data)
    existing = [el[0] for el in data]
    return existing
