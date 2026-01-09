from fastapi import FastAPI, Depends, HTTPException, status, Response 
from contextlib import asynccontextmanager 
from sqlalchemy.orm import Session 
from sqlalchemy import select 
from sqlalchemy.exc import IntegrityError 
from sqlalchemy.orm import selectinload 
from fastapi.middleware.cors import CORSMiddleware 
from .database import engine, SessionLocal, get_db
import os, httpx
from .models import Base, ReviewDB
from .schemas import ( 
    ReviewCreate, ReviewRead
) 

#Replacing @app.on_event("startup") 
@asynccontextmanager 
async def lifespan(app: FastAPI): 
    Base.metadata.create_all(bind=engine)    
    yield 

app = FastAPI(title="Review Service", lifespan=lifespan)

 
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
 

 ## List Reviews ##
@app.get("/api/reviews", response_model=list[ReviewRead])
def list_reviews(db: Session = Depends(get_db)):
    stmt = select(ReviewDB).order_by(ReviewDB.id)
    return db.execute(stmt).scalars().all()

USER_SERVICE_BASE_URL = os.getenv("USER_SERVICE_BASE_URL", "http://user-service:8000").rstrip("/")


## Create Review ##
@app.post("/api/reviews", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(payload: ReviewCreate, db: Session = Depends(get_db)):

    url = f"{USER_SERVICE_BASE_URL}/api/users/{payload.user_id}"
    try:
        resp = httpx.get(url, timeout=3.0)
    except:
        raise HTTPException(status_code=503, detail="User service unavailable")

    print("Calling user-service URL:", url)
    print("Status code from user-service:", resp.status_code)
    print("Response body:", resp.text)

    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="User not found")

    if resp.status_code >= 500:
        raise HTTPException(status_code=503, detail="User service unavailable")

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Error verifying user")
    
    review = ReviewDB(**payload.model_dump())
    db.add(review)
    try:
        db.commit()
        db.refresh(review)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="User already reviewed this movie")
    return review

## Return reviews with user ID ##
@app.get("/api/reviews/user/{user_id}", response_model=list[ReviewRead])
def reviews_by_user_id(user_id: int, db: Session = Depends(get_db)):
    stmt = select(ReviewDB).where(ReviewDB.user_id == user_id).order_by(ReviewDB.id)
    return db.execute(stmt).scalars().all()

## Get review by ID ##
@app.get("/api/reviews/{id}", response_model=ReviewRead)
def get_review(id: int, db: Session = Depends(get_db)):
    review = db.get(ReviewDB, id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found") 
    return review

## Delete a review ##
@app.delete("/api/reviews/{id}", status_code=204)
def delete_review(id: int, db: Session = Depends(get_db)) -> Response: 
    review = db.get(ReviewDB, id) 
    if not review: 
        raise HTTPException(status_code=404, detail="Review not found") 
    db.delete(review)
    db.commit() 
    return Response(status_code=status.HTTP_204_NO_CONTENT)