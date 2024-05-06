import json
import logging
import time
import uuid
from datetime import datetime
import hashlib

from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, func, JSON
import sqlalchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к базе данных
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


class AccountService:
    def __init__(self):
        self.session = Session()

    def get_processed_positions(self):
        try:
            with open("global_position.json", "r") as file:
                data = json.load(file)
                return data.get('processed_positions', [])
        except FileNotFoundError:
            return []

    def add_processed_position(self, position):
        processed_positions = self.get_processed_positions()
        processed_positions.append(position)
        with open("global_position.json", "w") as file:
            json.dump({"processed_positions": processed_positions}, file)

    def process_money_deposit_command(self, command):
        if command.global_position in self.get_processed_positions():
            logger.info("Skipping processed command.")
            return

        amount = command.data.get('amount')
        account_id = command.data.get('account_id')

        try:
            if not all([amount, account_id]):
                logger.error("Invalid command data. Money deposit command cannot be processed.")
                error_data = {'error_message': 'Invalid command data.'}
                self.create_event('MoneyDepositedError', error_data, command.metadata_json)
                self.session.commit()
                return

            account = self.session.query(Account).filter_by(account_id=account_id).first()

            if not account:
                logger.error("Account not found. Money deposit command cannot be processed.")
                error_data = {'error_message': 'Account not found.'}
                self.create_event('MoneyDepositedError', error_data, command.metadata_json)
                self.session.commit()
                return

            if account.status != 'block':
                logger.info("Processing money deposit command...")
                account.balance += amount
                self.create_event('MoneyDeposited', {'amount': amount, 'account_id': account_id}, command.metadata_json)
                logger.info("Money deposit command processed successfully.")
            else:
                logger.error("Account is blocked. Money deposit command cannot be processed.")
                error_data = {'error_message': 'Account is blocked.'}
                self.create_event('MoneyDepositedError', error_data, command.metadata_json)

            self.session.commit()
        except Exception as e:
            self.session.rollback()
            time.sleep(1)
            logger.exception("An error occurred while processing money deposit command: %s", e)

    def process_money_transfer_command(self, command):
        if command.global_position in self.get_processed_positions():
            logger.info("Skipping processed command.")
            return

        amount = command.data.get('amount')
        sender_id = command.data.get('sender_id')
        receiver_id = command.data.get('receiver_id')

        try:
            if not all([amount, sender_id, receiver_id]):
                logger.error("Invalid command data. Money transfer command cannot be processed.")
                error_data = {'error_message': 'Invalid command data.'}
                self.create_event('MoneyTransferedError', error_data, command.metadata_json)
                self.session.commit()
                return

            sender_account = self.session.query(Account).filter_by(account_id=sender_id).first()
            receiver_account = self.session.query(Account).filter_by(account_id=receiver_id).first()

            if not all([sender_account, receiver_account]):
                logger.error("Sender or receiver account not found. Money transfer command cannot be processed.")
                error_data = {'error_message': 'Sender or receiver account not found.'}
                self.create_event('MoneyTransferedError', error_data, command.metadata_json)
                self.session.commit()
                return

            if sender_account.status != 'block' and receiver_account.status != 'block' and sender_account.balance >= amount:
                logger.info("Processing money transfer command...")
                event_data = {
                    'amount': amount,
                    'sender_id': sender_id,
                    'receiver_id': receiver_id
                }
                self.create_event('MoneyTransfered', event_data, command.metadata_json)
                logger.info("Money transfer command processed successfully.")
            else:
                logger.error("Insufficient balance or invalid sender ID. Money transfer command cannot be processed.")
                error_data = {
                    'error_message': 'Insufficient balance or invalid sender ID'
                }
                self.create_event('MoneyTransferedError', error_data, command.metadata_json)

            self.session.commit()  # Сохраняем изменения в команде
        except Exception as e:
            self.session.rollback()
            time.sleep(1)
            logger.exception("An error occurred while processing money transfer command: %s", e)

    def process_account_create_command(self, command):
        if command.global_position in self.get_processed_positions():
            logger.info("Skipping processed command.")
            return

        account_name = command.data.get('account_name')
        account_email = command.data.get('account_email')
        password_hash = command.data.get('password_hash')

        try:
            if not all([account_name, account_email, password_hash]):
                logger.error("Invalid command data. Account creation command cannot be processed.")
                error_data = {'error_message': 'Invalid command data.'}
                self.create_event('AccountCreatedError', error_data, command.metadata_json)
                self.session.commit()
                return

            existing_account = self.session.query(Account).filter_by(account_email=account_email).first()

            if existing_account:
                logger.error("Account with the same email already exists. Account creation command cannot be processed.")
                error_data = {'error_message': 'Account with the same email already exists.'}
                self.create_event('AccountCreatedError', error_data, command.metadata_json)
                self.session.commit()
                return

            event_data = {
                'account_name': account_name,
                'account_email': account_email,
                'password_hash': password_hash
            }
            self.create_event('AccountCreated', event_data, command.metadata_json)
            logger.info("Account creation command processed successfully.")

            self.session.commit()
        except Exception as e:
            self.session.rollback()
            time.sleep(1)
            logger.exception("An error occurred while processing account creation command: %s", e)


    def create_event(self, event_type, event_data, metadata):
        max_position = self.session.query(func.max(Message.position)).scalar()
        next_position = max_position + 1 if max_position is not None else 1

        event = Message(
            position=next_position,
            stream_name='event',
            type=event_type,
            data=json.dumps(event_data),
            metadata_json=json.dumps(metadata),
        )
        self.session.add(event)

    def main(self):
        self.session.begin()
        processed_positions = self.get_processed_positions()
        all_commands = self.session.query(Message).filter_by(stream_name='command').order_by(Message.global_position.asc()).all()

        for command in all_commands:
            if command.global_position not in processed_positions:
                if command.type == 'MoneyTransfer':
                    self.process_money_transfer_command(command)
                elif command.type == 'MoneyDeposit':
                    self.process_money_deposit_command(command)
                elif command.type == 'AccountCreate':
                    self.process_account_create_command(command)
                else:
                    logger.info(f"Ignoring command of type {command.type} or it has already been processed.")
                    time.sleep(1)

                self.add_processed_position(command.global_position)

        self.session.commit()


if __name__ == "__main__":
    account_service = AccountService()
    account_service.main()
