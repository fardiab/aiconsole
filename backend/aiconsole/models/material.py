from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    content = Column(Text)
    file_url = Column(String) 

    def __repr__(self):
        return f"<Material(id={self.id}, name={self.name})>"
