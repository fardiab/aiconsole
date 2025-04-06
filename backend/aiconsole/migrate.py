import os
from sqlalchemy.orm import Session
from .crud import create_material  # or your actual crud module path


def migrate_files_to_db(db: Session, directory_path: str):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                content = f.read()
            create_material(
                db=db, name=filename, description="File migrated from filesystem", content=content, file_url=file_path
            )
