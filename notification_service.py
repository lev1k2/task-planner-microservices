import uuid
from datetime import datetime
from enum import Enum
from fastapi import FastAPI
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NotificationService")

app = FastAPI(title="Notification Service")

class TaskStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPayload(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    status: TaskStatus
    created_at: datetime

@app.post("/api/webhooks/task_created")
async def handle_task_created(payload: TaskPayload):
    # Логирование (симуляция отправки уведомления)
    logger.info(f" [УВЕДОМЛЕНИЕ] Создана новая задача! ID: {payload.id} | Название: {payload.title}")
    return {"status": "success", "message": "Notification logged"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
