import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, SessionLocal, get_db, Base
from model import Account, Transaction, SupportTicket
# Load environment variables from backend/.env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=GEMINI_API_KEY)

# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="Next-Gen AI ATM API",
    description="Backend APIs for our intelligent ATM ecosystem",
    version="1.0.0"
)


# Allow our React frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create a demo account if it doesn't already exist
def create_demo_account():
    db = SessionLocal()

    try:
        account = db.query(Account).filter(
            Account.account_number == "100001"
        ).first()

        if not account:
            demo_account = Account(
                account_number="100001",
                customer_name="Demo Customer",
                balance=25000.0
            )

            db.add(demo_account)
            db.commit()

    finally:
        db.close()


create_demo_account()


# API 1: Welcome endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to Next-Gen AI ATM Ecosystem",
        "status": "Backend running"
    }


# API 2: Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Next-Gen AI ATM"
    }


# API 3: Get account details and balance
@app.get("/api/account/{account_number}")
def get_account(
    account_number: str,
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    return {
        "account_number": account.account_number,
        "customer_name": account.customer_name,
        "balance": account.balance,
        "currency": "INR"
    }


# API 4: Get transaction history
@app.get("/api/account/{account_number}/transactions")
def get_transactions(
    account_number: str,
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    transactions = db.query(Transaction).filter(
        Transaction.account_number == account_number
    ).order_by(Transaction.timestamp.desc()).all()

    return [
        {
            "id": transaction.id,
            "type": transaction.transaction_type,
            "amount": transaction.amount,
            "status": transaction.status,
            "timestamp": transaction.timestamp
        }
        for transaction in transactions
    ]


# Withdrawal request structure
class WithdrawalRequest(BaseModel):
    account_number: str
    amount: float = Field(gt=0)


# API 5: Withdraw cash
@app.post("/api/withdraw")
def withdraw_cash(
    request: WithdrawalRequest,
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(
        Account.account_number == request.account_number
    ).first()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    if request.amount % 100 != 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be in multiples of 100"
        )

    if request.amount > account.balance:
        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    account.balance -= request.amount

    transaction = Transaction(
        account_number=request.account_number,
        transaction_type="Withdrawal",
        amount=request.amount,
        status="Success"
    )

    db.add(transaction)
    db.commit()
    db.refresh(account)

    return {
        "message": "Withdrawal successful",
        "withdrawn_amount": request.amount,
        "remaining_balance": account.balance
    }


# Support ticket request structure
class SupportTicketRequest(BaseModel):
    account_number: str
    issue: str
    description: str


# API 6: Create customer support ticket
@app.post("/api/support/ticket")
def create_support_ticket(
    request: SupportTicketRequest,
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(
        Account.account_number == request.account_number
    ).first()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    ticket = SupportTicket(
        account_number=request.account_number,
        issue=request.issue,
        description=request.description,
        status="Open"
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return {
        "message": "Support ticket created successfully",
        "ticket_id": ticket.id,
        "issue": ticket.issue,
        "status": ticket.status,
        "created_at": ticket.created_at
    }


# API 7: Get customer support tickets
@app.get("/api/support/tickets/{account_number}")
def get_support_tickets(
    account_number: str,
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    tickets = db.query(SupportTicket).filter(
        SupportTicket.account_number == account_number
    ).order_by(SupportTicket.created_at.desc()).all()

    return [
        {
            "id": ticket.id,
            "issue": ticket.issue,
            "description": ticket.description,
            "status": ticket.status,
            "created_at": ticket.created_at
        }
        for ticket in tickets
    ]

# ==========================================
# NEXT-GEN AI ATM - GEMINI CUSTOMER SUPPORT AGENT
# ==========================================

DEMO_ACCOUNT_NUMBER = "100001"


# Chat request structure
class AgentChatRequest(BaseModel):
    message: str


# ------------------------------------------
# TOOL 1: GET ACCOUNT BALANCE
# ------------------------------------------

def get_account_balance():
    """Retrieve the current balance of the demo ATM customer."""

    db = SessionLocal()

    try:
        account = db.query(Account).filter(
            Account.account_number == DEMO_ACCOUNT_NUMBER
        ).first()

        if not account:
            return {"error": "Account not found"}

        return {
            "account_number": account.account_number,
            "customer_name": account.customer_name,
            "balance": account.balance,
            "currency": "INR"
        }

    finally:
        db.close()


# ------------------------------------------
# TOOL 2: GET RECENT TRANSACTIONS
# ------------------------------------------

def get_recent_transactions():
    """Retrieve the five most recent transactions of the demo ATM customer."""

    db = SessionLocal()

    try:
        transactions = db.query(Transaction).filter(
            Transaction.account_number == DEMO_ACCOUNT_NUMBER
        ).order_by(
            Transaction.timestamp.desc()
        ).limit(5).all()

        return [
            {
                "id": transaction.id,
                "type": transaction.transaction_type,
                "amount": transaction.amount,
                "status": transaction.status,
                "timestamp": (
                    transaction.timestamp.isoformat()
                    if transaction.timestamp else None
                )
            }
            for transaction in transactions
        ]

    finally:
        db.close()


# ------------------------------------------
# TOOL 3: CREATE SUPPORT TICKET
# ------------------------------------------

def create_support_ticket(issue: str, description: str):
    """Create a support ticket when the customer explicitly requests one.

    Args:
        issue: Short title of the customer's issue.
        description: Detailed description of the complaint.
    """

    db = SessionLocal()

    try:
        account = db.query(Account).filter(
            Account.account_number == DEMO_ACCOUNT_NUMBER
        ).first()

        if not account:
            return {"error": "Account not found"}

        ticket = SupportTicket(
            account_number=DEMO_ACCOUNT_NUMBER,
            issue=issue,
            description=description,
            status="Open"
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return {
            "message": "Support ticket created successfully",
            "ticket_id": ticket.id,
            "issue": ticket.issue,
            "status": ticket.status
        }

    finally:
        db.close()


# ------------------------------------------
# GEMINI AI AGENT INSTRUCTIONS
# ------------------------------------------

ATM_AGENT_INSTRUCTIONS = """
You are the intelligent AI Customer Support Agent
of the Next-Gen AI ATM Ecosystem.

Your responsibilities:

1. Help customers understand ATM services.
2. Answer account balance questions using the balance tool.
3. Answer transaction questions using the transaction tool.
4. Explain ATM errors and troubleshooting steps.
5. Help customers report failed withdrawals and other issues.
6. Create support tickets when explicitly requested.

IMPORTANT RULES:

- Never invent account balances or transactions.
- Always use the appropriate tool for account information.
- Never claim a ticket was created unless the tool confirms it.
- Only create a ticket when the customer explicitly asks you
  to create or submit one.
- If a customer only describes a problem, ask whether they
  want you to create a support ticket.
- Never withdraw money or modify account balances.
- Never request PINs, passwords, OTPs or card security codes.
- Never reveal information about another customer.
- This is a demonstration ATM application, not a real bank.

Respond in a friendly, clear and professional manner.
Use INR when discussing account balances and transactions.
"""


# ------------------------------------------
# GEMINI CHAT API
# ------------------------------------------

@app.post("/api/agent/chat")
def chat_with_atm_agent(request: AgentChatRequest):

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a message."
        )

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=request.message,
            config=types.GenerateContentConfig(
                system_instruction=ATM_AGENT_INSTRUCTIONS,
                tools=[
                    get_account_balance,
                    get_recent_transactions,
                    create_support_ticket
                ],
                automatic_function_calling=(
                    types.AutomaticFunctionCallingConfig(
                        maximum_remote_calls=5
                    )
                )
            )
        )

        if not response.text:
            raise HTTPException(
                status_code=502,
                detail="The AI agent returned an empty response."
            )

        return {
            "reply": response.text,
            "agent": "Next-Gen AI ATM Gemini Assistant"
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Gemini Agent Error:", repr(error))

        raise HTTPException(
            status_code=502,
            detail="The AI support service is temporarily unavailable."
        )

