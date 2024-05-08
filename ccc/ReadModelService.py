from decimal import Decimal
import json
import logging
import time
import uuid
from datetime import datetime

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, func, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine("postgresql://postgres:1234@localhost:5432/postgres", client_encoding='utf-8')
Base = sqlalchemy.orm.declarative_base()

class Message(Base):
    __tablename__ = 'messages'
    __table_args__ = {'schema': 'message_store'}

    global_position = Column(Integer, primary_key=True)
    position = Column(Integer, nullable=False)
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
    account_email = Column(String(50), nullable=False)
    password_hash = Column(String(128), nullable=False)
    balance = Column(Numeric(20, 2), nullable=False, default=0)
    status = Column(String(20), nullable=False, default='active')
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())
    updated_at = Column(DateTime, nullable=False, default=func.current_timestamp(), onupdate=func.current_timestamp())

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class ReadModelService:
    def __init__(self):
        self.session = Session()
        self.processed_positions = self.get_processed_positions()

    def get_processed_positions(self):
        try:
            with open("global_position.json", "r") as file:
                data = json.load(file)
                return set(data.get('processed_positions', []))
        except FileNotFoundError:
            return set()

    def add_processed_position(self, position):
        self.processed_positions.add(position)
        with open("global_position.json", "w") as file:
            json.dump({"processed_positions": list(self.processed_positions)}, file)

    def process_event(self, event):
        event_type = event.type
        event_data = event.data

        if event.global_position in self.processed_positions:
            return

        if event_type == 'AccountCreated':
            self.create_account(event_data)
        elif event_type == 'MoneyDeposited':
            self.deposit_money(event_data)
        elif event_type == 'MoneyTransfered':
            self.transfer_money(event_data)
        else:
            logger.info(f"Ignoring event of type {event_type}.")

        self.add_processed_position(event.global_position)


    def create_account(self, event_data):
        try:
            event_data_dict = json.loads(event_data)
            new_account = Account(
                account_name=event_data_dict['account_name'],
                account_email=event_data_dict['account_email'],
                password_hash=event_data_dict['password_hash'],
                balance=0,  # Новый аккаунт создается с нулевым балансом
                status='active'
            )
            self.session.add(new_account)
            self.session.commit()
            logger.info("New account created successfully.")
        except (json.JSONDecodeError, KeyError) as e:
            self.session.rollback()
            logger.error("Error occurred while creating account: %s", str(e))


    def deposit_money(self, event_data):
        try:
            account_id = event_data['account_id']
            amount = event_data['amount']

            account = self.session.query(Account).filter_by(account_id=account_id).first()
            if account:
                account.balance += amount
                self.session.commit()
                logger.info("Money deposited successfully.")
            else:
                logger.error("Account not found while depositing money.")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error("Error occurred while depositing money: %s", str(e))


    def transfer_money(self, event_data):
        try:
            event_data_dict = json.loads(event_data)
            sender_id = event_data_dict['sender_id']
            receiver_id = event_data_dict['receiver_id']
            amount = Decimal(event_data_dict['amount'])

            sender_account = self.session.query(Account).filter_by(account_id=sender_id).first()
            receiver_account = self.session.query(Account).filter_by(account_id=receiver_id).first()

            if sender_account and receiver_account:
                sender_account.balance -= amount
                receiver_account.balance += amount
                self.session.commit()
                logger.info("Money transferred successfully.")
            else:
                logger.error("Sender or receiver account not found while transferring money.")
        except (json.JSONDecodeError, KeyError) as e:
            self.session.rollback()
            logger.error("Error occurred while transferring money: %s", str(e))

    def main(self):
        all_events = self.session.query(Message).filter_by(stream_name='event').all()

        for event in all_events:
            self.process_event(event)

        self.session.close()


if __name__ == "__main__":
    read_model_service = ReadModelService()
    # while True:
    read_model_service.main()
