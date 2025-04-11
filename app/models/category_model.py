from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    type = Column(Enum('EXPENSE', 'INCOME', name='category_type'), nullable=False)
     
     
    transactions = relationship("FinancialTransaction", back_populates="category")