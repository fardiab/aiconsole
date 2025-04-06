from sqlalchemy.orm import Session
from models.material import Material
from schemas.material import MaterialCreate, MaterialUpdate


def create_material(db: Session, material: MaterialCreate) -> Material:
    db_material = Material(**material.dict())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material


def get_material(db: Session, material_id: int) -> Material:
    return db.query(Material).filter(Material.id == material_id).first()


def get_material_by_name(db: Session, name: str) -> Material:
    return db.query(Material).filter(Material.name == name).first()


def get_all_materials(db: Session) -> list[Material]:
    return db.query(Material).all()


def update_material(db: Session, material_id: int, material_update: MaterialUpdate) -> Material:
    material = db.query(Material).get(material_id)
    if not material:
        return None
    for key, value in material_update.dict(exclude_unset=True).items():
        setattr(material, key, value)
    db.commit()
    db.refresh(material)
    return material


def delete_material(db: Session, material_id: int) -> bool:
    material = db.query(Material).get(material_id)
    if not material:
        return False
    db.delete(material)
    db.commit()
    return True
