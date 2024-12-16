# app/utils.py

import os
from datetime import datetime
from typing import Dict, Any
from .config import settings
import shutil
import uuid

def generate_file_path(metadata: Dict[str, Any], extension: str) -> str:
    tenant_id = metadata.get("tenant_id")
    call_start_timestamp = metadata.get("call_start_timestamp")
    date_called = call_start_timestamp.date()
    year = date_called.year
    month = f"{date_called.month:02}"
    day = f"{date_called.day:02}"
    extension_or_agent = metadata.get("representative_id")
    call_type = metadata.get("call_type", "inbound")  # default to inbound

    directory = os.path.join(
        settings.RECORDS_PATH,
        f"tenant_{tenant_id}",
        str(year),
        month,
        day,
        str(extension_or_agent),
        call_type
    )
    os.makedirs(directory, exist_ok=True)

    timestamp = call_start_timestamp.strftime("%Y-%m-%dT%H-%M-%S")
    caller = metadata.get("caller_phone_number")
    callee = metadata.get("callee_phone_number")
    call_id = metadata.get("call_id")
    filename = f"{timestamp}_{caller}_{callee}_{extension_or_agent}_{call_id}.{extension}"

    return os.path.join(directory, filename)

def save_file(file, path: str):
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

def extract_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract necessary metadata from the input data."""
    return {
        "tenant_id": data.get("tenant_id"),
        "call_start_timestamp": data.get("call_start_timestamp"),
        "insent_timestamp": data.get("insent_timestamp"),
        "caller_phone_number": data.get("caller_phone_number"),
        "callee_phone_number": data.get("callee_phone_number"),
        "call_id": data.get("call_id"),
        "representative_id": data.get("representative_id"),
        "call_type": data.get("call_type", "inbound")  # default to inbound
    }
