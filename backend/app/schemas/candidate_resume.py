from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CandidateResumeResponse(BaseModel):
    id: str
    job_id: Optional[str] = None
    file_name: str
    file_size_bytes: int
    parsed_name: Optional[str] = None
    parsed_email: Optional[str] = None
    parsed_phone: Optional[str] = None
    extracted_skills: Optional[List[str]] = []
    work_history: Optional[List[Any]] = []
    education: Optional[List[Any]] = []
    parse_status: str
    parse_error_message: Optional[str] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
