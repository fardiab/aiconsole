# The AIConsole Project
#
# Copyright 2023 10Clouds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import cast

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from fastapi import Request
import httpx
import os
from dotenv import load_dotenv
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from aiconsole.api.endpoints.registry import materials
from aiconsole.api.endpoints.services import (
    AssetWithGivenNameAlreadyExistError,
    Materials,
)
from aiconsole.api.utils.asset_exists import asset_exists, asset_path
from aiconsole.api.utils.asset_get import asset_get
from aiconsole.api.utils.asset_status_change import asset_status_change
from aiconsole.api.utils.status_change_post_body import StatusChangePostBody
from aiconsole.core.assets.get_material_content_name import get_material_content_name
from aiconsole.core.assets.materials.material import (
    Material,
    MaterialContentType,
    MaterialWithStatus,
)
from aiconsole.core.assets.types import AssetLocation, AssetStatus, AssetType
from aiconsole.core.project import project
from aiconsole.utils.git_utils import GitRepository
from pydantic import BaseModel

router = APIRouter()


def get_default_content_for_type(type: MaterialContentType):
    if type == MaterialContentType.STATIC_TEXT:
        return """

content, content content

## Sub header

Bullets in sub header:
* Bullet 1
* Bullet 2
* Bullet 3

""".strip()
    elif type == MaterialContentType.DYNAMIC_TEXT:
        return """

import random

async def content(context):
    samples = ['sample 1' , 'sample 2', 'sample 3', 'sample 4']
    return f'''
# Examples of great content
{random.sample(samples, 2)}

'''.strip()

""".strip()
    elif type == MaterialContentType.API:
        return """

'''
Add here general API description
'''

def create():
    '''
    Add comment when to use this function, and add example of usage:
    ```python
        create()
    ```
    '''
    print("Created")


def print_list():
    '''
    Use this function to print 'List'.
    Sample of use:
    ```python
        print_list()
    ```

    '''
    print("List")



def fibonacci(n):
    '''
    Use it to calculate and return the nth term of the Fibonacci sequence.
    Sample of use:
    ```python
      fibonacci(10)
    ```
    '''
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)
""".strip()
    else:
        raise ValueError("Invalid material content type")


materials_repo = GitRepository("F:/Python/aiconsole/materials")


class CommitMessage(BaseModel):
    message: str


@router.post("/materials/commit/")
def commit_materials(message: CommitMessage):
    try:
        materials_repo.commit_changes(message.message)
        return {"status": "success", "message": "Changes committed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/materials/changelog/")
def get_materials_changelog():
    try:
        changelog = materials_repo.get_changelog()
        return {"status": "success", "changelog": changelog}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{material_id}")
async def get_material(request: Request, material_id: str):
    type = cast(MaterialContentType, request.query_params.get("type", ""))

    return await asset_get(
        request,
        AssetType.MATERIAL,
        material_id,
        lambda: MaterialWithStatus(
            id="new_" + get_material_content_name(type).lower(),
            name="New " + get_material_content_name(type),
            content_type=type,
            usage="",
            usage_examples=[],
            status=AssetStatus.ENABLED,
            defined_in=AssetLocation.PROJECT_DIR,
            override=False,
            content=get_default_content_for_type(type),
        ),
    )


@router.patch("/{asset_id}")
async def partially_update_material(
    asset_id: str, material: Material, materials_service: Materials = Depends(materials)
):
    try:
        await materials_service.partially_update_material(material_id=asset_id, material=material)
    except AssetWithGivenNameAlreadyExistError:
        raise HTTPException(status_code=400, detail="Material with given name already exists")


@router.post("/{asset_id}")
async def create_material(asset_id: str, material: Material, materials_service: Materials = Depends(materials)):
    try:
        await materials_service.create_material(material_id=asset_id, material=material)
    except AssetWithGivenNameAlreadyExistError:
        raise HTTPException(status_code=400, detail="Material with given name already exists")


@router.post("/{material_id}/status-change")
async def material_status_change(material_id: str, body: StatusChangePostBody):
    return await asset_status_change(AssetType.MATERIAL, material_id, body)


@router.delete("/{material_id}")
async def delete_material(material_id: str):
    try:
        await project.get_project_materials().delete_asset(material_id)
        return JSONResponse({"status": "ok"})
    except KeyError:
        raise HTTPException(status_code=404, detail="Material not found")


@router.get("/{asset_id}/exists")
async def material_exists(request: Request, asset_id: str):
    return await asset_exists(AssetType.MATERIAL, request, asset_id)


@router.get("/{asset_id}/path")
async def material_path(request: Request, asset_id: str):
    return asset_path(AssetType.MATERIAL, request, asset_id)


# OAuth2 Configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")

# OAuth2 Password Bearer token URL for token verification (optional, if using tokens)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Step 1: Redirect to GitHub OAuth2 for authentication
@router.get("/auth/login")
async def login():
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}&scope=user:email"
    return RedirectResponse(url=github_auth_url)

@router.get("/auth/callback")
async def auth_callback(code: str):
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

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = response.json()

    if "login" not in user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch user data")

    return {"message": "Authentication successful", "user": user_data}@app.get("/auth/login")
async def login():
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}&scope=user:email"
    return RedirectResponse(url=github_auth_url)

@router.get("/auth/callback")
async def auth_callback(code: str):
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

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = response.json()

    if "login" not in user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch user data")

    return {"message": "Authentication successful", "user": user_data}
