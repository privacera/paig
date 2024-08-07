from pydantic import BaseModel
from typing import List
from pydantic import Field


class DecryptListMessagesByID(BaseModel):
    encryptionKeyId: int = Field(default=0, description="ID of the the key")
    encryptedDataList: List[str] = Field(default=[], description="List of encrypted messages")
