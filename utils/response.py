from typing import Optional,Any
from pydantic import BaseModel

class ResponseModel(BaseModel):
    code: int
    msg: str
    data: Optional[Any] = None
    

def success_response(data: dict = None, code: int = 200, msg: str = "success"):
    return ResponseModel(code=code, msg=msg, data=data)

def error_response(code: int = 400, msg: str = "error", details: dict = None):
    return ResponseModel(code=code, msg=msg, data={"details": details})
