from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.configs.database import Base


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    source_urls = Column(Text)
    posted = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())