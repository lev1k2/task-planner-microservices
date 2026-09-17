import uuid
from datetime import datetime, timezone
from enum import Enum
from fastapi import FastAPI, BackgroundTasks, status
from pydantic import BaseModel
import httpx
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaskService")

app = FastAPI(title="Task Service")

# ИСПРАВЛЕНО: Полный и корректный URL-адрес сервиса уведомлений (порт 8002)
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

# ИСПРАВЛЕНО: Добавлен цикл на 3 повторные попытки при сбое сети или ошибках сервера
async def send_notification_webhook(task: Task):
    async with httpx.AsyncClient() as client:
        for attempt in range(1, 4):  # Интенсивно пытаемся отправить до 3 раз
            try:
                response = await client.post(
                    NOTIFICATION_SERVICE_URL, 
                    json=task.model_dump(mode='json'), 
                    timeout=5.0
                )
                if response.status_code == 200:
                    logger.info(f"Уведомление для задачи {task.id} успешно отправлено с попытки №{attempt}.")
                    return
                
                logger.warning(f"Попытка {attempt}: Notification Service вернул код {response.status_code}")
            
            except httpx.RequestError as exc:
                logger.error(f"Попытка {attempt}: Локальная точка отказа (сеть недоступна) для задачи {task.id}: {exc}")
        
        # Если все попытки исчерпаны, сервис не падает, а просто фиксирует критическую ошибку в лог
        logger.critical(f"Не удалось доставить вебхук для задачи {task.id} после 3 попыток.")

@app.post("/api/tasks", response_model=Task, status_code=201)
async def create_task(task_in: TaskCreate, background_tasks: BackgroundTasks):
    new_task = Task(
        id=uuid.uuid4(),
        title=task_in.title,
        description=task_in.description,
        status=TaskStatus.NEW,
        created_at=datetime.now(timezone.utc)
    )
    
    # Отправляем вебхук асинхронно в фоне
    background_tasks.add_task(send_notification_webhook, new_task)
    
    return new_task

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
