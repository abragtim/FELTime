import sqlite3
from sqlite3.dbapi2 import Cursor

db = sqlite3.connect('server.db')
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS users (
    login TEXT,
    password TEXT,
    cash BIGINT
)""")

db.commit()

user_login = input('Login:')
user_password = input('Password:')

sql.execute(f"SELECT login FROM users WHERE login = '{user_login}'")
if sql.fetchone() is None:
    sql.execute(f"INSERT INTO users VALUES (?, ?, ?)", (user_login, user_password, 0))
    db.commit()

    print('Регистрация прошла успешно')
else:
    print('Такая запись уже имеется')
    for value in sql.execute("SELECT * FROM users"):
        print(value[0])


