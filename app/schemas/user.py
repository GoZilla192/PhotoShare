from pydantic import BaseModel

from app.models import UserRole

class UserCreateSchema(BaseModel):
	username: str
	email: str
	password_hash: str
	
class UserReadSchema(BaseModel):
	id: int
	username: str
	email: str
	role: UserRole
	is_active: bool
	