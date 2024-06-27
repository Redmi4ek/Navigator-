from datetime import datetime
import uuid
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from main import Base, Message, Teacher, DATABASE_URL
import time
import logging

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)  # Создание таблиц, если их нет

def get_last_processed_position(session: Session):
    # Получаем последнюю обработанную позицию из данных в messages
    last_message = session.query(Message).filter(Message.type == "TeacherRegistered").order_by(Message.global_position.desc()).first()
    if last_message and "lastProcessed" in last_message.data:
        return last_message.data["lastProcessed"]
    return 0

def update_teachers():
    while True:
        session = SessionLocal()
        try:
            last_processed_position = get_last_processed_position(session)
            new_messages = session.query(Message).filter(
                Message.type == "TeacherRegistered",
                Message.global_position > last_processed_position
            ).all()

            for message in new_messages:
                data = message.data
                metadata = message.metadata_json
                # Проверяем, не существует ли уже учитель с такими данными
                existing_teacher = session.query(Teacher).filter_by(
                    email=data['email']
                ).first()

                if not existing_teacher:
                    # Если учитель не существует, добавляем его
                    logger.info(f"Adding new teacher: {data['first_name']} {data['last_name']}")
                    new_teacher = Teacher(
                        first_name=data['first_name'],
                        last_name=data['last_name'],
                        email=data['email'],
                        school=data['school'],
                        phone_number=data['phone_number'],
                        registration_password=data['registration_password'],
                        uuid=data['teacher_id']
                    )
                    session.add(new_teacher)
                    session.commit()

                # Обновляем значение lastProcessed в сообщении
                message.data["lastProcessed"] = message.global_position
                session.commit()

        finally:
            session.close()
        
        # Задержка перед следующей проверкой сообщений
        time.sleep(1)

if __name__ == "__main__":
    update_teachers()
