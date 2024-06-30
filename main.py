from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, func, UUID, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import uuid
from fastapi.responses import HTMLResponse

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"

engine = create_engine(DATABASE_URL, client_encoding='utf-8')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    __table_args__ = {'schema': 'message_store'}
    
    global_position = Column(Integer, primary_key=True, autoincrement=True)
    position = Column(Integer, nullable=False)
    time = Column(DateTime, default=datetime.utcnow)
    stream_name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    data = Column(JSON)
    metadata_json = Column('metadata', JSON)
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)

class Teacher(Base):
    __tablename__ = "teachers"
    __table_args__ = {'schema': 'message_store'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID, unique=True)
    email = Column(VARCHAR, nullable=False)
    registration_password = Column(VARCHAR, nullable=False)
    first_name = Column(VARCHAR, nullable=False)
    last_name = Column(VARCHAR, nullable=False)
    school = Column(VARCHAR, nullable=False)
    phone_number = Column(VARCHAR, nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'schema': 'message_store'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID, unique=True)
    email = Column(VARCHAR, nullable=False)
    password = Column(VARCHAR, nullable=False)
    first_name = Column(VARCHAR, nullable=False)
    last_name = Column(VARCHAR, nullable=False)
    school = Column(VARCHAR, nullable=False)
    phone_number = Column(VARCHAR, nullable=False)
    photo = Column(String)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Achievement(Base):
    __tablename__ = "achivments"
    __table_args__ = {'schema': 'message_store'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    achievement_type = Column(VARCHAR, nullable=False)
    year = Column(Integer, nullable=False)
    title = Column(VARCHAR, nullable=False)
    journal = Column(VARCHAR, nullable=False)
    url = Column(String, nullable=False)


    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class TeacherRequest(BaseModel):
    email: str
    registration_password: str
    first_name: str
    last_name: str
    school: str
    phone_number: str

class UserRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    school: str
    phone_number: str
    photo: str

class AchievementRequest(BaseModel):
    achievement_type: str
    year: int
    title: str
    journal: str
    url: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register_teacher")
def register_teacher(request: TeacherRequest, db: Session = Depends(get_db)):
    max_position = db.query(func.max(Message.position)).scalar()
    next_position = max_position + 1 if max_position is not None else 1
    uuid_teacher = uuid.uuid4()
    
    message = Message(
        position=next_position,
        time=datetime.utcnow(),
        stream_name="teacher-" + str(uuid_teacher),
        type="RegisterTeacher",
        data={"first_name": request.first_name,
              "last_name": request.last_name,
              "email": request.email,
              "school": request.school,
              "phone_number": request.phone_number},
        metadata_json={"user_id": "manager1"},
        id=uuid_teacher
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return {"message": "Teacher registered successfully"}

@app.get("/teachers")
def get_teachers(db: Session = Depends(get_db)):
    teachers = db.query(Teacher).all()
    return {"teachers": [teacher.to_dict() for teacher in teachers]}

@app.post("/register_user")
def register_user(request: UserRequest, db: Session = Depends(get_db)):
    new_user = User(
        email=request.email,
        password=request.password,
        first_name=request.first_name,
        last_name=request.last_name,
        school=request.school,
        phone_number=request.phone_number,
        photo=request.photo
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user": new_user.to_dict()}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"users": [user.to_dict() for user in users]}

@app.post("/add_achievement")
def add_achievement(request: AchievementRequest, db: Session = Depends(get_db)):
    new_achievement = Achievement(
        achievement_type=request.achievement_type,
        year=request.year,
        title=request.title,
        journal=request.journal,
        url=request.url
    )
    db.add(new_achievement)
    db.commit()
    db.refresh(new_achievement)
    return {"message": "Achievement added successfully", "achievement": new_achievement.to_dict()}

@app.get("/achievements")
def get_achievements(db: Session = Depends(get_db)):
    achievements = db.query(Achievement).all()
    return {"achievements": [achievement.to_dict() for achievement in achievements]}

@app.get("/regist", response_class=HTMLResponse)
def regist(request: Request):
    return templates.TemplateResponse("regist.html", {"request": request})

@app.get("/teachers_page", response_class=HTMLResponse)
def teachers_page(request: Request):
    return templates.TemplateResponse("teachers.html", {"request": request})

@app.get("/users_page", response_class=HTMLResponse)
def users_page(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})

@app.get("/achievements_page", response_class=HTMLResponse)
def achievements_page(request: Request):
    return templates.TemplateResponse("achievements.html", {"request": request})