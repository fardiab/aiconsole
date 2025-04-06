from sqlalchemy.orm import Session
from .models import Material
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from .database import init_db, get_db
from .schemas.material import MaterialResponse
from . import crud


router = APIRouter()

init_db()


@router.get("/materials/", response_model=List[MaterialResponse])
def get_materials(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_materials(db, skip=skip, limit=limit)


@router.get("/materials/{material_id}", response_model=MaterialResponse)
def get_material_by_id(material_id: int, db: Session = Depends(get_db)):
    material = crud.get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.post("/materials/", response_model=MaterialResponse)
def create_material(
    name: str, description: str, content: str, file_url: Optional[str] = None, db: Session = Depends(get_db)
):
    return crud.create_material(db, name, description, content, file_url)
