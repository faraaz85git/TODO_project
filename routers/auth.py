from fastapi import Depends,FastAPI,APIRouter,HTTPException
from pydantic import BaseModel,Field
from models import Users
from starlette import status
from passlib.context import CryptContext
from database import session_local
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt,JWTError
from datetime import datetime,timedelta,timezone

router=APIRouter(
    prefix='/auth',
    tags=['auth']
)
SECRET_KEY='197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM='HS256'
bcrypt_context=CryptContext(schemes=['bcrypt'],deprecated='auto')

oauth2_bearer=OAuth2PasswordBearer(tokenUrl='auth/token')

class Create_User_Request(BaseModel):
    username:str
    email:str
    first_name:str
    last_name:str
    password:str
    role:str

class Token(BaseModel):
    access_token:str
    token_type:str
def get_db():
    db=session_local()
    try:
        yield db
    finally:
        db.close()

# it is creating a depency
db_dependency = Annotated[Session,Depends(get_db)]

def authenticate_user(db,username:str,password:str):
    user=db.query(Users).filter(Users.user_name==username).first()
    if user:
        if user.user_name==username and bcrypt_context.verify(password,user.hashed_password):
            return user
    else:
        return False

def get_curr_user(token:Annotated[str,Depends(oauth2_bearer)]):
   try:
        payload=jwt.decode(token,SECRET_KEY,ALGORITHM)
        user_name=payload.get('sub')
        id=payload.get('id')
        if user_name==None or id==None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='gcfgjfgc authorised')
        else:
            return {"user_name":user_name,"id":id}
   except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='not authorised')



def create_access_token(username:str,user_id:int,expires_delta:timedelta):
    encode={'sub':username,'id':user_id}
    expires=datetime.now(timezone.utc)+expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY,ALGORITHM)


@router.post('/',status_code=status.HTTP_201_CREATED)
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


@router.post('/token',response_model=Token)
async def login_for_token(db:db_dependency,
                          form_data:Annotated[OAuth2PasswordRequestForm,Depends()]
                          ):
    user=authenticate_user(db,form_data.username,form_data.password)
    if user:
        token=create_access_token(username=user.user_name , user_id=user.id , expires_delta=timedelta(minutes=20))
        return {'access_token':token,'token_type':'bearer'}

    else:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
