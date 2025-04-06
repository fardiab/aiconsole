import os
from sqlalchemy.orm import Session
from crud.material import create_material
from aiconsole.schemas import MaterialCreate
from aiconsole.database import SessionLocal

MATERIALS_DIR = "./materials"


def migrate_materials():
    db: Session = SessionLocal()
    for filename in os.listdir(MATERIALS_DIR):
        path = os.path.join(MATERIALS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        create_material(
            db,
            MaterialCreate(
                name=filename, content=content, type="markdown", path=path  # Or determine based on file extension
            ),
        )


if __name__ == "__main__":
    migrate_materials()
