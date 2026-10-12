from random import randrange

from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

# TUTORIAL up to 12:40 ******

# create database tables if they do not exist
#models.Base.metadata.create_all(bind=engine) #<- when using alembic, you don't need this line of code

app = FastAPI()

# you can create a strict list of domains/origins that you wish to be able to access your API
# origins = [
#     "http://localhost.tiangolo.com",
#     "https://www.google.com", 
#     "https://www.youtube.com", 
#     "https://localhost.tiangolo.com", 
#     "http://localhost", 
#     "http://localhost:8000"
# ]

# or you can set it to be public to any domain can access the API
origins = ["*"]

# the CORS middleware allows the API to be accessed from other domains, & you can set specific rules about what it will accept, Get &/ Post requests, https headers etc
app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"]
)


# use the router object to include all of those routes in the main app file
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the JB fastAPI Tutorial homepage!"}

# to run app type into terminal: uvicorn app.main:app --reload
# <folder>.<filename>:<FastAPI object name> --reload (the reload property tells the app to reload each time code is changed, without needing to stop & re-start the local server)




