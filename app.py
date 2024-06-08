from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, func, UUID
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import uuid
from fastapi.staticfiles import StaticFiles

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/postgres"

engine = create_engine(DATABASE_URL, client_encoding='utf-8')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()  # Исправление согласно предупреждению

class Message(Base):
    __tablename__ = 'messages'
    __table_args__ = {'schema': 'message_store'}

    global_position = Column(Integer, primary_key=True, autoincrement=True)
    position = Column(Integer, nullable=False)
    time = Column(DateTime, nullable=False, default=datetime.utcnow)
    stream_name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    data = Column(JSON)
    metadata_json = Column(JSON, name='metadata')
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Настройка CORS
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем директорию static для статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register_teacher(request: RegisterRequest, db: Session = Depends(get_db)):
    max_position = db.query(func.max(Message.position)).scalar()
    next_position = max_position + 1 if max_position is not None else 1
    uuid_teacher = uuid.uuid4()

    message = Message(
        position=next_position,
        time=datetime.utcnow(),
        stream_name="teacher-" + str(uuid_teacher),
        type="RegisterTeacher",
        data={"first_name": request.first_name, "last_name": request.last_name},
        metadata={"user_id": "manager1"},
        id=uuid_teacher
    )

    db.add(message)
    db.commit()
    db.refresh(message)
    
    return {"message": "Teacher registered successfully", "teacher_id": str(message.id)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
