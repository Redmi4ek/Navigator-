from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, func, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import uuid
from fastapi.responses import HTMLResponse

# Конфигурация базы данных
DATABASE_URL = "postgresql://postgres:mrkanat2004@localhost:5432/postgres"

# Создание движка базы данных и сессии
engine = create_engine(DATABASE_URL, client_encoding='utf-8')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Определение модели сообщений
class Message(Base):
    __tablename__ = 'messages'
    __table_args__ = {'schema': 'message_store'}
    
    global_position = Column(Integer, primary_key=True, autoincrement=True)
    position = Column(Integer, nullable=False)
    time = Column(DateTime, nullable=False, default=datetime.utcnow)
    stream_name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    data = Column(JSON)
    metadata_json = Column('metadata', JSON)
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)

# Определение модели учителей
class Teacher(Base):
    __tablename__ = "teachers"
    __table_args__ = {'schema': 'message_store'}
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    telegram_id = Column(String)
    school = Column(String)
    phone_number = Column(String)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}



# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

# Инициализация FastAPI приложения
app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение шаблонов и статических файлов
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Модель данных для запроса регистрации
class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    telegram_id: str
    school: str
    phone_number: str

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Обработчик регистрации учителя
@app.post("/register")
def register_teacher(request: RegisterRequest, db: Session = Depends(get_db)):
    # Определение следующей позиции сообщения
    max_position = db.query(func.max(Message.position)).scalar()
    next_position = max_position + 1 if max_position is not None else 1
    uuid_teacher = uuid.uuid4()

    # Создание нового сообщения регистрации учителя
    message = Message(
        position=next_position,
        time=datetime.utcnow(),
        stream_name="teacher-" + str(uuid_teacher),
        type="RegisterTeacher",
        data={"first_name": request.first_name,
              "last_name": request.last_name,
              "telegram_id": request.telegram_id,
              "school": request.school,
              "phone_number": request.phone_number},
        metadata_json={"user_id": "manager1"},
        id=uuid_teacher
    )

    # Добавление сообщения в базу данных
    db.add(message)
    db.commit()
    db.refresh(message)

    return {"message": "Teacher registered successfully"}

# Обработчик получения списка учителей
@app.get("/teachersbd")
def get_teachers(db: Session = Depends(get_db)):
    teachers = db.query(Teacher).all()
    return {"teachers": [teacher.to_dict() for teacher in teachers]}

# Обработчик страницы регистрации
@app.get("/regist", response_class=HTMLResponse)
def regist(request: Request):
    return templates.TemplateResponse("regist.html", {"request": request})

# Обработчик страницы учителей
@app.get("/teachers", response_class=HTMLResponse)
def teachers(request: Request):
    return templates.TemplateResponse("teachers.html", {"request": request})

#Обработчик страницы статей
@app.get("/regist_teacher", response_class=HTMLResponse)
def teachers(request: Request):
    return templates.TemplateResponse("reg_for_teacher.html", {"request": request})

@app.get("/regist_teacher2", response_class=HTMLResponse)
def teachers(request: Request):
    return templates.TemplateResponse("reg_for_teacher2.html", {"request": request})


@app.get("/article_form", response_class=HTMLResponse)
def teachers(request: Request):
    return templates.TemplateResponse("article_form.html", {"request": request})

@app.get("/all_articles", response_class=HTMLResponse)
def teachers(request: Request):
    return templates.TemplateResponse("all_articles.html", {"request": request})

@app.get("/my_articles_table", response_class=HTMLResponse)
def teachers(request: Request):
    return templates.TemplateResponse("my_articles_table.html", {"request": request})