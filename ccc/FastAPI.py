from decimal import Decimal
import json
import logging
import time
import uuid
from datetime import datetime
from passlib.context import CryptContext

from sqlalchemy import func
import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, func, JSON ,cast, Numeric
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS","GET"],  
    allow_headers=["*"],
)

# Подключение к базе данных
engine = create_engine("postgresql://postgres:1234@localhost:5432/postgres", client_encoding='utf-8')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    __table_args__ = {'schema': 'message_store'}

    global_position = Column(Integer, primary_key=True)
    position = Column(Integer, nullable=False, autoincrement=True)
    time = Column(DateTime, nullable=False, default=datetime.utcnow)
    stream_name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    data = Column(JSON)
    metadata_json = Column(JSON, name='metadata')
    id = Column(UUID(as_uuid=True), default=uuid.uuid4)


class Account(Base):
    __tablename__ = 'accounts'

    account_id = Column(Integer, primary_key=True, autoincrement=True)
    account_name = Column(String(50), nullable=False)
    account_email = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    balance = Column(Numeric(20, 2), nullable=False, default=0)
    status = Column(String(20), nullable=False, default='active')
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())
    updated_at = Column(DateTime, nullable=False, default=func.current_timestamp(), onupdate=func.current_timestamp())


Base.metadata.create_all(bind=engine)

class MoneyDepositCommand(BaseModel):
    amount: float
    account_id: int

@app.post("/moneydepositcommand/")
def create_moneydeposit_command(command: MoneyDepositCommand, db: Session = Depends(get_db)):
    try:
        amount_float = float(command.amount)

        existing_command = db.query(Message).filter(
            Message.type == "MoneyDeposit",
            cast(Message.data['amount'], Numeric) == amount_float,
            cast(Message.data['account_id'], Integer) == command.account_id
        ).first()
        
        if existing_command:
            return {"message": "Money Deposit command already exists", "command_id": existing_command.global_position}

        max_position = db.query(func.max(Message.position)).scalar()
        next_position = max_position + 1 if max_position is not None else 1
        db_command = Message(
            position=next_position,
            stream_name="command",
            type="MoneyDeposit",
            data={"amount": amount_float,
                  "account_id": command.account_id}
        )
        db.add(db_command)
        db.commit()
        db.refresh(db_command)
        return db_command
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class MoneyTransferCommand(BaseModel):
    amount: float
    sender_id: int
    receiver_id: int

@app.post("/moneytransfercommand/")
def create_moneytransfer_command(command: MoneyTransferCommand, db: Session = Depends(get_db)):
    try:
        # Check if a command with the same attributes already exists
        existing_command = db.query(Message).filter(
            Message.type == "MoneyTransfer",
            cast(Message.data['amount'], Numeric) == command.amount,
            cast(Message.data['sender_id'], Integer) == command.sender_id,
            cast(Message.data['receiver_id'], Integer) == command.receiver_id
        ).first()
        
        if existing_command:
            # If the command already exists, return the specified message along with the existing command's ID
            return {"message": "Money transfer command already exists", "command_id": existing_command.global_position}

        # If the command does not exist, proceed with saving it to the database
        max_position = db.query(func.max(Message.position)).scalar()
        next_position = max_position + 1 if max_position is not None else 1
        db_command = Message(
            position=next_position,
            stream_name="command",
            type="MoneyTransfer",
            data={"amount": command.amount,
                  "sender_id": command.sender_id,
                  "receiver_id": command.receiver_id}
        )
        db.add(db_command)
        db.commit()
        db.refresh(db_command)
        return db_command
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class AccountCreateCommand(BaseModel):
    account_name: str
    account_email: str
    password_hash: str

@app.post("/accountcreatecommand/")
def create_accountcreate_command(command: AccountCreateCommand, db: Session = Depends(get_db)):
    # Проверяем, существует ли уже команда с такими же данными
    existing_command = db.query(Message).filter_by(stream_name="command", type="AccountCreate", data={
        "account_name": command.account_name,
        "account_email": command.account_email,
        "password_hash": command.password_hash
    }).first()
    
    # Если уже существует команда с такими же данными, возвращаем информацию об этой команде
    if existing_command:
        return {"message": "Account creation command already exists", "command_id": existing_command.global_position}
    
    # В противном случае создаем новую команду
    max_position = db.query(func.max(Message.position)).scalar()
    next_position = max_position + 1 if max_position is not None else 1
    db_command = Message(position=next_position,
                         stream_name="command", 
                         type="AccountCreate", 
                         data=dict(account_name=command.account_name, 
                                   account_email=command.account_email, 
                                   password_hash=command.password_hash))
    db.add(db_command)
    db.commit()
    db.refresh(db_command)
    
    # Получаем только что созданный аккаунт из базы данных
    newly_created_account = db.query(Account).filter_by(account_email=command.account_email).first()
    
    # Проверяем, был ли найден аккаунт
    if newly_created_account:
        user_id = newly_created_account.account_id  # Получаем user_id только что созданного аккаунта
        return {"user_id": user_id, "message": "Account created successfully"}
    else:
        return {"message": "Failed to retrieve user_id after account creation"}

# Определение модели для данных входа
class LoginForm(BaseModel):
    email: str
    password: str

@app.options("/accountcreatecommand/")
async def options_account_create_command():
    return JSONResponse(content="Allow: POST", status_code=200)
    

@app.post("/login/")
async def login(login_data: LoginForm, db: Session = Depends(get_db)):
    # Получение пользователя по email
    user = db.query(Account).filter(Account.account_email == login_data.email).first()
    user0 = db.query(Account).filter(Account.account_name == login_data.email).first()
    # Проверка существования пользователя и соответствия пароля
    if (user and user.password_hash == login_data.password) or (user0 and user0.password_hash == login_data.password):
        # Возвращение редиректа на index.html
        response = RedirectResponse(url='/index.html')
        return response
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
@app.get("/index.html", response_class=HTMLResponse)
async def read_index(request: Request):
    with open("index.html") as f:
        return f.read()