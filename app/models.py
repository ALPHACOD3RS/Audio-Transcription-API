# app/models.py

from sqlalchemy import Column, Integer, String, TIMESTAMP, JSON, ARRAY, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations_test"
    __table_args__ = (
        UniqueConstraint('conversation_id', name='conversations_conversation_test_id_key'),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False)
    conversation_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    insent_timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    call_id = Column(String(255))
    callee_phone_number = Column(String(255))
    caller_phone_number = Column(String(255))
    call_start_timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    call_end_timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    call_duration = Column(Integer)
    customer_id = Column(String(255))
    customer_details = Column(JSON)
    call_project_id = Column(String(255))
    call_project_details = Column(JSON)
    crm_date = Column(JSON)
    representative_id = Column(String(255), nullable=False)
    representative_name = Column(String(255), nullable=False)
    representative_details = Column(JSON)
    conversation_transcript = Column(JSON, nullable=False)
    conversation_summary = Column(String(255))
    tags = Column(ARRAY(String))
    sentiment = Column(JSON)
    resolution_status = Column(String(50))
    audio_file_id = Column(String(255))
    audio_file_details = Column(JSON)
    language = Column(String(50))
    analytics = Column(JSON)

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
