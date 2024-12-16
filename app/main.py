# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from . import models, schemas, auth, database, transcription, utils, logging_config
from .config import settings
import os
from loguru import logger
from datetime import datetime

# Initialize logging
logging_config.setup_logging()

app = FastAPI(
    title="Audio Transcription API",
    description="API for transcribing audio files with timestamps and speaker diarization.",
    version="1.0.0"
)

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

@app.post("/token", tags=["Authentication"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Authentication failed for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    logger.info(f"User {user.username} authenticated successfully.")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/upload-audio", response_model=List[schemas.AudioUploadResponse], tags=["Audio"])
async def upload_audio(
    files: List[UploadFile] = File(..., description="List of audio files up to 10"),
    tenant_id: int = Form(...),
    insent_timestamp: datetime = Form(...),
    call_start_timestamp: datetime = Form(...),
    call_end_timestamp: datetime = Form(...),
    caller_phone_number: str = Form(...),
    callee_phone_number: str = Form(...),
    representative_id: str = Form(...),
    representative_name: str = Form(...),
    call_type: str = Form("inbound"),
    audio_file_language: str = Form(..., description="Language of the audio, e.g., 'he' for Hebrew"),
    db: Session = Depends(database.get_db),
    current_user: models.APIKey = Depends(auth.get_current_user)
):
    if len(files) > 10:
        logger.error("Bulk upload exceeds 10 files.")
        raise HTTPException(status_code=400, detail="Cannot upload more than 10 files at once.")
    
    responses = []
    for file in files:
        try:
            # Extract metadata
            metadata = {
                "tenant_id": tenant_id,
                "insent_timestamp": insent_timestamp,
                "call_start_timestamp": call_start_timestamp,
                "call_end_timestamp": call_end_timestamp,
                "caller_phone_number": caller_phone_number,
                "callee_phone_number": callee_phone_number,
                "call_id": str(uuid.uuid4()),
                "representative_id": representative_id,
                "call_type": call_type
            }

            # Generate file path
            extension = file.filename.split(".")[-1]
            uniform_extension = "wav"  # Convert all files to WAV
            file_path = utils.generate_file_path(metadata, uniform_extension)

            # Save the original file temporarily
            temp_path = f"/tmp/{uuid.uuid4()}.{extension}"
            with open(temp_path, "wb") as buffer:
                buffer.write(await file.read())
            logger.debug(f"Saved temporary file at {temp_path}")

            # Convert audio to uniform format
            utils.convert_audio(temp_path, file_path)
            logger.info(f"Converted and saved file at {file_path}")

            # Remove temporary file
            os.remove(temp_path)

            # Transcribe audio
            transcript_data = transcription.transcribe_audio(file_path, language=audio_file_language)
            logger.debug(f"Transcribed audio: {transcript_data}")

            # Summarize transcript
            full_transcript = " ".join([segment['text'] for segment in transcript_data['transcript']])
            summary = transcription.summarize_transcript(full_transcript)
            logger.debug(f"Summarized transcript: {summary}")

            # Save to database
            conversation = models.Conversation(
                tenant_id=metadata["tenant_id"],
                conversation_id=uuid.uuid4(),
                insent_timestamp=metadata["insent_timestamp"],
                call_id=metadata["call_id"],
                callee_phone_number=metadata["callee_phone_number"],
                caller_phone_number=metadata["caller_phone_number"],
                call_start_timestamp=metadata["call_start_timestamp"],
                call_end_timestamp=metadata["call_end_timestamp"],
                call_duration=int((metadata["call_end_timestamp"] - metadata["call_start_timestamp"]).total_seconds()),
                customer_id=None,  # Populate as needed
                customer_details=None,  # Populate as needed
                call_project_id=None,  # Populate as needed
                call_project_details=None,  # Populate as needed
                crm_date=None,  # Populate as needed
                representative_id=metadata["representative_id"],
                representative_name=representative_name,
                representative_details=None,  # Populate as needed
                conversation_transcript=transcript_data,
                conversation_summary=summary,
                tags=None,  # Populate as needed
                sentiment=None,  # Populate as needed
                resolution_status=None,  # Populate as needed
                audio_file_id=file_path,
                audio_file_details=None,  # Populate as needed
                language=audio_file_language,
                analytics=None  # Populate as needed
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            logger.info(f"Saved conversation {conversation.conversation_id} to database.")

            responses.append(schemas.AudioUploadResponse(
                success=True,
                details="File processed successfully.",
                conversation_id=str(conversation.conversation_id)
            ))
        except Exception as e:
            logger.error(f"Failed to process file {file.filename}: {e}")
            responses.append(schemas.AudioUploadResponse(
                success=False,
                details=str(e)
            ))
    return responses

# New Endpoint: Retrieve Conversations

@app.get("/conversations", response_model=schemas.ConversationsListResponse, tags=["Conversations"])
def get_conversations(
    tenant_id: Optional[int] = Query(None, description="Filter by Tenant ID"),
    conversation_id: Optional[uuid.UUID] = Query(None, description="Filter by Conversation ID"),
    representative_id: Optional[str] = Query(None, description="Filter by Representative ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(database.get_db),
    current_user: models.APIKey = Depends(auth.get_current_user)
):
    """
    Retrieve conversations from the database with optional filters.
    """
    try:
        query = db.query(models.Conversation)

        if tenant_id is not None:
            query = query.filter(models.Conversation.tenant_id == tenant_id)
        if conversation_id is not None:
            query = query.filter(models.Conversation.conversation_id == conversation_id)
        if representative_id is not None:
            query = query.filter(models.Conversation.representative_id == representative_id)
        if start_date is not None:
            query = query.filter(models.Conversation.call_start_timestamp >= start_date)
        if end_date is not None:
            query = query.filter(models.Conversation.call_end_timestamp <= end_date)

        conversations = query.all()

        response = schemas.ConversationsListResponse(
            conversations=[
                schemas.ConversationMetadata(
                    tenant_id=conv.tenant_id,
                    conversation_id=conv.conversation_id,
                    insent_timestamp=conv.insent_timestamp,
                    call_id=conv.call_id,
                    callee_phone_number=conv.callee_phone_number,
                    caller_phone_number=conv.caller_phone_number,
                    call_start_timestamp=conv.call_start_timestamp,
                    call_end_timestamp=conv.call_end_timestamp,
                    call_duration=conv.call_duration,
                    customer_id=conv.customer_id,
                    customer_details=conv.customer_details,
                    call_project_id=conv.call_project_id,
                    call_project_details=conv.call_project_details,
                    crm_date=conv.crm_date,
                    representative_id=conv.representative_id,
                    representative_name=conv.representative_name,
                    representative_details=conv.representative_details,
                    conversation_transcript=conv.conversation_transcript,
                    conversation_summary=conv.conversation_summary,
                    tags=conv.tags,
                    sentiment=conv.sentiment,
                    resolution_status=conv.resolution_status,
                    audio_file_id=conv.audio_file_id,
                    audio_file_details=conv.audio_file_details,
                    language=conv.language,
                    analytics=conv.analytics
                ) for conv in conversations
            ]
        )
        logger.info(f"Retrieved {len(conversations)} conversations from the database.")
        return response
    except Exception as e:
        logger.error(f"Failed to retrieve conversations: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
