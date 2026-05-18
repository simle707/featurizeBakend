from pydantic import BaseModel
from typing import Any, Dict


class CreateVMRequest(BaseModel):
    host_machine_id: str
    units: int


class StandardResponse(BaseModel):
    status: int = 0
    data: Any
    message: str = "success"

class LoginRequest(BaseModel):
    sub: str

class PaddleBillingRequest(BaseModel):
    paddle_payload: Dict[str, Any]