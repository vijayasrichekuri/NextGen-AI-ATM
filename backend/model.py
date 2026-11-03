from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from database import Base


# ATM customer account table
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, index=True)
    customer_name = Column(String)
    balance = Column(Float, default=25000.0)


# ATM transaction history table
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, index=True)
    transaction_type = Column(String)
    amount = Column(Float)
    status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


# Customer support ticket table
class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, index=True)
    issue = Column(String)
    description = Column(String)
    status = Column(String, default="Open")
    created_at = Column(DateTime, default=datetime.utcnow)