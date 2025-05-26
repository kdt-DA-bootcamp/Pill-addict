#사용자 정보 입력 코드

from pydantic import BaseModel
from typing import List, Optional

class UserHealthInfo(BaseModel):
    is_pregnant: Optional[bool] = False
    is_baby: Optional[bool] = False
    smokes: Optional[bool] = False
    drinks: Optional[bool] = False
    allergies: Optional[List[str]] = []
    wants_detailed: Optional[bool] = False
