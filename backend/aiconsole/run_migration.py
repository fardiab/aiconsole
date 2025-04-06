from .database import SessionLocal
from .migrate import migrate_files_to_db

db = SessionLocal()
directory_path = "F:/Python/aiconsole/materials"  # path to your files

migrate_files_to_db(db, directory_path)
db.close()
