from pydantic import BaseModel
from typing import Optional


class MaterialBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: str
    file_url: Optional[str] = None


class MaterialCreate(MaterialBase):
    pass


class MaterialResponse(MaterialBase):
    id: int

    class Config:
        from_attributes = True
