import os
import logging
import time
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from database import engine, get_db, Base
from models import Todo
from schemas import TodoCreate, TodoUpdate, TodoResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables with retry logic
def init_db():
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            return
        except OperationalError as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"Failed to connect to database, retrying... ({retry_count}/{max_retries})")
                time.sleep(2)
            else:
                logger.error(f"Failed to create database tables after {max_retries} retries")
                raise

# Initialize database on startup
init_db()

app = FastAPI(title="Todo API", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    logger.info("Home endpoint called")
    return {"message": "Todo API is running"}


@app.get("/health")
def health_check():
    logger.info("Health check called")
    return {"status": "healthy"}


# Todo endpoints
@app.get("/todos", response_model=list[TodoResponse])
def get_todos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get all todos with pagination"""
    logger.info(f"Fetching todos with skip={skip}, limit={limit}")
    todos = db.query(Todo).offset(skip).limit(limit).all()
    return todos


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """Get a specific todo by ID"""
    logger.info(f"Fetching todo with id={todo_id}")
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        logger.error(f"Todo with id={todo_id} not found")
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post("/todos", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    """Create a new todo"""
    logger.info(f"Creating todo with title={todo.title}")
    db_todo = Todo(title=todo.title, description=todo.description)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    logger.info(f"Todo created with id={db_todo.id}")
    return db_todo


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_db)):
    """Update a todo"""
    logger.info(f"Updating todo with id={todo_id}")
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        logger.error(f"Todo with id={todo_id} not found")
        raise HTTPException(status_code=404, detail="Todo not found")
    
    update_data = todo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)
    
    db.add(todo)
    db.commit()
    db.refresh(todo)
    logger.info(f"Todo with id={todo_id} updated successfully")
    return todo


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Delete a todo"""
    logger.info(f"Deleting todo with id={todo_id}")
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        logger.error(f"Todo with id={todo_id} not found")
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(todo)
    db.commit()
    logger.info(f"Todo with id={todo_id} deleted successfully")
    return {"message": "Todo deleted successfully"}
