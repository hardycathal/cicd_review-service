import os
from fastapi import FastAPI, Depends, HTTPException, status, Response 
from contextlib import asynccontextmanager 
from sqlalchemy.orm import Session 
from sqlalchemy import select 
from sqlalchemy.exc import IntegrityError 
from sqlalchemy.orm import selectinload 
from fastapi.middleware.cors import CORSMiddleware 
from .database import engine, SessionLocal, get_db
from .models import Base, MovieDB
from .schemas import ( 
    MovieCreate, MovieRead
) 
import requests

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
#Replacing @app.on_event("startup") 
@asynccontextmanager 
async def lifespan(app: FastAPI): 
    Base.metadata.create_all(bind=engine)    
    yield 

app = FastAPI(lifespan=lifespan)

 
def commit_or_rollback(db: Session, error_msg: str): 
    try: 
        db.commit() 
    except IntegrityError: 
        db.rollback() 
        raise HTTPException(status_code=409, detail=error_msg) 
 

## Health Check ##
@app.get("/health") 
def health(): 
    return {"status": "ok"}

@app.get("/api/movies/popular")
def get_popular():
    if not TMDB_API_KEY:
        raise HTTPException(status_code=500, detail="TMDB_API_KEY not configured")
    
    url = "https://api.themoviedb.org/3/movie/popular"
    params = {"api_key": TMDB_API_KEY}

    response = requests.get(url, params=params)
    return response.json()
