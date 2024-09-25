from fastapi import Depends,FastAPI,APIRouter
from pydantic import BaseModel,Field
from models import Users
from starlette import status
from passlib.context import CryptContext
from database import session_local
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
router=APIRouter()
bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
def get_db():
    db=session_local()
    try:
        yield db
    finally:
        db.close()

# it is creating a depency
db_dependency = Annotated[Session,Depends(get_db)]

class Create_User_Request(BaseModel):
    username:str
    email:str
    first_name:str
    last_name:str
    password:str
    role:str



@router.post('/auth',status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency,
                      create_user_request:Create_User_Request):
       create_user_model=Users(
           email=create_user_request.email,
           user_name=create_user_request.username,
           first_name=create_user_request.first_name,
           last_name=create_user_request.last_name,
           hashed_password=bcrypt_context.hash(create_user_request.password),
           role=create_user_request.role,
           is_active=True
       )
       db.add(create_user_model)
       db.commit()


@router.post('/token')
async def login_for_token(db:db_dependency,
                          form_data:Annotated[OAuth2PasswordRequestForm,Depends()]
                          ):
    return 'token'

