from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str  # In real-life, store hashed passwords in the database


class UserInDB(User):
    hashed_password: str
