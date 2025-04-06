from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from aiconsole.security import hash_password, create_access_token, verify_password
from aiconsole.dependencies import get_current_user

app = FastAPI()

# In-memory database for demonstration
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "hashed_password": hash_password("testpassword"),  # Hashed password
    }
}


class UserInLogin(BaseModel):
    username: str
    password: str


@app.post("/token")
def login_for_access_token(user: UserInLogin):
    fake_user = fake_users_db.get(user.username)
    if not fake_user or not verify_password(user.password, fake_user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# A protected route that requires authentication
@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "Protected data", "user": current_user}
