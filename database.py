from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL='sqlite:///./todos.db' #this is location of my db in todo app

#engine is something that help in creating connection and usign database in application
#connect_args={'check_same_thread':False} sqlite by deafault allow only one thread to interact with database but fastpi it
#is common that multiple thread interact with datbase in same time
engine=create_engine(SQLALCHEMY_DATABASE_URL,connect_args={'check_same_thread':False})

session_local=sessionmaker(autocommit=False,autoflush=False,bind=engine)
"""Now we need to create a session local and each instance of the session local will have a database session.

The class itself is not a database session yet.

We will add that later on.

But right now we just need to be able to create an instance of session local that will be able to become

an actual database in the future.

to make sure that our auto commits and auto flushes are false or the database transactions are going

to try and do something automatically.
"""
Base=declarative_base()# it help in creating datbase model obj that that help in creating table or mapping to table.