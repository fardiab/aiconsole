from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from fastapi import Request
import httpx
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()  # Load environment variables from .env

router = FastAPI()

# OAuth2 Configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")

# OAuth2 Password Bearer token URL for token verification (optional, if using tokens)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Step 1: Redirect to GitHub OAuth2 for authentication
@router.get("/auth/login", response_model=RedirectResponse)
async def login():
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}&scope=user:email"
    return RedirectResponse(url=github_auth_url)


# Step 2: Handle the GitHub OAuth2 callback and exchange code for an access token
@router.get("/auth/callback", response_model=dict)
async def auth_callback(code: str):
    # Exchange the code for an access token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI,
            },
            headers={"Accept": "application/json"},
        )
        data = response.json()
        access_token = data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authentication failed")

    # Step 3: Use the access token to fetch the user profile
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = response.json()

    if "login" not in user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch user data")

    # Successfully authenticated, return user data (or redirect to a protected page)
    return {"message": "Authentication successful", "user": user_data}


# Example of a protected route that requires authentication
@router.get("/protected", response_model=dict)
async def protected_route(token: str = Depends(oauth2_scheme)):
    return {"message": "This is a protected route", "user": token}
