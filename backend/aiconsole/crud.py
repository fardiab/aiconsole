from sqlalchemy.orm import Session
from .models import Material
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from .database import init_db, get_db
from .schemas.material import MaterialResponse
from aiconsole import crud
from crud_one import material as material_crud
from aiconsole.schemas import material as material_schema


router = APIRouter()

init_db()


def bulk_delete_materials(db: Session, material_ids: List[int]) -> bool:
    materials = db.query(Material).filter(Material.id.in_(material_ids)).all()
    if not materials:
        return False
    for material in materials:
        db.delete(material)
    db.commit()
    return True


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


@router.post("/materials/", response_model=material_schema.MaterialOut)
def create(material: material_schema.MaterialCreate, db: Session = Depends(get_db)):
    return material_crud.create_material(db, material)


@router.get("/materials/", response_model=list[material_schema.MaterialOut])
def read_all(db: Session = Depends(get_db)):
    return material_crud.get_all_materials(db)


@router.get("/materials/{material_id}", response_model=material_schema.MaterialOut)
def read_one(material_id: int, db: Session = Depends(get_db)):
    material = material_crud.get_material(db, material_id)
    if material is None:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.put("/materials/{material_id}", response_model=material_schema.MaterialOut)
def update(material_id: int, material_update: material_schema.MaterialUpdate, db: Session = Depends(get_db)):
    material = material_crud.update_material(db, material_id, material_update)
    if material is None:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.delete("/materials/{material_id}", status_code=204)
def delete(material_id: int, db: Session = Depends(get_db)):
    success = material_crud.delete_material(db, material_id)
    if not success:
        raise HTTPException(status_code=404, detail="Material not found")
    return


@router.delete("/materials/bulk-delete", status_code=204)
def bulk_delete(material_ids: List[int], db: Session = Depends(get_db)):
    success = crud.bulk_delete_materials(db, material_ids)
    if not success:
        raise HTTPException(status_code=404, detail="Materials not found")
    return {"detail": "Materials successfully deleted"}
