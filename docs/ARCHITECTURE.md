# ARCHITECTURE — Питомец ТПУ 🐶

## 1. Обзор системы

```
┌──────────────────┐     HTTP/JSON      ┌──────────────────┐
│                  │  ←───────────────→  │                  │
│  Frontend        │                    │  Backend (API)   │
│  HTML/CSS/JS     │                    │  FastAPI         │
│  (браузер)       │                    │  Python 3.11+    │
│                  │                    │                  │
└──────────────────┘                    └────────┬─────────┘
                                                 │
                                        ┌────────┴─────────┐
                                        │                  │
                                   ┌────┴────┐      ┌──────┴──────┐
                                   │ SQLite  │      │ LLM Service │
                                   │ (файл)  │      │ (адаптер)   │
                                   └─────────┘      └─────────────┘
                                                          │
                                                ┌─────────┴─────────┐
                                                │                   │
                                          ┌─────┴─────┐    ┌───────┴───────┐
                                          │ Local     │    │ Cloud API     │
                                          │ (Ollama)  │    │ (OpenRouter)  │
                                          └───────────┘    └───────────────┘
```

**Принцип:** монолитное приложение. Один сервер FastAPI отдаёт и API, и статические файлы фронтенда. Никаких отдельных серверов для фронтенда.

---

## 2. Структура проекта (файловое дерево)

```
tpu-pet/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app, CORS, роутинг, раздача статики
│   │   ├── config.py            # Настройки из .env (DATABASE_URL, JWT_SECRET, LLM_PROVIDER)
│   │   ├── database.py          # SQLAlchemy engine, SessionLocal, Base
│   │   ├── models.py            # ORM-модели (User, Pet, Task)
│   │   ├── schemas.py           # Pydantic-схемы (request/response)
│   │   ├── auth.py              # Хэширование, JWT create/verify, dependency get_current_user
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth_router.py   # POST /api/auth/register, /api/auth/login
│   │   │   ├── pet_router.py    # GET /api/pet, PUT /api/pet/name
│   │   │   ├── task_router.py   # CRUD задач + activate + complete
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── pet_service.py   # recompute_hunger, apply_penalty, level_up logic
│   │   │   ├── task_service.py  # activate_tasks, complete_task, streak_check, check_overdue_tasks
│   │   │   ├── llm_service.py   # LLM-адаптер: local / cloud / fallback
│   │   ├── scheduler.py         # APScheduler: периодический пересчёт голода (опционально)
│   ├── requirements.txt
│   ├── .env.example
├── frontend/
│   ├── index.html               # Точка входа (SPA-like через JS-роутинг)
│   ├── css/
│   │   ├── style.css            # Основные стили
│   │   ├── responsive.css       # Медиа-запросы для мобильных
│   ├── js/
│   │   ├── app.js               # Роутер (переключение страниц), инициализация
│   │   ├── api.js               # fetch-обёртка для всех API-вызовов + JWT
│   │   ├── auth.js              # Логика страницы входа/регистрации
│   │   ├── pet.js               # Логика главной страницы (питомец)
│   │   ├── tasks.js             # Логика страницы задач
│   │   ├── chat.js              # Заглушка чата
│   ├── assets/
│   │   ├── images/              # Картинки питомца (заглушки → потом реальные)
│   │   ├── icons/               # Иконки навигации
├── prompts/
│   ├── bulk_evaluate.txt        # Промпт для LLM (оценка задач)
├── tests/
│   ├── test_hunger.py           # Тесты: hunger decay, penalty
│   ├── test_exp.py              # Тесты: level up, exp calculation
│   ├── test_tasks.py            # Тесты: activate, complete, streak
│   ├── test_overdue.py          # Тесты: штраф за пропуск дедлайна
│   ├── test_auth.py             # Тесты: register, login, JWT
│   ├── conftest.py              # Фикстуры pytest
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT_PLAN.md
│   ├── CLAUDE_CODE_INSTRUCTIONS.md
├── deployment/
│   ├── docker-compose.yml       # Опционально
│   ├── systemd/
│   │   ├── tpu-pet.service      # systemd-юнит для продакшена
│   ├── nginx.conf               # Проксирование (опционально)
├── .gitignore
├── README.md
```

---

## 3. Backend — детали

### 3.1 FastAPI + раздача статики

FastAPI отдаёт фронтенд как статические файлы. Это избавляет от необходимости отдельного веб-сервера на этапе разработки.

```
# Принцип (не код, а описание):
# 1. Все /api/* маршруты обрабатываются роутерами
# 2. Всё остальное — отдаёт файлы из frontend/
# 3. Если файл не найден — отдаёт index.html (SPA fallback)
```

### 3.2 Конфигурация (.env)

| Переменная | Пример | Описание |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./tpu_pet.db` | Строка подключения SQLAlchemy |
| `JWT_SECRET` | `supersecretkey123` | Секрет для подписи JWT |
| `JWT_EXPIRE_DAYS` | `7` | Срок жизни токена |
| `LLM_PROVIDER` | `fallback` | `local` / `cloud` / `fallback` |
| `LLM_API_URL` | `http://localhost:11434/api/generate` | URL для локального Ollama |
| `LLM_API_KEY` | `sk-...` | API-ключ для облачного провайдера |
| `LLM_MODEL` | `qwen2.5:7b` | Имя модели |
| `LLM_TIMEOUT` | `30` | Таймаут LLM-запроса в секундах |

### 3.3 Аутентификация

- **Регистрация:** email + пароль → bcrypt hash → сохранение в БД → автоматическое создание питомца → возврат JWT
- **Вход:** email + пароль → проверка hash → возврат JWT
- **JWT:** HS256, payload = `{user_id, exp}`, передаётся в заголовке `Authorization: Bearer <token>`
- **Middleware:** dependency `get_current_user` декодирует токен, возвращает user_id. Если токен невалиден → 401

### 3.4 LLM-адаптер (llm_service.py)

Три режима, переключение через `LLM_PROVIDER`:

**`local`** — Qwen через Ollama (HTTP POST на `LLM_API_URL`):
- Формат запроса: Ollama API (`/api/generate`)
- Модель: `qwen2.5:7b` или аналог

**`cloud`** — облачный API (OpenRouter / Together AI):
- Формат запроса: OpenAI-совместимый (`/v1/chat/completions`)
- Нужен `LLM_API_KEY`

**`fallback`** — без LLM:
- Все задачи получают: `difficulty=medium, exp_reward=25, hunger_reward=20`

**Общий интерфейс:**

```
Вход: список строк (заголовки задач)
Выход: список объектов {task_title, difficulty, exp_reward, hunger_reward}
```

**Валидация ответа LLM:**
1. Ответ должен быть валидным JSON
2. difficulty ∈ {low, medium, high}
3. exp_reward и hunger_reward — в пределах диапазонов для данной difficulty
4. Если что-то невалидно → для этой задачи применяется fallback

---

## 4. База данных

### 4.1 SQLite + SQLAlchemy

- Файл БД: `tpu_pet.db` в корне backend/
- ORM: SQLAlchemy 2.0 (declarative)
- Миграции: для MVP НЕ используем Alembic — БД пересоздаётся при первом запуске
- **Путь миграции на PostgreSQL:** замена `DATABASE_URL` в .env (SQLAlchemy абстрагирует)

### 4.2 Схема таблиц

#### Таблица `users`

| Поле | Тип | Ограничения |
|---|---|---|
| id | INTEGER | PK, autoincrement |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| created_at | DATETIME | DEFAULT now |

#### Таблица `pets`

| Поле | Тип | Ограничения |
|---|---|---|
| id | INTEGER | PK, autoincrement |
| user_id | INTEGER | FK → users.id, UNIQUE |
| name | VARCHAR(100) | DEFAULT 'Студент-корги' |
| level | INTEGER | DEFAULT 0, CHECK 0–3 |
| current_exp | FLOAT | DEFAULT 0 |
| hunger | FLOAT | DEFAULT 100 |
| last_hunger_update | DATETIME | DEFAULT now |
| hunger_zero_since | DATETIME | NULLABLE (время, когда голод впервые стал 0) |
| created_at | DATETIME | DEFAULT now |

#### Таблица `tasks`

| Поле | Тип | Ограничения |
|---|---|---|
| id | INTEGER | PK, autoincrement |
| user_id | INTEGER | FK → users.id |
| title | VARCHAR(200) | NOT NULL |
| category | VARCHAR(50) | NOT NULL |
| deadline | DATE | NOT NULL |
| difficulty | VARCHAR(10) | NULLABLE (low/medium/high) |
| exp_reward | FLOAT | NULLABLE |
| hunger_reward | FLOAT | NULLABLE |
| is_activated | BOOLEAN | DEFAULT false |
| is_completed | BOOLEAN | DEFAULT false |
| is_overdue | BOOLEAN | DEFAULT false |
| created_at | DATETIME | DEFAULT now |
| completed_at | DATETIME | NULLABLE |

#### Таблица `llm_logs` (опциональная, для отладки)

| Поле | Тип | Ограничения |
|---|---|---|
| id | INTEGER | PK |
| user_id | INTEGER | FK → users.id |
| request_text | TEXT | Промпт (без PII) |
| response_text | TEXT | Ответ LLM |
| provider | VARCHAR(20) | local/cloud/fallback |
| created_at | DATETIME | DEFAULT now |

---

## 5. API-контракт

### 5.1 Аутентификация

**POST /api/auth/register**
```
Request:  { "email": "student@mail.ru", "password": "secret123" }
Success:  201 { "token": "eyJ...", "user_id": 1 }
Error:    400 { "detail": "Email уже зарегистрирован" }
Error:    422 { "detail": "Некорректный формат email" }
```

**POST /api/auth/login**
```
Request:  { "email": "student@mail.ru", "password": "secret123" }
Success:  200 { "token": "eyJ...", "user_id": 1 }
Error:    401 { "detail": "Неверный email или пароль" }
```

### 5.2 Питомец

**GET /api/pet** *(требует JWT)*
```
Response: 200 {
  "id": 1,
  "name": "Студент-корги",
  "level": 1,
  "current_exp": 85.0,
  "required_exp": 300.0,
  "hunger": 72.5,
  "mood": "neutral",
  "image": "pet_level1_neutral.png"
}
```
> Hunger, штрафы за голод и штрафы за просроченные дедлайны пересчитываются при каждом GET-запросе.

**PUT /api/pet/name** *(требует JWT)*
```
Request:  { "name": "Барсик" }
Success:  200 { "name": "Барсик" }
Error:    422 { "detail": "Имя не может быть пустым" }
```

### 5.3 Задачи

**GET /api/tasks** *(требует JWT)*
```
Response: 200 {
  "tasks": [
    {
      "id": 1,
      "title": "Сделать лабу по физике",
      "category": "Физика",
      "deadline": "15.04.2026",
      "difficulty": "medium",
      "exp_reward": 30,
      "hunger_reward": 25,
      "is_activated": true,
      "is_completed": false
    }
  ]
}
```
> Задачи отсортированы по категориям, затем по дедлайну.
> Перед возвратом: сервер проверяет просроченные задачи (deadline < today, is_activated=true, is_completed=false, is_overdue=false), применяет штраф (вычитает exp_reward и hunger_reward из питомца), помечает их is_overdue=true. Просроченные задачи НЕ возвращаются в списке.

**POST /api/tasks** *(требует JWT)*
```
Request:  { "title": "Сделать лабу по физике", "category": "Физика", "deadline": "15.04.2026" }
Success:  201 { "id": 1, "title": "...", ... , "is_activated": false }
```

**PUT /api/tasks/{id}** *(требует JWT)*
```
Request:  { "title": "Новый заголовок", "category": "Физика", "deadline": "20.04.2026" }
Success:  200 { ... задача с is_activated: false, difficulty: null, rewards: null }
```
> При редактировании активированной задачи — награда сбрасывается.

**DELETE /api/tasks/{id}** *(требует JWT)*
```
Success:  200 { "detail": "Задача удалена" }
Error:    404 { "detail": "Задача не найдена" }
```

**POST /api/tasks/activate** *(требует JWT)*
```
Request:  (пустое тело)
Success:  200 {
  "activated_count": 3,
  "tasks": [ ... задачи с назначенными наградами ]
}
Error:    200 { "activated_count": 0, "message": "Нет новых задач для активации" }
```

**POST /api/tasks/{id}/complete** *(требует JWT)*
```
Success:  200 {
  "exp_gained": 37,
  "hunger_gained": 25,
  "streak_active": true,
  "streak_multiplier": 1.25,
  "level_up": false,
  "pet": { ... обновлённое состояние питомца }
}
Error:    400 { "detail": "Задача не активирована" }
Error:    400 { "detail": "Задача уже выполнена" }
```

### 5.4 Коды ответов (общие)

| Код | Когда |
|---|---|
| 200 | Успех |
| 201 | Создан ресурс |
| 400 | Бизнес-ошибка (не активирована, уже выполнена и т.д.) |
| 401 | Не авторизован / токен невалиден |
| 404 | Ресурс не найден |
| 422 | Ошибка валидации (Pydantic) |
| 500 | Внутренняя ошибка сервера |

---

## 6. Frontend — детали

### 6.1 Подход: SPA без фреймворка

Один `index.html` загружает все JS-модули. Переключение «страниц» — через показ/скрытие div-секций (display: none/block). URL не меняется (для MVP это допустимо).

**Альтернатива (если потребуется):** хэш-роутинг (`#/pet`, `#/tasks`, `#/chat`) — реализуется 20 строками JS.

### 6.2 API-обёртка (api.js)

Единый модуль для всех fetch-запросов:
- Автоматически добавляет `Authorization: Bearer <token>` из localStorage
- При 401 — очищает токен, показывает страницу входа
- Обрабатывает ошибки сети

### 6.3 Хранение JWT

- `localStorage.setItem('token', '...')` при входе/регистрации
- Удаление при выходе или при 401

### 6.4 Адаптивность

- Mobile-first подход
- Breakpoints: 480px (мобильный), 768px (планшет), 1024px+ (десктоп)
- Навигация: нижняя панель на мобильном, боковая или верхняя на десктопе

---

## 7. Безопасность

| Мера | Реализация |
|---|---|
| Пароли | bcrypt (passlib), минимум 6 символов |
| Аутентификация | JWT HS256, срок 7 дней |
| CORS | Настроен для конкретного домена (или `*` для dev) |
| Rate limiting | slowapi: 5 попыток/мин на /auth/login |
| SQL injection | SQLAlchemy ORM (параметризованные запросы) |
| XSS | Экранирование пользовательского ввода на фронте |
| LLM-инъекции | Валидация ответа LLM по JSON-схеме, не исполняем код из ответов |

---

## 8. Логирование

**Формат:** JSON (одна строка на запись).

```json
{
  "timestamp": "2026-04-01T12:00:00Z",
  "level": "INFO",
  "event": "llm_request",
  "user_id": 42,
  "provider": "local",
  "task_count": 3,
  "response_time_ms": 1200,
  "success": true
}
```

**Правила:**
- Никогда не логировать email, пароль, JWT-токен
- user_id — допустимо (внутренний ID)
- Содержимое задач — допустимо (нет PII)
- LLM-ответы — логировать в llm_logs таблицу (для отладки)
