from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware

# Определите модель SQLAlchemy
Base = declarative_base()

class Teacher(Base):
    __table_args__ = {'schema': 'message_store'}
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    telegram_id = Column(String)
    school = Column(String)
    phone_number = Column(Integer)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
# Создайте движок SQLAlchemy
engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

# Создайте сессию SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()

# Создайте FastAPI приложение
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
    expose_headers=["*"],
)


templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/regist", response_class=HTMLResponse)
async def regist(request: Request):
    return templates.TemplateResponse("regist.html", {"request": request})

@app.get("/teachers", response_class=HTMLResponse)
async def teacher(request: Request):
    return templates.TemplateResponse("teachers.html", {"request": request})

@app.get("/teachersbd")
def read_teachers():
    # Получите все записи из таблицы teachers
    teachers = session.query(Teacher).all()

    # Отправьте данные на фронт
    return {"teachers": [t.to_dict() for t in teachers]}

