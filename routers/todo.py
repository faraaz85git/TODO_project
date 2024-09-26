from typing import Annotated,Optional
from fastapi import APIRouter,Depends,HTTPException,Path,Query
from starlette import status
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from database import session_local
from models import Todos
from .auth import get_curr_user
router=APIRouter()

#it is creating connection then return data the close
def get_db():
    db=session_local()
    try:
        yield db
    finally:
        db.close()

# it is creating a depency
db_dependency = Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_curr_user)]

class Todo_request(BaseModel):
    id:Optional[int]=Field(description='not required for creating todo',default=None)
    title:str=Field(max_length=50)
    description:str=Field(max_length=50)
    priority:int=Field(gt=0,lt=6)
    complete:bool=Field(default=False)



#Depends is saying read_all is depend on get db function`
@router.get('/',status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,
                   db:db_dependency):
    user_id=user.get('id')
    return db.query(Todos).filter(Todos.owner_id==user_id).all()

@router.get('/todos/{todo_id}',status_code=status.HTTP_200_OK)
async def get_todo_by_id(user:user_dependency,
                         db:db_dependency,
                         todo_id:int=Path(gt=-1)):
    user_id=user.get('id')
    todo_model=db.query(Todos).filter(Todos.id==todo_id and Todos.owner_id==user_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404,detail="NOT FOUND")

@router.post('/todo',status_code=status.HTTP_201_CREATED)
async def create_todos(user:user_dependency,
                       db:db_dependency,
                       todo_req:Todo_request):
    # return {'status': 'run'}
    if user is None:
        raise HTTPException(status_code=401,detail='not authorised')
    new_todo=Todos(**(todo_req.model_dump()),owner_id=user.get('id'))
    db.add(new_todo)
    db.commit()

@router.put('/update/{todo_id}',status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db:db_dependency,
                      update_todo:Todo_request,
                      todo_id:int=Path(gt=0)):
    todo_model=db.query(Todos).filter(Todos.id==todo_id).first()

    #change is occuring on same instance which is in database.
    #todomodel is getting update not created new todo
    if todo_model:
        todo_model.title=update_todo.title
        todo_model.description=update_todo.description
        todo_model.priority=update_todo.priority
        todo_model.complete=update_todo.complete

        db.add(todo_model)
        db.commit()

    else:
        raise HTTPException(status_code=404,detail="not found")

@router.delete('/delete/{todo_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db:db_dependency,todo_id:int=Path(gt=0)):
    todo_model=db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model:
        db.query(Todos).filter(Todos.id==todo_id).delete()
        db.commit()
    else:
        raise HTTPException(status_code=404,detail="not found")