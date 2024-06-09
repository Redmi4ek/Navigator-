from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from main import Base, Message, Teacher, DATABASE_URL
import time
from datetime import datetime
import uuid
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)  # Создание таблиц, если их нет

def get_last_processed_position(session: Session):
    # Получаем последнюю обработанную позицию из данных в messages
    last_message = session.query(Message).filter(Message.type.in_(["TeacherRegistered", "TeacherRegisterError"])).order_by(Message.global_position.desc()).first()
    if last_message and "lastProcessed" in last_message.data:
        return last_message.data["lastProcessed"]
    return 0

def process_messages():
    while True:
        session = SessionLocal()
        try:
            last_processed_position = get_last_processed_position(session)
            new_messages = session.query(Message).filter(
                Message.type == "RegisterTeacher",
                Message.global_position > last_processed_position
            ).all()

            for message in new_messages:
                data = message.data
                existing_teacher = session.query(Teacher).filter_by(
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    telegram_id=data['telegram_id']
                ).first()

                if existing_teacher is None:
                    # Учитель не существует, регистрируем
                    logger.info(f"Registering new teacher: {data['first_name']} {data['last_name']}")
                    new_message = Message(
                        position=message.position + 1,
                        time=datetime.utcnow(),
                        stream_name=message.stream_name,
                        type="TeacherRegistered",
                        data={**message.data, "lastProcessed": message.global_position},
                        metadata_json=message.metadata_json,
                        id=uuid.uuid4()
                    )
                else:
                    # Учитель существует, ошибка регистрации
                    logger.info(f"Teacher {data['first_name']} {data['last_name']} already exists, registration failed")
                    new_message = Message(
                        position=message.position + 1,
                        time=datetime.utcnow(),
                        stream_name=message.stream_name,
                        type="TeacherRegisterError",
                        data={"error": "Teacher already exists", "lastProcessed": message.global_position},
                        metadata_json=message.metadata_json,
                        id=uuid.uuid4()
                    )

                # Проверяем, было ли уже обработано сообщение
                existing_message = session.query(Message).filter_by(
                    type=new_message.type,
                    data=new_message.data,
                    global_position=message.global_position
                ).first()

                if not existing_message:
                    # Добавляем только новые сообщения
                    session.add(new_message)
                    session.commit()
        finally:
            session.close()
        
        # Задержка перед следующей проверкой сообщений
        time.sleep(1)

if __name__ == "__main__":
    process_messages()
