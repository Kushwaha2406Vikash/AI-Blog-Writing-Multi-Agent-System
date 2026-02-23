from pydantic import BaseModel,Field
from typing import Optional,List




class EvidenceItem(BaseModel):
    title: str
    url: str
    published_at: Optional[str] = None  # prefer ISO "YYYY-MM-DD"
    snippet: Optional[str] = None
    source: Optional[str] = None  

class EvidencePack(BaseModel):
    evidence: List[EvidenceItem] = Field(default_factory=list)