from typing import Annotated
from fastapi import FastAPI,Depends,HTTPException,Path,Query
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

#Depends is saying read_all is depend on get db function`
@app.get('/')
async def read_all(db:db_dependency):
    return db.query(Todos).all()

@app.get('/todos/{todo_id}')
async def get_todo_by_id(db:db_dependency,todo_id:int=Path(gt=-1)):
    todo_model=db.query(Todos).filter(Todos.id==todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404,detail="NOT FOUND")