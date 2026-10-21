from random import randrange

from contextlib import asynccontextmanager
from fastapi import FastAPI
from . import models
from .database import engine, SessionLocal
from .routers import post, user, auth, vote
from .config import settings
from .utils import hash_password
from fastapi.middleware.cors import CORSMiddleware


# create database tables if they do not exist
# models.Base.metadata.create_all(bind=engine) #<- when using alembic, you don't need this line of code

# default application permissions
DEFAULT_PERMISSIONS = ["admin", "read", "user_profiles", "planner", "metric"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        changes_made = False

        # seed permissions
        for perm_name in DEFAULT_PERMISSIONS:
            existing_perm = db.query(models.Permission).filter(models.Permission.name == perm_name).first()
            if not existing_perm:
                new_perm = models.Permission(name=perm_name)
                db.add(new_perm)
                changes_made = True

        if changes_made:
            db.commit()

        # seed admin user
        admin_email = "admin@gmail.com"
        admin_pwd = "pwd999"
        existing_admin = db.query(models.User).filter(models.User.email == admin_email).first()

        if not existing_admin:
            admin_perm = db.query(models.Permission).filter(models.Permission.name == "admin").first()

            hash_pwd = hash_password(admin_pwd)

            admin_user = models.User(
                email = admin_email, 
                username = "admin", 
                password = hash_pwd, 
                display_name = "admin", 
                short_name = "admin"
            )

            admin_user.permissions.append(admin_perm)

            db.add(admin_user)
            db.commit()

    except Exception as e:
        print(f"Error during startup seeding of permission & admin user: {e}")
        db.rollback()
    finally:
        db.close()

    yield


app = FastAPI(lifespan=lifespan)

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
    return {"message": "Welcome to the JB fastAPI homepage"}

# to run app type into terminal: uvicorn app.main:app --reload
# <folder>.<filename>:<FastAPI object name> --reload (the reload property tells the app to reload each time code is changed, without needing to stop & re-start the local server)




