from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from decouple import config

app = FastAPI()


class User(BaseModel):
    username: str
    password: str
    email: str


def mysql_connect():
    db_host = config('DB_HOST')
    db_user = config('DB_USER')
    db_password = config('DB_PASSWORD')
    db_database = config('DB_DATABASE')

    db = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_database
    )
    return db, db.cursor(dictionary=True)


@app.get("/users/get_user/{user_id}")
def get_user(user_id: int):
    db, cursor = mysql_connect()

    query = "SELECT * FROM Users WHERE UserID = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User of that given id not found")


@app.post("/users/create_user")
def create_user(user: User):
    db, cursor = mysql_connect()

    query = """
    INSERT INTO Users (Username, Password, Email)
    VALUES (%s, %s, %s)
    """
    data = (
        user.username,
        user.password,
        user.email
    )
    cursor.execute(query, data)
    db.commit()
    cursor.close()
    db.close()

    return {"message": "User created successfully."}


@app.put("/users/update_user/{user_id}")
def update_user(user_id: int, user: User):
    db, cursor = mysql_connect()

    cursor.execute("SELECT * FROM Users WHERE UserID = %s", (user_id,))
    existing_user = cursor.fetchone()
    if not existing_user:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="User of that id not found")

    query = """
    UPDATE Users
    SET Username = %s, Password = %s, Email = %s
    WHERE UserID = %s
    """
    update_values = (
        user.username,
        user.password,
        user.email,
        user_id
    )

    cursor.execute(query, update_values)
    db.commit()
    cursor.close()
    db.close()

    return {"message": "User updated successfully."}


@app.delete("/users/delete_user/{user_id}")
def delete_user(user_id: int):
    db, cursor = mysql_connect()

    cursor.execute("SELECT * FROM Users WHERE UserID = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="User of that id not found")

    query = "DELETE FROM Users WHERE UserID = %s"
    cursor.execute(query, (user_id,))
    db.commit()
    cursor.close()
    db.close()

    return {"message": "User deleted successfully."}
