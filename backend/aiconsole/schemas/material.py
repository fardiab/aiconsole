from pydantic import BaseModel


class MaterialBase(BaseModel):
    name: str
    description: str = ""
    content: str
    file_url: str = ""


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    name: str = None
    description: str = None
    content: str = None
    file_url: str = None


class MaterialOut(MaterialBase):
    id: int

    class Config:
        orm_mode = True
