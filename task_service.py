import uuid
from datetime import datetime, timezone
from enum import Enum
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaskService")

app = FastAPI(title="Task Service")

# URL соседнего сервиса уведомлений
NOTIFICATION_SERVICE_URL = "http://127.0.0"

class TaskStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskCreate(BaseModel):
    title: str
    description: str

class Task(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    status: TaskStatus
    created_at: datetime

# Отправка вебхука с обработкой ошибок
async def send_notification_webhook(task: Task):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(NOTIFICATION_SERVICE_URL, json=task.model_dump(mode='json'), timeout=5.0)
            if response.status_code == 200:
                logger.info(f"Уведомление для задачи {task.id} успешно отправлено.")
            else:
                logger.error(f"Notification Service вернул код {response.status_code}")
    except httpx.RequestError as exc:
        logger.error(f"Ошибка сети при отправке вебхука для задачи {task.id}: {exc}.")

@app.post("/api/tasks", response_model=Task, status_code=201)
async def create_task(task_in: TaskCreate, background_tasks: BackgroundTasks):
    new_task = Task(
        id=uuid.uuid4(),
        title=task_in.title,
        description=task_in.description,
        status=TaskStatus.NEW,
        created_at=datetime.now(timezone.utc)
    )
    
    # Отправляем вебхук в фоне
    background_tasks.add_task(send_notification_webhook, new_task)
    
    return new_task

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
