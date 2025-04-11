from decimal import Decimal
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from enum import Enum 
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from sqlalchemy import Enum
from app.models.base import Base

class TransactionType(PyEnum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
class FinancialTransaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(10, 2), nullable=False)  # Positive for income, negative for expenses
    date = Column(Date, default=datetime.utcnow().date(), nullable=False)
    description = Column(String(100), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
   

    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))

    account = relationship("Account", back_populates="transactions", lazy="selectin")
    user = relationship("User", back_populates="transactions", lazy="selectin")
    category = relationship("Category", back_populates="transactions", lazy="selectin")