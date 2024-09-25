
from fastapi import FastAPI

import models
from database import engine
from routers import auth,todo


app=FastAPI()

#it is creating a database and model we defined.
models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)#now endpoint define in auth is available in main
app.include_router(todo.router)
