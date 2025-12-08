from pydantic import BaseModel
from typing import List

class CouncilPayload(BaseModel):
    orcid: str = "application-profile"
    amount: int = 5
    key: int = 0
    specialty_id: str = "01.01.01"
    keywords: List[str] = []