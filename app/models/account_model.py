from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Boolean
from decimal import Decimal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.models.base import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    balance = Column(Numeric(7, 2), default=Decimal('0.00'))
    is_credit = Column(Boolean, default=False)

    # Se for crédito:  
    credit_limit = Column(Numeric(15, 2), default=Decimal('0.00'))  # Limite total  
    used_credit = Column(Numeric(15, 2), default=Decimal('0.00')) # Limite utilizado
    due_day = Column(Integer, nullable=True)
    
    # Referencia um User
    user_id = Column(Integer, ForeignKey('users.id'),  nullable=False)
    user = relationship("User", back_populates="accounts")

    transactions = relationship("FinancialTransaction", back_populates="account",   cascade="all, delete-orphan", passive_deletes=True)


    @property
    def available_credit(self) -> Decimal:
        """Calcula o limite disponível dinamicamente"""
        if self.is_credit:
            return self.credit_limit - self.used_credit
        return Decimal('0.00')
    
    def __repr__(self):
        return f"<Account {self.name} ({'Crédito' if self.is_credit else 'Débito'})>"