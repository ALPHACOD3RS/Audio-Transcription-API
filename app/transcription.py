# app/transcription.py

import whisperx
import ffmpeg
import os
from typing import Dict, Any
from .config import settings
from transformers import pipeline
import torch

# Initialize WhisperX model
print("Loading WhisperX model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisperx.load_model("large", device=device)  # Choose model size as needed

# Initialize summarization pipeline
print("Loading summarization model...")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=0 if device=="cuda" else -1)

def convert_audio(input_path: str, output_path: str) -> None:
    """Convert audio to WAV format with specific parameters."""
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, format='wav', acodec='pcm_s16le', ac=1, ar='16k')
            .overwrite_output()
            .run(quiet=True)
        )
    except ffmpeg.Error as e:
        raise Exception(f"Error converting audio: {e}")

def transcribe_audio(file_path: str, language: str = "he") -> Dict[str, Any]:
    """Transcribe audio with timestamps and speaker diarization using WhisperX."""
    try:
        # Transcription
        result = model.transcribe(file_path, language=language, word_timestamps=True)
        
        # Load the alignment model and metadata
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        result_aligned = whisperx.align(result["segments"], model_a, metadata, file_path, device)
        
        # Speaker Diarization
        transcript = []
        for segment in result_aligned['segments']:
            transcript.append({
                "speaker": f"speaker_{segment['speaker']}",
                "timestamp": segment['start'],
                "text": segment['text']
            })
        
        # Metadata extraction (populate as needed)
        metadata_info = {
            # Populate with actual metadata if available
        }
        
        return {
            "metadata": metadata_info,
            "transcript": transcript
        }
    except Exception as e:
        raise Exception(f"Transcription failed: {e}")

def summarize_transcript(transcript: str) -> str:
    """Summarize transcript using transformers-based model."""
    try:
        # The summarizer may have a token limit; split if necessary
        max_chunk = 1000  # Adjust based on model's max tokens
        summary = ""
        for i in range(0, len(transcript), max_chunk):
            chunk = transcript[i:i+max_chunk]
            summary_chunk = summarizer(chunk, max_length=150, min_length=40, do_sample=False)[0]['summary_text']
            summary += summary_chunk + " "
        return summary.strip()
    except Exception as e:
        raise Exception(f"Summarization failed: {e}")
