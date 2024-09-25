from typing import Annotated,Optional
from fastapi import FastAPI,Depends,HTTPException,Path,Query
from starlette import status
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
import models
from database import engine,session_local
from models import Todos

app=FastAPI()
#it is creating a database and model we defined.
models.Base.metadata.create_all(bind=engine)

#it is creating connection then return data the close
def get_db():
    db=session_local()
    try:
        yield db
    finally:
        db.close()

# it is creating a depency
db_dependency = Annotated[Session,Depends(get_db)]


class Todo_request(BaseModel):
    id:Optional[int]=Field(description='not required for creating todo',default=None)
    title:str=Field(max_length=50)
    description:str=Field(max_length=50)
    priority:int=Field(gt=0,lt=6)
    complete:bool=Field(default=False)



#Depends is saying read_all is depend on get db function`
@app.get('/',status_code=status.HTTP_200_OK)
async def read_all(db:db_dependency):
    return db.query(Todos).all()

@app.get('/todos/{todo_id}',status_code=status.HTTP_200_OK)
async def get_todo_by_id(db:db_dependency,todo_id:int=Path(gt=-1)):
    todo_model=db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404,detail="NOT FOUND")

@app.post('/todo',status_code=status.HTTP_201_CREATED)
async def create_todos(db:db_dependency,todo_req:Todo_request):
    new_todo=Todos(**(todo_req.model_dump()))
    db.add(new_todo)
    db.commit()

@app.put('/update/{todo_id}',status_code=status.HTTP_204_NO_CONTENT)
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

