from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()

DATABASE_URL = "sqlite:///./todo.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    is_done = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)


class Task(BaseModel):
    id: int
    title: str
    is_done: bool = False


@app.post("/tasks")
def create_task(task: Task):
    db = SessionLocal()

    new_task = TaskDB(
        id=task.id,
        title=task.title,
        is_done=task.is_done
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    db.close()

    return new_task


@app.get("/tasks")
def get_tasks():
    db = SessionLocal()
    tasks = db.query(TaskDB).all()
    db.close()
    return tasks

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task):
    db = SessionLocal()

    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()

    if task is None:
        db.close()
        return {"error": "Task not found"}

    task.title = updated_task.title
    task.is_done = updated_task.is_done

    db.commit()
    db.refresh(task)
    db.close()

    return {"message": "Task updated!", "task": task}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    db = SessionLocal()

    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()

    if task is None:
        db.close()
        return {"error": "Task not found"}

    db.delete(task)
    db.commit()
    db.close()
    return {"message": "Task deleted!"}

