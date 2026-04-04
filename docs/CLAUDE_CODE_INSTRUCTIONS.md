# CLAUDE CODE INSTRUCTIONS — Питомец ТПУ 🐶

## Общие правила работы с Claude Code

### Перед началом работы

1. **Всегда начинай с контекста.** В начале каждой сессии дай Claude Code прочитать файлы проекта:
   ```
   Прочитай файлы: docs/PRD.md, docs/ARCHITECTURE.md, docs/DEVELOPMENT_PLAN.md
   ```

2. **Работай по одной задаче за раз.** Не проси сделать "весь backend" — проси конкретный файл или функцию.

3. **Проверяй после каждого шага.** После каждой генерации — запусти, проверь, только потом двигайся дальше.

4. **Не меняй уже работающий код без необходимости.** Если шаг работает — фиксируй и переходи к следующему.

### Правила промптов

- Указывай конкретный файл: «Создай файл `backend/app/models.py`»
- Указывай что должно быть внутри: описание, не абстракция
- Ссылайся на архитектуру: «Как описано в ARCHITECTURE.md, секция 4.2»
- Просьбы о тестах — отдельно от реализации
- Если Claude Code предлагает усложнение — откажись: «Нет, делаем проще, как в плане»

### Правила безопасности

- Никогда не вставляй реальные пароли или API-ключи в код
- Всё через `.env` файл
- В примерах: `email = "test@example.com"`, `password = "testpass123"`

---

## Промпты по шагам

### Шаг 1.1 — Структура проекта

```
Создай следующую структуру папок для проекта "tpu-pet":

tpu-pet/
├── backend/
│   ├── app/
│   │   ├── __init__.py (пустой)
│   │   ├── routers/
│   │   │   ├── __init__.py (пустой)
│   │   ├── services/
│   │   │   ├── __init__.py (пустой)
├── frontend/
│   ├── css/
│   ├── js/
│   ├── assets/
│   │   ├── images/
│   │   ├── icons/
├── prompts/
├── tests/
├── docs/
├── deployment/

Создай пустые __init__.py во всех Python-пакетах.
Создай .gitignore для Python-проекта (включи: __pycache__, .env, *.db, venv/).
```

### Шаг 1.2 — requirements.txt

```
Создай файл backend/requirements.txt со следующими зависимостями:

fastapi==0.115.0
uvicorn==0.30.0
sqlalchemy==2.0.35
pydantic==2.9.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-dotenv==1.0.1
httpx==0.27.0
apscheduler==3.10.4

Используй фиксированные версии. httpx нужен для запросов к LLM API.
```

### Шаг 1.3 — .env.example

```
Создай файл backend/.env.example:

DATABASE_URL=sqlite:///./tpu_pet.db
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRE_DAYS=7
LLM_PROVIDER=fallback
LLM_API_URL=http://localhost:11434/api/generate
LLM_API_KEY=
LLM_MODEL=qwen2.5:7b
LLM_TIMEOUT=30
```

### Шаг 1.4 — config.py

```
Создай файл backend/app/config.py.

Он должен:
- Читать переменные окружения из .env файла (используя python-dotenv)
- Содержать класс Settings со всеми переменными из .env.example
- Значения по умолчанию для всех переменных
- Экспортировать один экземпляр: settings = Settings()

Переменные: DATABASE_URL, JWT_SECRET, JWT_EXPIRE_DAYS (int), LLM_PROVIDER, LLM_API_URL, LLM_API_KEY, LLM_MODEL, LLM_TIMEOUT (int).
```

### Шаг 1.5 — database.py

```
Создай файл backend/app/database.py.

Он должен:
- Создать SQLAlchemy engine из settings.DATABASE_URL
- Если SQLite — добавить connect_args={"check_same_thread": False}
- Создать SessionLocal = sessionmaker(...)
- Создать Base = declarative_base()
- Создать функцию-генератор get_db() для dependency injection в FastAPI

Используй SQLAlchemy 2.0 стиль.
```

### Шаг 1.6 — models.py

```
Создай файл backend/app/models.py с ORM-моделями.

Используй SQLAlchemy declarative style. Модели:

1. User:
   - id: Integer, primary key, autoincrement
   - email: String(255), unique, not null
   - password_hash: String(255), not null
   - created_at: DateTime, default=now
   - relationship: pet (один к одному), tasks (один ко многим)

2. Pet:
   - id: Integer, primary key, autoincrement
   - user_id: Integer, ForeignKey("users.id"), unique, not null
   - name: String(100), default="Студент-корги"
   - level: Integer, default=0 (допустимо 0-3)
   - current_exp: Float, default=0
   - hunger: Float, default=100
   - last_hunger_update: DateTime, default=now
   - hunger_zero_since: DateTime, nullable=True (время, когда голод впервые стал 0)
   - created_at: DateTime, default=now

3. Task:
   - id: Integer, primary key, autoincrement
   - user_id: Integer, ForeignKey("users.id"), not null
   - title: String(200), not null
   - category: String(50), not null
   - deadline: Date, not null
   - difficulty: String(10), nullable (low/medium/high)
   - exp_reward: Float, nullable
   - hunger_reward: Float, nullable
   - is_activated: Boolean, default=False
   - is_completed: Boolean, default=False
   - is_overdue: Boolean, default=False
   - created_at: DateTime, default=now
   - completed_at: DateTime, nullable

Имена таблиц: "users", "pets", "tasks".
```

### Шаг 1.7 — main.py (минимальный)

```
Создай файл backend/app/main.py.

Он должен:
- Создать FastAPI app с title="TPU Pet API"
- При запуске (startup event или lifespan) — создать все таблицы через Base.metadata.create_all
- Добавить CORS middleware (allow_origins=["*"] для dev)
- Добавить один эндпоинт: GET /api/health → {"status": "ok"}
- Не подключать роутеры пока (их ещё нет)

Для запуска: uvicorn app.main:app --reload (из папки backend/)
```

### Шаг 1.9 — schemas.py

```
Создай файл backend/app/schemas.py с Pydantic-моделями.

Схемы:

1. UserCreate: email (EmailStr), password (str, min 6 символов)
2. UserLogin: email (str), password (str)
3. TokenResponse: token (str), user_id (int)

4. PetResponse: id, name, level, current_exp, required_exp (float), hunger, mood (str), image (str)
5. PetNameUpdate: name (str, min 1, max 100 символов)

6. TaskCreate: title (str, max 200), category (str, max 50), deadline (str в формате DD.MM.YYYY)
7. TaskUpdate: title (опционально), category (опционально), deadline (опционально)
8. TaskResponse: id, title, category, deadline, difficulty (optional), exp_reward (optional), hunger_reward (optional), is_activated, is_completed, is_overdue
9. TaskActivateResponse: activated_count (int), tasks (list[TaskResponse])
10. TaskCompleteResponse: exp_gained (float), hunger_gained (float), streak_active (bool), streak_multiplier (float), level_up (bool), pet (PetResponse)

Используй Pydantic v2 стиль (model_config, field validators).
Для deadline — валидатор, который проверяет формат DD.MM.YYYY.
```

### Шаг 1.10 — auth.py

```
Создай файл backend/app/auth.py.

Функции:
1. hash_password(password: str) -> str — используя passlib bcrypt
2. verify_password(password: str, hash: str) -> bool
3. create_access_token(user_id: int) -> str — JWT с payload {sub: user_id, exp: now + JWT_EXPIRE_DAYS}
4. decode_access_token(token: str) -> int — возвращает user_id или выбрасывает HTTPException 401

5. get_current_user — FastAPI Depends:
   - Извлекает токен из заголовка Authorization: Bearer <token>
   - Декодирует токен
   - Возвращает user_id (int)
   - Если токен невалиден → HTTPException 401

Используй settings из config.py для JWT_SECRET и JWT_EXPIRE_DAYS.
Алгоритм JWT: HS256.
```

### Шаг 1.11–1.12 — auth_router.py

```
Создай файл backend/app/routers/auth_router.py.

Два эндпоинта:

1. POST /api/auth/register
   - Принимает: UserCreate (email + password)
   - Проверяет: email не занят (иначе 400)
   - Создаёт пользователя (hash password)
   - Автоматически создаёт питомца (name="Студент-корги", level=0, hunger=100, exp=0)
   - Возвращает: TokenResponse (token + user_id), статус 201

2. POST /api/auth/login
   - Принимает: UserLogin (email + password)
   - Проверяет: пользователь существует и пароль верный (иначе 401)
   - Возвращает: TokenResponse (token + user_id), статус 200

Не забудь подключить роутер в main.py: app.include_router(auth_router)
```

### Шаг 1.15–1.16 — pet_router.py

```
Создай файл backend/app/routers/pet_router.py.

Два эндпоинта (оба требуют JWT — используй Depends(get_current_user)):

1. GET /api/pet
   - Находит питомца текущего пользователя
   - Пока БЕЗ пересчёта голода (это будет в неделю 2)
   - Возвращает PetResponse с:
     - required_exp = 200 * (1.5 ** level)
     - mood = "happy" если hunger > 80, "neutral" если 21-80, "sad" если 0-20
     - image = f"pet_level{level}_{mood}.png"

2. PUT /api/pet/name
   - Принимает: PetNameUpdate
   - Обновляет имя питомца
   - Возвращает: {"name": новое_имя}

Подключи роутер в main.py.
```

### Шаг 1.17–1.20 — task_router.py (CRUD)

```
Создай файл backend/app/routers/task_router.py.

Четыре эндпоинта (все требуют JWT):

1. GET /api/tasks
   - Перед возвратом: вызвать check_overdue_tasks(user_id) для применения штрафов за просроченные дедлайны
   - Возвращает все задачи пользователя где is_completed=false И is_overdue=false
   - Сортировка: по категории (алфавит), внутри категории — по дедлайну
   - Формат дедлайна в ответе: DD.MM.YYYY

2. POST /api/tasks
   - Принимает: TaskCreate
   - Создаёт задачу (is_activated=false, is_completed=false)
   - Возвращает: TaskResponse, статус 201

3. PUT /api/tasks/{task_id}
   - Принимает: TaskUpdate (частичное обновление)
   - Проверяет: задача принадлежит текущему пользователю
   - Если задача была активирована — сбрасывает: difficulty=null, exp_reward=null, hunger_reward=null, is_activated=false
   - Возвращает: TaskResponse

4. DELETE /api/tasks/{task_id}
   - Проверяет: задача принадлежит текущему пользователю
   - Удаляет задачу
   - Возвращает: {"detail": "Задача удалена"}
   - Если не найдена: 404

Подключи роутер в main.py.
```

### Шаг 2.1–2.5 — pet_service.py (голод и штрафы)

```
Создай файл backend/app/services/pet_service.py.

Функции:

1. recompute_hunger(pet: Pet, db: Session) -> None
   - Рассчитывает прошедшее время с last_hunger_update
   - hunger = max(0, pet.hunger - elapsed_hours * (100 / 48))
   - Обновляет pet.last_hunger_update = now
   - Если hunger стал 0 и hunger_zero_since is None → устанавливаем hunger_zero_since = now
   - Если hunger > 0 → hunger_zero_since = None
   - Сохраняет в БД

2. apply_exp_penalty(pet: Pet, db: Session) -> None
   - Если pet.hunger_zero_since is not None:
     - penalty_hours = (now - hunger_zero_since).total_seconds() / 3600
     - penalty = floor(penalty_hours) * 10
     - pet.current_exp = max(0, pet.current_exp - penalty)
   - НЕ понижает уровень

3. get_mood(hunger: float) -> str
   - 0-20 → "sad"
   - 21-80 → "neutral"
   - 81-100 → "happy"

4. get_required_exp(level: int) -> float
   - return 200 * (1.5 ** level)

5. get_pet_image(level: int, mood: str) -> str
   - return f"pet_level{level}_{mood}.png"

После создания — обнови GET /api/pet в pet_router.py:
вызывай recompute_hunger и apply_exp_penalty перед возвратом данных.
```

### Шаг 2.8 — Промпт для LLM

```
Создай файл prompts/bulk_evaluate.txt со следующим содержимым (на английском):

---
PROMPT FILE: bulk_evaluate.txt
PURPOSE: Evaluate a batch of student tasks and assign difficulty + rewards.
USAGE: Called from llm_service.py when user clicks "Activate tasks".

INPUT FORMAT (injected into prompt):
A JSON array of task titles, e.g.: ["Buy water", "Complete English test", "Prepare for calculus exam"]

PROMPT:
You are a task difficulty evaluator for a student productivity app.

Given a list of student task titles, evaluate each task and assign:
- difficulty: "low", "medium", or "high"
- exp_reward: integer within the range for that difficulty
- hunger_reward: integer within the range for that difficulty

Difficulty ranges:
- low: simple daily tasks (e.g., "drink water", "check email"). exp: 10-20, hunger: 5-15
- medium: regular academic tasks (e.g., "complete English test", "read chapter 5"). exp: 25-40, hunger: 20-35
- high: complex/long tasks (e.g., "prepare for calculus exam", "write term paper"). exp: 60-80, hunger: 50-70

Respond ONLY with a valid JSON array. No extra text, no markdown.

RESPONSE SCHEMA:
[
  {
    "title": "exact task title from input",
    "difficulty": "low" | "medium" | "high",
    "exp_reward": <integer>,
    "hunger_reward": <integer>
  }
]

EXAMPLE INPUT:
["Не забыть попить воды", "Выполнить тест по английскому языку", "Подготовиться к экзамену по высшей математике"]

EXPECTED OUTPUT:
[
  {"title": "Не забыть попить воды", "difficulty": "low", "exp_reward": 12, "hunger_reward": 8},
  {"title": "Выполнить тест по английскому языку", "difficulty": "medium", "exp_reward": 30, "hunger_reward": 25},
  {"title": "Подготовиться к экзамену по высшей математике", "difficulty": "high", "exp_reward": 70, "hunger_reward": 60}
]

VALIDATION RULES:
1. Response must be valid JSON array
2. Array length must equal input array length
3. difficulty must be one of: "low", "medium", "high"
4. exp_reward and hunger_reward must be integers within the ranges above
5. If any rule is violated for a task → use fallback: difficulty="medium", exp_reward=25, hunger_reward=20

FALLBACK BEHAVIOR:
If the entire response is unparseable → all tasks get: difficulty="medium", exp_reward=25, hunger_reward=20
---
```

### Шаг 2.9–2.13 — llm_service.py

```
Создай файл backend/app/services/llm_service.py.

Реализуй функцию:

async def evaluate_tasks(titles: list[str]) -> list[dict]:
    """
    Возвращает список: [{"title": str, "difficulty": str, "exp_reward": int, "hunger_reward": int}]
    """

Логика:
1. Читаем settings.LLM_PROVIDER
2. Если "fallback" → сразу возвращаем medium/25/20 для каждой задачи
3. Если "local" → отправляем HTTP POST на settings.LLM_API_URL (Ollama формат):
   - body: {"model": settings.LLM_MODEL, "prompt": <промпт из bulk_evaluate.txt с подставленными titles>, "stream": false}
   - timeout: settings.LLM_TIMEOUT секунд
4. Если "cloud" → отправляем HTTP POST на settings.LLM_API_URL (OpenAI формат):
   - headers: {"Authorization": f"Bearer {settings.LLM_API_KEY}"}
   - body: {"model": settings.LLM_MODEL, "messages": [{"role": "user", "content": <промпт>}]}
5. Парсим ответ как JSON
6. Валидируем каждый элемент:
   - difficulty in ["low", "medium", "high"]
   - exp_reward в допустимом диапазоне для difficulty
   - hunger_reward в допустимом диапазоне для difficulty
7. Невалидные элементы → fallback значения
8. При любой ошибке (timeout, JSON parse error, network error) → логируем ошибку, возвращаем fallback для всех задач

Используй httpx для HTTP-запросов (async).
Загружай текст промпта из файла prompts/bulk_evaluate.txt.

ДИАПАЗОНЫ для валидации:
RANGES = {
    "low":    {"exp": (10, 20),  "hunger": (5, 15)},
    "medium": {"exp": (25, 40),  "hunger": (20, 35)},
    "high":   {"exp": (60, 80),  "hunger": (50, 70)},
}
```

### Шаг 2.16–2.19 — task_service.py (complete + streak + level_up)

```
Создай файл backend/app/services/task_service.py.

Функции:

1. check_streak(user_id: int, db: Session) -> tuple[bool, float]:
   - Считает количество задач, выполненных за последние 24 часа
   - Если больше 3 → return (True, 1.25)
   - Иначе → return (False, 1.0)

2. complete_task(task_id: int, user_id: int, db: Session) -> dict:
   - Проверяет: задача существует, принадлежит пользователю, активирована, не выполнена
   - Если нет → raise HTTPException
   - Проверяет стрик
   - Рассчитывает: final_exp = floor(task.exp_reward * multiplier)
   - Рассчитывает: final_hunger = floor(task.hunger_reward * multiplier)
   - Обновляет питомца:
     - pet.hunger = min(100, pet.hunger + final_hunger)
     - pet.current_exp += final_exp
     - Если hunger стал > 0 → pet.hunger_zero_since = None
   - Проверяет level_up:
     - required = get_required_exp(pet.level)
     - Если pet.current_exp >= required И pet.level < 3:
       - pet.level += 1
       - pet.current_exp = 0 (излишек НЕ переносится)
       - level_up = True
   - Отмечает задачу выполненной: is_completed=True, completed_at=now
   - Возвращает dict с данными для TaskCompleteResponse
```

### Шаг 2.14 — POST /api/tasks/activate

```
Добавь в backend/app/routers/task_router.py эндпоинт:

POST /api/tasks/activate (требует JWT)

Логика:
1. Найти все задачи пользователя где is_activated=False и is_completed=False
2. Если таких нет → вернуть {"activated_count": 0, "message": "Нет новых задач для активации"}
3. Собрать список заголовков (titles)
4. Вызвать llm_service.evaluate_tasks(titles)
5. Для каждой задачи записать: difficulty, exp_reward, hunger_reward, is_activated=True
6. Сохранить в БД
7. Вернуть TaskActivateResponse
```

### Шаг 2.18 — POST /api/tasks/{id}/complete

```
Добавь в backend/app/routers/task_router.py эндпоинт:

POST /api/tasks/{task_id}/complete (требует JWT)

Логика:
1. Сначала вызвать recompute_hunger и apply_exp_penalty для питомца (чтобы данные актуальны)
2. Вызвать task_service.complete_task(task_id, user_id, db)
3. Вернуть TaskCompleteResponse
```

### Шаг 2.22–2.23 — check_overdue_tasks (штраф за пропуск дедлайна)

```
Добавь в backend/app/services/task_service.py новую функцию:

def check_overdue_tasks(user_id: int, db: Session) -> int:
    """
    Проверяет все активированные, невыполненные, непросроченные задачи пользователя.
    Если deadline < today → применяет штраф и помечает задачу как просроченную.
    Возвращает количество задач, по которым применён штраф.
    """

Логика:
1. Найти все задачи пользователя где:
   - is_activated = True
   - is_completed = False
   - is_overdue = False
   - deadline < date.today()
2. Для каждой такой задачи:
   - Получить питомца пользователя
   - pet.current_exp = max(0, pet.current_exp - task.exp_reward)
   - pet.hunger = max(0, pet.hunger - task.hunger_reward)
   - Если pet.hunger == 0 и pet.hunger_zero_since is None → установить hunger_zero_since = now
   - task.is_overdue = True
3. Сохранить изменения в БД
4. Вернуть количество обработанных задач

ВАЖНО:
- Уровень питомца НЕ понижается
- EXP не ниже 0, hunger не ниже 0
- Штраф применяется ОДИН РАЗ (is_overdue = True предотвращает повторный штраф)
- Неактивированные задачи НЕ штрафуются (у них нет назначенной награды)

---

После создания функции — обнови два эндпоинта:

1. GET /api/pet (в pet_router.py):
   - Перед возвратом данных вызвать check_overdue_tasks(user_id, db)
   
2. GET /api/tasks (в task_router.py):
   - Перед возвратом списка вызвать check_overdue_tasks(user_id, db)
   - Возвращать только задачи где is_completed=False И is_overdue=False
```

### Шаг 2.24 — test_overdue.py

```
Создай файл tests/test_overdue.py.

Тесты:

1. test_overdue_applies_penalty
   - Задача: activated=True, deadline=вчера, exp_reward=30, hunger_reward=25
   - Питомец: exp=100, hunger=80
   - После check_overdue_tasks → exp=70, hunger=55, task.is_overdue=True

2. test_overdue_not_activated
   - Задача: activated=False, deadline=вчера
   - check_overdue_tasks → задача НЕ помечена как overdue, штраф НЕ применён

3. test_overdue_already_completed
   - Задача: activated=True, completed=True, deadline=вчера
   - check_overdue_tasks → штраф НЕ применён (задача выполнена вовремя)

4. test_overdue_already_marked
   - Задача: is_overdue=True, deadline=вчера
   - check_overdue_tasks → штраф НЕ применён повторно

5. test_overdue_exp_not_below_zero
   - Питомец: exp=10, задача: exp_reward=50
   - После штрафа → exp=0 (не -40)

6. test_overdue_hunger_not_below_zero
   - Питомец: hunger=5, задача: hunger_reward=30
   - После штрафа → hunger=0 (не -25)

7. test_overdue_multiple_tasks
   - 3 просроченные задачи (rewards: 20+30+40 exp)
   - Питомец: exp=100
   - После штрафа → exp=10 (100-20-30-40)

8. test_overdue_deadline_today_not_penalized
   - Задача: deadline=сегодня
   - check_overdue_tasks → штраф НЕ применён (deadline < today, не <=)

9. test_overdue_level_not_decreased
   - Питомец: level=2, exp=0, задача: exp_reward=50
   - После штрафа → level=2, exp=0 (уровень не понижается)

Используй фикстуры из conftest.py. Для управления датами используй monkeypatch или freezegun.
```

### Шаги 3.1–3.28 — Frontend

```
ОБЩИЙ КОНТЕКСТ ДЛЯ ВСЕХ ФРОНТЕНД-ЗАДАЧ:

Прочитай docs/PRD.md и docs/ARCHITECTURE.md (секция 6).

Технологии: чистый HTML + CSS + JS (без фреймворков, без npm, без сборки).
Подход: один index.html, переключение секций через display:none/block.
Стиль: mobile-first, палитра бежево-жёлто-оранжевая.
API-обёртка: все запросы через api.js, JWT в localStorage.
```

**Промпт для 3.1 (index.html):**

```
Создай файл frontend/index.html.

Структура:
- <head>: meta viewport, подключение css/style.css и css/responsive.css
- <body>:
  - <div id="page-auth"> — секция входа/регистрации
  - <div id="page-pet"> — секция питомца (главная)
  - <div id="page-tasks"> — секция задач
  - <div id="page-chat"> — секция чата
  - <nav id="bottom-nav"> — нижняя навигация (4 кнопки: главная, задания, чат, выход)
- Перед </body>: подключение js/api.js, js/auth.js, js/pet.js, js/tasks.js, js/chat.js, js/app.js (именно в этом порядке)

Все секции page-* по умолчанию display:none.
Навигация по умолчанию display:none (показывается после входа).

Секция auth содержит:
- Два режима: вход и регистрация (переключение ссылкой "Нет аккаунта?" / "Уже есть аккаунт?")
- Поля: email, пароль (+ подтверждение для регистрации)
- Кнопка отправки

Палитра: фон #FFF8F0, акцент #FF9800, текст #333333, ошибка #E53935.
```

**Промпт для 3.5 (api.js):**

```
Создай файл frontend/js/api.js.

Это модуль-обёртка для всех API-запросов.

Глобальный объект API с методами:
- API.baseUrl = "" (пустая строка, т.к. бэкенд и фронт на одном сервере)
- API.getToken() — возвращает токен из localStorage
- API.setToken(token) — сохраняет токен
- API.clearToken() — удаляет токен
- API.request(method, url, body) — универсальная функция:
  - Добавляет Content-Type: application/json
  - Добавляет Authorization: Bearer <token> если есть
  - При статусе 401 → API.clearToken(), показать страницу auth
  - Возвращает response.json()
- API.get(url) — обёртка
- API.post(url, body) — обёртка
- API.put(url, body) — обёртка
- API.delete(url) — обёртка
```

> Для остальных фронтенд-файлов (pet.js, tasks.js, chat.js, app.js, CSS) — используй аналогичный подход: описывай структуру, ссылайся на PRD и API-контракт из ARCHITECTURE.md.

---

## Промпты для тестов

### Шаг 2.6 — test_hunger.py

```
Создай файл tests/test_hunger.py с pytest-тестами для функций голода.

Используй fixtures из conftest.py (создай conftest.py тоже).

conftest.py:
- Фикстура: тестовая БД (SQLite in-memory)
- Фикстура: тестовый пользователь + питомец
- Фикстура: mock datetime (для управления временем)

Тесты (test_hunger.py):
1. test_hunger_no_decay_just_created — только что создан, hunger = 100
2. test_hunger_after_1_hour — через 1 час: hunger ≈ 97.9 (100 - 2.083)
3. test_hunger_after_24_hours — через 24 часа: hunger ≈ 50
4. test_hunger_after_48_hours — через 48 часов: hunger = 0
5. test_hunger_after_72_hours — через 72 часа: hunger = 0 (не уходит в минус)
6. test_hunger_restore_on_task_complete — hunger был 50, задача даёт +30 → hunger = 80
7. test_hunger_restore_max_100 — hunger был 90, задача даёт +30 → hunger = 100 (не 120)
```

### Шаг 2.7 — test_exp.py

```
Создай файл tests/test_exp.py.

Тесты:
1. test_required_exp_level_0 — get_required_exp(0) == 200
2. test_required_exp_level_1 — get_required_exp(1) == 300
3. test_required_exp_level_2 — get_required_exp(2) == 450
4. test_level_up — exp = 200 при level 0 → level 1, exp = 0
5. test_no_level_up_below_threshold — exp = 199 при level 0 → уровень не меняется
6. test_max_level_3 — level = 3, exp = 9999 → уровень остаётся 3
7. test_exp_overflow_not_carried — exp = 250 при level 0 (need 200) → level 1, exp = 0 (не 50)
8. test_penalty_at_hunger_zero — hunger = 0 в течение 3 часов → exp -= 30
9. test_penalty_exp_not_below_zero — exp = 5, штраф 30 → exp = 0
10. test_penalty_no_level_decrease — level 2, exp 0, штраф → level остаётся 2
```

### Шаг 2.15 — test_tasks.py

```
Создай файл tests/test_tasks.py.

Тесты:
1. test_activate_with_mock_llm — 3 задачи, mock LLM возвращает валидный JSON → все активированы
2. test_activate_empty — нет неактивированных задач → activated_count = 0
3. test_activate_llm_failure — LLM timeout → все задачи получают fallback (medium/25/20)
4. test_activate_invalid_llm_response — LLM вернул невалидный JSON → fallback
5. test_activate_partial_invalid — LLM вернул 2 валидных + 1 с exp_reward=999 → невалидный получает fallback
6. test_complete_activated_task — задача активирована → complete → exp и hunger начислены
7. test_complete_non_activated — задача не активирована → 400 ошибка
8. test_complete_already_completed — задача уже выполнена → 400 ошибка
9. test_streak_under_3 — выполнено 2 задачи за 24ч → multiplier = 1.0
10. test_streak_over_3 — выполнено 4 задачи за 24ч → multiplier = 1.25 для 4-й

Используй mock для LLM (monkeypatch или unittest.mock.patch).
```

---

## Подключение фронтенда к бэкенду (main.py)

```
Обнови backend/app/main.py — добавь раздачу статических файлов.

После подключения всех роутеров:
1. Подключи StaticFiles из fastapi.staticfiles
2. Замонтируй папку frontend/ как статику:
   - app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
3. Это должно быть ПОСЛЕДНИМ маунтом (после всех /api/* роутеров)

Теперь при запуске uvicorn — открытие http://localhost:8000 покажет index.html.
```

---

## Деплой (задачи 4.8–4.9)

### Вариант A: без Docker (venv + systemd)

```
Создай файл deployment/systemd/tpu-pet.service:

[Unit]
Description=TPU Pet Web App
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/tpu-pet/backend
Environment="PATH=/opt/tpu-pet/venv/bin"
EnvironmentFile=/opt/tpu-pet/backend/.env
ExecStart=/opt/tpu-pet/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Вариант B: Docker

```
Создай файл deployment/docker-compose.yml:

version: "3.8"
services:
  web:
    build:
      context: ..
      dockerfile: deployment/Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ../backend/.env
    volumes:
      - ../frontend:/app/frontend:ro
      - db_data:/app/backend/data

volumes:
  db_data:

---
И файл deployment/Dockerfile:

FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY prompts/ ./prompts/
WORKDIR /app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Чек-лист перед защитой

- [ ] Приложение запускается на сервере / локально
- [ ] Регистрация → вход → JWT работает
- [ ] Питомец создаётся автоматически
- [ ] Создание задачи → активация → выполнение → EXP начисляется
- [ ] Голод убывает со временем
- [ ] Штраф при hunger=0
- [ ] Штраф за пропуск дедлайна (просроченная задача исчезает, exp/hunger вычитается)
- [ ] Стрик-множитель работает (4+ задачи за сутки)
- [ ] Level-up работает (0→1→2→3)
- [ ] Редактирование и удаление задач
- [ ] Чат-заглушка с ссылкой
- [ ] Мобильная версия выглядит нормально
- [ ] Все pytest-тесты проходят
- [ ] README.md написан
- [ ] Демо работает стабильно
