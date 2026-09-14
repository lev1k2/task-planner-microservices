# API Contract v1.0

## Схема данных Task (JSON)
{
  "id": "uuid4",
  "title": "string",
  "description": "string",
  "status": "new | in_progress | done",
  "created_at": "ISO8601 string"
}

## Эндпоинты

### 1. Task Service
* **Запрос:** POST `/api/tasks`
* **Тело запроса:**
  ```json
  {
    "title": "Купить молоко",
    "description": "В магазине у дома"
  }
  ```
* **Ответ:** Код `201 Created`

### 2. Notification Service (Webhook)
* **Запрос:** POST `/api/webhooks/task_created`
* **Тело запроса:** Полный объект Task.
* **Ответ:** Код `200 OK`
