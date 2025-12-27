from fastapi import Header
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserContext(BaseModel):
    id: str
    # Rendiamo email e role opzionali per evitare crash di validazione
    email: Optional[str] = None 
    role: Optional[str] = None

def get_optional_user(
    x_user_cognito_sub: str = Header(None, alias="x-user-cognito-sub"),
    x_user_email: str = Header(None, alias="x-user-email"),
    x_user_role: str = Header(None, alias="x-user-role")
) -> Optional[UserContext]:
    
    print(f"Extracting optional user: id={x_user_cognito_sub}, email={x_user_email}, role={x_user_role}")
    
    if not x_user_cognito_sub:
        return None
        
    return UserContext(
        id=x_user_cognito_sub,
        email=x_user_email,
        role=x_user_role
    )