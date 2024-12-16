# app/schemas.py

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class TranscriptSegment(BaseModel):
    speaker: str
    timestamp: float
    text: str

class Transcript(BaseModel):
    metadata: Dict[str, Any]
    transcript: List[TranscriptSegment]

class ConversationTranscript(BaseModel):
    conversation_transcript: List[Transcript]

class ConversationSummary(BaseModel):
    conversation_summary: Optional[str]

class AudioUploadResponse(BaseModel):
    success: bool
    details: Optional[str]
    conversation_id: Optional[uuid.UUID]

# Schemas for Retrieval

class ConversationMetadata(BaseModel):
    tenant_id: int
    conversation_id: uuid.UUID
    insent_timestamp: datetime
    call_id: Optional[str]
    callee_phone_number: Optional[str]
    caller_phone_number: Optional[str]
    call_start_timestamp: datetime
    call_end_timestamp: datetime
    call_duration: Optional[int]
    customer_id: Optional[str]
    customer_details: Optional[Dict[str, Any]]
    call_project_id: Optional[str]
    call_project_details: Optional[Dict[str, Any]]
    crm_date: Optional[Dict[str, Any]]
    representative_id: str
    representative_name: str
    representative_details: Optional[Dict[str, Any]]
    conversation_transcript: Dict[str, Any]
    conversation_summary: Optional[str]
    tags: Optional[List[str]]
    sentiment: Optional[Dict[str, Any]]
    resolution_status: Optional[str]
    audio_file_id: Optional[str]
    audio_file_details: Optional[Dict[str, Any]]
    language: str
    analytics: Optional[Dict[str, Any]]

class ConversationResponse(BaseModel):
    conversation: ConversationMetadata

class ConversationsListResponse(BaseModel):
    conversations: List[ConversationMetadata]
