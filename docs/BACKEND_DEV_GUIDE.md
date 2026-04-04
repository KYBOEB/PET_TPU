# BACKEND DEVELOPMENT GUIDE — Питомец ТПУ 🐶

## Роль Claude в этом чате

Ты — **ведущий backend-разработчик и наставник**. Твоя задача — провести разработчика (Данилу) через все этапы создания серверной части проекта «Питомец ТПУ», используя **Claude Code** в терминале.

**Ты НЕ пишешь код напрямую в этот чат.** Вместо этого ты:
1. Объясняешь текущий этап и его цель
2. Даёшь **готовый промпт на английском** для Claude Code
3. Описываешь **как проверить результат**
4. Указываешь **git-команды для коммита**
5. Формируешь **краткую сводку для отчёта куратору**

---

## Перед началом работы

### Шаг 0: Подготовка окружения

Скажи разработчику выполнить следующее перед первым промптом к Claude Code:

```bash
# 1. Создать и активировать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или: venv\Scripts\activate  # Windows

# 2. Инициализировать git-репозиторий
git init
git remote add origin <URL репозитория на GitHub>

# 3. Скопировать файлы документации в docs/
# (PRD.md, ARCHITECTURE.md, DEVELOPMENT_PLAN.md, CLAUDE_CODE_INSTRUCTIONS.md)
```

### Правила работы с Claude Code

1. **Один промпт = одна задача.** Не просить сделать «весь backend». Один файл или одна функция за раз.
2. **Контекст в начале сессии.** Первый промпт каждой сессии Claude Code:
   ```
   Read the project files: docs/PRD.md, docs/ARCHITECTURE.md, docs/DEVELOPMENT_PLAN.md. Understand the full project context before I give you tasks.
   ```
3. **Проверка после каждого шага.** Запустить, убедиться что работает, только потом коммит.
4. **Отказ от усложнений.** Если Claude Code предлагает паттерны или абстракции сверх плана:
   ```
   No, keep it simple. Follow the plan exactly as described in ARCHITECTURE.md. This is an MVP for beginners.
   ```
5. **Безопасность.** Никаких реальных паролей или ключей в коде. Всё через .env.

---

## ЭТАП 1: Инициализация проекта и база данных
**Задачи плана:** 1.1–1.8
**Ожидаемый результат:** сервер запускается, БД создаётся, /api/health = 200
**Время:** ~60 минут

---

### Промпт 1.1 → Claude Code

```
Create the project folder structure for "tpu-pet" exactly as described in docs/ARCHITECTURE.md section 2.

Structure:
tpu-pet/
├── backend/
│   ├── app/
│   │   ├── __init__.py (empty)
│   │   ├── routers/
│   │   │   ├── __init__.py (empty)
│   │   ├── services/
│   │   │   ├── __init__.py (empty)
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

Also create:
- Empty __init__.py in all Python packages
- .gitignore for Python project (include: __pycache__, .env, *.db, venv/, .idea/, .vscode/)
```

### Промпт 1.2 → Claude Code

```
Create file backend/requirements.txt with these exact pinned dependencies:

fastapi==0.115.0
uvicorn==0.30.0
sqlalchemy==2.0.35
pydantic[email]==2.9.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-dotenv==1.0.1
httpx==0.27.0
apscheduler==3.10.4
slowapi==0.1.9
```

### Промпт 1.3 → Claude Code

```
Create file backend/.env.example with these variables:

DATABASE_URL=sqlite:///./tpu_pet.db
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRE_DAYS=7
LLM_PROVIDER=fallback
LLM_API_URL=http://localhost:11434/api/generate
LLM_API_KEY=
LLM_MODEL=qwen2.5:7b
LLM_TIMEOUT=30

Then copy it to backend/.env (this file is in .gitignore).
```

### Промпт 1.4 → Claude Code

```
Create file backend/app/config.py.

Requirements:
- Use python-dotenv to load variables from .env file
- Create a Settings class with all variables from .env.example
- All variables must have default values matching .env.example
- JWT_EXPIRE_DAYS and LLM_TIMEOUT should be int type
- Export a singleton: settings = Settings()

Keep it simple — no Pydantic BaseSettings, just a plain class with dotenv.
```

### Промпт 1.5 → Claude Code

```
Create file backend/app/database.py.

Requirements:
- Create SQLAlchemy engine from settings.DATABASE_URL
- If SQLite: add connect_args={"check_same_thread": False}
- Create SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
- Create Base = declarative_base()
- Create generator function get_db() for FastAPI dependency injection

Use SQLAlchemy 2.0 style. Keep it minimal.
```

### Промпт 1.6 → Claude Code

```
Create file backend/app/models.py with SQLAlchemy ORM models.

Use declarative style. Models as described in docs/ARCHITECTURE.md section 4.2:

1. User:
   - id: Integer, primary key, autoincrement
   - email: String(255), unique, not null
   - password_hash: String(255), not null
   - created_at: DateTime, default=datetime.utcnow
   - relationship: pet (one-to-one), tasks (one-to-many)

2. Pet:
   - id: Integer, primary key, autoincrement
   - user_id: Integer, ForeignKey("users.id"), unique, not null
   - name: String(100), default="Студент-корги"
   - level: Integer, default=0
   - current_exp: Float, default=0
   - hunger: Float, default=100
   - last_hunger_update: DateTime, default=datetime.utcnow
   - hunger_zero_since: DateTime, nullable=True
   - created_at: DateTime, default=datetime.utcnow

3. Task:
   - id: Integer, primary key, autoincrement
   - user_id: Integer, ForeignKey("users.id"), not null
   - title: String(200), not null
   - category: String(50), not null
   - deadline: Date, not null
   - difficulty: String(10), nullable
   - exp_reward: Float, nullable
   - hunger_reward: Float, nullable
   - is_activated: Boolean, default=False
   - is_completed: Boolean, default=False
   - is_overdue: Boolean, default=False
   - created_at: DateTime, default=datetime.utcnow
   - completed_at: DateTime, nullable

Table names: "users", "pets", "tasks".
```

### Промпт 1.7 → Claude Code

```
Create file backend/app/main.py — minimal FastAPI application.

Requirements:
- Create FastAPI app with title="TPU Pet API"
- On startup (use lifespan context manager): create all tables via Base.metadata.create_all(bind=engine)
- Add CORS middleware with allow_origins=["*"] for development
- Add one endpoint: GET /api/health that returns {"status": "ok"}
- Do NOT include routers yet (they don't exist)
- The app should be runnable with: cd backend && uvicorn app.main:app --reload
```

### Проверка этапа 1

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
# Открыть http://localhost:8000/api/health → должно вернуть {"status": "ok"}
# Проверить: файл tpu_pet.db создался
```

### Git-коммит этапа 1

```bash
git add .
git commit -m "feat: project structure, database models, minimal FastAPI server

- Created project folder structure (backend, frontend, tests, docs)
- Added SQLAlchemy models: User, Pet, Task
- Added config.py with .env support
- Added database.py with SQLite connection
- Added minimal main.py with /api/health endpoint
- Server starts, database file is created"

git push origin main
```

### Сводка для куратора — Этап 1

> **Этап 1: Инициализация проекта и база данных.**
> Создана структура проекта, реализованы ORM-модели данных (User, Pet, Task) с помощью SQLAlchemy, настроено подключение к SQLite, создан минимальный сервер FastAPI с эндпоинтом проверки работоспособности. Сервер запускается, база данных создаётся автоматически.

---

## ЭТАП 2: Аутентификация (JWT)
**Задачи плана:** 1.9–1.13
**Ожидаемый результат:** регистрация → вход → JWT-токен → питомец создан
**Время:** ~60 минут

---

### Промпт 2.1 → Claude Code

```
Create file backend/app/schemas.py with Pydantic v2 models.

Schemas needed:
1. UserCreate: email (EmailStr from pydantic), password (str, min_length=6)
2. UserLogin: email (str), password (str)
3. TokenResponse: token (str), user_id (int)
4. PetResponse: id, name, level, current_exp, required_exp (float), hunger (float), mood (str), image (str)
5. PetNameUpdate: name (str, min_length=1, max_length=100)
6. TaskCreate: title (str, max_length=200), category (str, max_length=50), deadline (str — format DD.MM.YYYY, add a field_validator to verify format)
7. TaskUpdate: title (Optional[str]), category (Optional[str]), deadline (Optional[str])
8. TaskResponse: id, title, category, deadline (str), difficulty (Optional[str]), exp_reward (Optional[float]), hunger_reward (Optional[float]), is_activated (bool), is_completed (bool), is_overdue (bool)
9. TaskActivateResponse: activated_count (int), tasks (list[TaskResponse])
10. TaskCompleteResponse: exp_gained (float), hunger_gained (float), streak_active (bool), streak_multiplier (float), level_up (bool), pet (PetResponse)

Use Pydantic v2 style (model_config, field_validator).
```

### Промпт 2.2 → Claude Code

```
Create file backend/app/auth.py.

Functions:
1. hash_password(password: str) -> str — using passlib CryptContext with bcrypt
2. verify_password(password: str, hash: str) -> bool
3. create_access_token(user_id: int) -> str — JWT with payload {"sub": str(user_id), "exp": datetime.utcnow() + timedelta(days=settings.JWT_EXPIRE_DAYS)}, algorithm HS256
4. decode_access_token(token: str) -> int — returns user_id or raises HTTPException(401)
5. get_current_user — FastAPI Depends function:
   - Extracts token from Authorization: Bearer <token> header
   - Decodes token with decode_access_token
   - Returns user_id (int)
   - If invalid → HTTPException 401 with detail "Неверный или истёкший токен"

Use settings.JWT_SECRET from config.py. Use python-jose for JWT.
```

### Промпт 2.3 → Claude Code

```
Create file backend/app/routers/auth_router.py.

Two endpoints:

1. POST /api/auth/register
   - Accepts: UserCreate (email + password)
   - Check: email not taken (else 400, detail="Email уже зарегистрирован")
   - Create user with hashed password
   - Automatically create pet (name="Студент-корги", level=0, hunger=100, current_exp=0)
   - Return: TokenResponse (token + user_id), status 201

2. POST /api/auth/login
   - Accepts: UserLogin (email + password)
   - Check: user exists and password is correct (else 401, detail="Неверный email или пароль")
   - Return: TokenResponse (token + user_id), status 200

Use APIRouter with prefix="/api/auth" and tags=["auth"].
Then update main.py to include this router: app.include_router(auth_router)
```

### Проверка этапа 2

```bash
# Перезапустить сервер (удалить старую БД: rm tpu_pet.db)
uvicorn app.main:app --reload

# Тест регистрации:
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
# Ожидается: 201 {"token": "eyJ...", "user_id": 1}

# Тест входа:
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
# Ожидается: 200 {"token": "eyJ...", "user_id": 1}

# Тест дубликата email:
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
# Ожидается: 400 {"detail": "Email уже зарегистрирован"}
```

### Git-коммит этапа 2

```bash
git add .
git commit -m "feat: authentication system (register, login, JWT)

- Added Pydantic schemas for all API contracts
- Implemented bcrypt password hashing
- Implemented JWT token creation and verification
- POST /api/auth/register creates user + pet, returns JWT
- POST /api/auth/login verifies credentials, returns JWT
- get_current_user dependency extracts user_id from Bearer token"

git push origin main
```

### Сводка для куратора — Этап 2

> **Этап 2: Система аутентификации.**
> Реализована регистрация и вход по email/паролю с JWT-токенами. Пароли хранятся в хэшированном виде (bcrypt). При регистрации автоматически создаётся питомец. Созданы Pydantic-схемы для всех API-контрактов проекта.

---

## ЭТАП 3: CRUD задач и эндпоинты питомца
**Задачи плана:** 1.14–1.21
**Ожидаемый результат:** все CRUD-эндпоинты работают, данные сохраняются
**Время:** ~60 минут

---

### Промпт 3.1 → Claude Code

```
Create file backend/app/routers/pet_router.py.

Two endpoints (both require JWT — use Depends(get_current_user)):

1. GET /api/pet
   - Find the pet belonging to the current user
   - For now, NO hunger recalculation (that comes later)
   - Return PetResponse with:
     - required_exp = 200 * (1.5 ** pet.level)
     - mood = "happy" if hunger > 80, "neutral" if 21-80, "sad" if 0-20
     - image = f"pet_level{pet.level}_{mood}.png"

2. PUT /api/pet/name
   - Accepts: PetNameUpdate
   - Updates the pet name
   - Returns: {"name": new_name}

Use APIRouter with prefix="/api/pet" and tags=["pet"].
Register in main.py.
```

### Промпт 3.2 → Claude Code

```
Create file backend/app/routers/task_router.py.

Four endpoints (all require JWT):

1. GET /api/tasks
   - Return all tasks for the current user where is_completed=False AND is_overdue=False
   - Sort by category (alphabetical), then by deadline within category
   - Format deadline as DD.MM.YYYY in response
   - Return: {"tasks": [TaskResponse, ...]}

2. POST /api/tasks
   - Accepts: TaskCreate
   - Parse deadline from DD.MM.YYYY string to date object
   - Create task with is_activated=False, is_completed=False, is_overdue=False
   - Return: TaskResponse, status 201

3. PUT /api/tasks/{task_id}
   - Accepts: TaskUpdate (partial update — only provided fields)
   - Verify task belongs to current user (else 404)
   - If task was activated → reset: difficulty=None, exp_reward=None, hunger_reward=None, is_activated=False
   - Return: TaskResponse

4. DELETE /api/tasks/{task_id}
   - Verify task belongs to current user (else 404)
   - Delete the task
   - Return: {"detail": "Задача удалена"}

Use APIRouter with prefix="/api/tasks" and tags=["tasks"].
Register in main.py.
```

### Проверка этапа 3

```bash
# Перезапустить сервер (rm tpu_pet.db)
# Зарегистрироваться, сохранить токен:
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Получить питомца:
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/pet

# Создать задачу:
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Сделать лабу","category":"Физика","deadline":"15.04.2026"}'

# Список задач:
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks
```

### Git-коммит этапа 3

```bash
git add .
git commit -m "feat: pet endpoints and task CRUD

- GET /api/pet returns pet data with mood and image
- PUT /api/pet/name updates pet name
- POST /api/tasks creates a new task
- GET /api/tasks returns sorted task list (by category, deadline)
- PUT /api/tasks/{id} edits task, resets rewards if activated
- DELETE /api/tasks/{id} removes task
- All endpoints require JWT authentication"

git push origin main
```

### Сводка для куратора — Этап 3

> **Этап 3: Эндпоинты питомца и CRUD задач.**
> Реализовано получение данных питомца (уровень, опыт, голод, настроение) и изменение имени. Реализован полный набор операций с задачами: создание, просмотр (с сортировкой по категориям), редактирование и удаление. Все эндпоинты защищены JWT-аутентификацией.

---

## ЭТАП 4: Механика голода и штрафов
**Задачи плана:** 2.1–2.7
**Ожидаемый результат:** голод убывает со временем, штраф при hunger=0, тесты проходят
**Время:** ~60 минут

---

### Промпт 4.1 → Claude Code

```
Create file backend/app/services/pet_service.py.

Implement these functions exactly as described in docs/PRD.md sections 3.2-3.4:

1. recompute_hunger(pet, db) -> None
   - Calculate elapsed hours since pet.last_hunger_update
   - hunger = max(0, pet.hunger - elapsed_hours * (100 / 48))
   - Update pet.last_hunger_update to now
   - If hunger reached 0 and hunger_zero_since is None → set hunger_zero_since = now
   - If hunger > 0 → set hunger_zero_since = None
   - Commit to DB

2. apply_exp_penalty(pet, db) -> None
   - If pet.hunger_zero_since is not None:
     - penalty_hours = (now - hunger_zero_since).total_seconds() / 3600
     - penalty = floor(penalty_hours) * 10
     - pet.current_exp = max(0, pet.current_exp - penalty)
   - Level is NEVER decreased
   - Commit to DB

3. get_mood(hunger: float) -> str
   - 0-20 → "sad", 21-80 → "neutral", 81-100 → "happy"

4. get_required_exp(level: int) -> float
   - return 200 * (1.5 ** level)

5. get_pet_image(level: int, mood: str) -> str
   - return f"pet_level{level}_{mood}.png"

Then UPDATE backend/app/routers/pet_router.py:
In GET /api/pet, BEFORE building the response, call:
  recompute_hunger(pet, db)
  apply_exp_penalty(pet, db)
```

### Промпт 4.2 → Claude Code

```
Create test files for hunger and exp mechanics.

First, create tests/conftest.py:
- Fixture: test database (SQLite in-memory, "sqlite:///:memory:")
- Fixture: test client (FastAPI TestClient with dependency override for get_db)
- Fixture: create a test user + pet in DB
- Fixture: helper to create tasks

Then create tests/test_hunger.py:
1. test_hunger_no_decay_just_created — freshly created pet, hunger = 100
2. test_hunger_after_1_hour — after 1 hour: hunger ≈ 97.9 (100 - 100/48)
3. test_hunger_after_24_hours — after 24 hours: hunger ≈ 50
4. test_hunger_after_48_hours — after 48 hours: hunger = 0
5. test_hunger_after_72_hours — after 72 hours: hunger = 0 (not negative)
6. test_hunger_restore_max_100 — hunger was 90, task gives +30 → hunger = 100

Then create tests/test_exp.py:
1. test_required_exp_level_0 — get_required_exp(0) == 200
2. test_required_exp_level_1 — get_required_exp(1) == 300
3. test_required_exp_level_2 — get_required_exp(2) == 450
4. test_level_up — exp reaches 200 at level 0 → level becomes 1, exp = 0
5. test_no_level_up_below_threshold — exp = 199 at level 0 → level stays 0
6. test_max_level_3 — level = 3, exp = 9999 → level stays 3
7. test_exp_overflow_not_carried — exp = 250 at level 0 (need 200) → level 1, exp = 0 (NOT 50)
8. test_penalty_at_hunger_zero — hunger = 0 for 3 hours → exp -= 30
9. test_penalty_exp_not_below_zero — exp = 5, penalty 30 → exp = 0
10. test_penalty_no_level_decrease — level 2, exp 0, penalty → level stays 2

Use monkeypatch or freezegun to control datetime.
```

### Проверка этапа 4

```bash
cd backend
pip install pytest httpx  # если не установлены
python -m pytest tests/test_hunger.py tests/test_exp.py -v
# Все тесты должны пройти
```

### Git-коммит этапа 4

```bash
git add .
git commit -m "feat: hunger decay, exp penalty, and unit tests

- Implemented recompute_hunger: linear decay over 48 hours
- Implemented apply_exp_penalty: -10 exp/hour at zero hunger
- GET /api/pet now recalculates hunger and penalties on each request
- Added helper functions: get_mood, get_required_exp, get_pet_image
- Added test fixtures (conftest.py)
- Added 7 hunger tests and 10 exp tests — all passing"

git push origin main
```

### Сводка для куратора — Этап 4

> **Этап 4: Механика голода и штрафов.**
> Реализована система убывания голода (линейно за 48 часов) и штраф за нулевой голод (−10 EXP/час). Данные пересчитываются при каждом обращении к API. Написаны 17 unit-тестов для проверки расчётов голода, опыта и пограничных случаев.

---

## ЭТАП 5: Интеграция с LLM
**Задачи плана:** 2.8–2.15
**Ожидаемый результат:** задачи активируются через LLM или fallback, тесты проходят
**Время:** ~90 минут

---

### Промпт 5.1 → Claude Code

```
Create file prompts/bulk_evaluate.txt with the LLM prompt for task evaluation.

The prompt should be in English. Content:

---
You are a task difficulty evaluator for a student productivity app.

Given a list of student task titles, evaluate each task and assign:
- difficulty: "low", "medium", or "high"
- exp_reward: integer within the range for that difficulty
- hunger_reward: integer within the range for that difficulty

Difficulty ranges:
- low: simple daily tasks (e.g., "drink water", "check email"). exp: 10-20, hunger: 5-15
- medium: regular academic tasks (e.g., "complete English test", "read chapter 5"). exp: 25-40, hunger: 20-35
- high: complex/long tasks (e.g., "prepare for calculus exam", "write term paper"). exp: 60-80, hunger: 50-70

Respond ONLY with a valid JSON array. No extra text, no markdown, no code fences.

Example input: ["Не забыть попить воды", "Выполнить тест по английскому языку"]

Example output:
[{"title": "Не забыть попить воды", "difficulty": "low", "exp_reward": 12, "hunger_reward": 8}, {"title": "Выполнить тест по английскому языку", "difficulty": "medium", "exp_reward": 30, "hunger_reward": 25}]

Tasks to evaluate:
{tasks_json}
---

The {tasks_json} placeholder will be replaced at runtime with a JSON array of task titles.
```

### Промпт 5.2 → Claude Code

```
Create file backend/app/services/llm_service.py.

Implement an async function:

async def evaluate_tasks(titles: list[str]) -> list[dict]:
    """Returns: [{"title": str, "difficulty": str, "exp_reward": int, "hunger_reward": int}]"""

Logic:
1. Read settings.LLM_PROVIDER
2. If "fallback" → return fallback values for all tasks immediately
3. If "local" → HTTP POST to settings.LLM_API_URL (Ollama format):
   body: {"model": settings.LLM_MODEL, "prompt": <prompt with titles>, "stream": false}
   timeout: settings.LLM_TIMEOUT seconds
4. If "cloud" → HTTP POST to settings.LLM_API_URL (OpenAI-compatible format):
   headers: {"Authorization": f"Bearer {settings.LLM_API_KEY}"}
   body: {"model": settings.LLM_MODEL, "messages": [{"role": "user", "content": <prompt>}]}
5. Parse response as JSON
6. Validate each item:
   - difficulty in ["low", "medium", "high"]
   - exp_reward within range for that difficulty
   - hunger_reward within range for that difficulty
7. Invalid items get fallback values
8. On ANY error (timeout, parse error, network) → log error, return fallback for ALL tasks

Validation ranges:
RANGES = {
    "low":    {"exp": (10, 20),  "hunger": (5, 15)},
    "medium": {"exp": (25, 40),  "hunger": (20, 35)},
    "high":   {"exp": (60, 80),  "hunger": (50, 70)},
}
FALLBACK = {"difficulty": "medium", "exp_reward": 25, "hunger_reward": 20}

Use httpx for async HTTP requests. Load prompt template from prompts/bulk_evaluate.txt.
```

### Промпт 5.3 → Claude Code

```
Add the activate endpoint to backend/app/routers/task_router.py:

POST /api/tasks/activate (requires JWT)

Logic:
1. Find all tasks for the user where is_activated=False and is_completed=False
2. If none found → return {"activated_count": 0, "message": "Нет новых задач для активации"}
3. Collect titles list
4. Call await llm_service.evaluate_tasks(titles)
5. For each task, write: difficulty, exp_reward, hunger_reward, is_activated=True
6. Commit to DB
7. Return TaskActivateResponse with activated_count and updated tasks list
```

### Промпт 5.4 → Claude Code

```
Create file tests/test_tasks.py with tests for task activation and completion.

Tests:
1. test_activate_with_mock_llm — 3 tasks, mock LLM returns valid JSON → all activated with correct values
2. test_activate_empty — no unactivated tasks → activated_count = 0
3. test_activate_llm_failure — LLM timeout → all tasks get fallback (medium/25/20)
4. test_activate_invalid_llm_response — LLM returns invalid JSON → fallback for all
5. test_activate_partial_invalid — LLM returns 2 valid + 1 with exp_reward=999 → invalid one gets fallback

Use monkeypatch or unittest.mock.patch to mock the LLM service. Test with fallback provider for simplicity.
```

### Проверка этапа 5

```bash
# Убедиться что .env содержит LLM_PROVIDER=fallback
python -m pytest tests/test_tasks.py -v

# Ручная проверка:
# 1. Зарегистрироваться, получить токен
# 2. Создать 2 задачи
# 3. POST /api/tasks/activate → задачи должны получить difficulty и rewards
```

### Git-коммит этапа 5

```bash
git add .
git commit -m "feat: LLM integration for task evaluation with fallback

- Created LLM prompt template (prompts/bulk_evaluate.txt)
- Implemented llm_service.py with 3 modes: local, cloud, fallback
- Added response validation with per-task fallback
- POST /api/tasks/activate evaluates unactivated tasks via LLM
- Added 5 tests for activation logic with mocked LLM
- Fallback mode works without any external dependencies"

git push origin main
```

### Сводка для куратора — Этап 5

> **Этап 5: Интеграция с нейросетью.**
> Реализован сервис оценки сложности задач через нейросеть Qwen с тремя режимами работы: локальный сервер, облачное API, fallback (без нейросети). Включена валидация ответов нейросети с автоматическим переключением на стандартные значения при ошибках. Написаны тесты с мок-объектами.

---

## ЭТАП 6: Выполнение задач, стрик, level-up, штраф за дедлайн
**Задачи плана:** 2.16–2.24
**Ожидаемый результат:** полный backend-цикл работает, все тесты проходят
**Время:** ~90 минут

---

### Промпт 6.1 → Claude Code

```
Create file backend/app/services/task_service.py.

Implement these functions:

1. check_streak(user_id: int, db: Session) -> tuple[bool, float]:
   - Count tasks completed by user in the last 24 hours (completed_at >= now - 24h)
   - If count > 3 → return (True, 1.25)
   - Else → return (False, 1.0)

2. complete_task(task_id: int, user_id: int, db: Session) -> dict:
   - Find task, verify: exists, belongs to user, is_activated=True, is_completed=False
   - If any check fails → raise HTTPException(400) with appropriate Russian message
   - Check streak → get multiplier
   - Calculate: final_exp = floor(task.exp_reward * multiplier)
   - Calculate: final_hunger = floor(task.hunger_reward * multiplier)
   - Update pet:
     - pet.hunger = min(100, pet.hunger + final_hunger)
     - pet.current_exp += final_exp
     - If hunger > 0 → pet.hunger_zero_since = None
   - Check level_up:
     - required = get_required_exp(pet.level)
     - If pet.current_exp >= required AND pet.level < 3:
       - pet.level += 1
       - pet.current_exp = 0 (overflow is NOT carried over)
       - level_up = True
   - Mark task: is_completed=True, completed_at=now
   - Commit and return dict for TaskCompleteResponse

3. check_overdue_tasks(user_id: int, db: Session) -> int:
   - Find all tasks where: user_id matches, is_activated=True, is_completed=False, is_overdue=False, deadline < date.today()
   - For each such task:
     - pet.current_exp = max(0, pet.current_exp - task.exp_reward)
     - pet.hunger = max(0, pet.hunger - task.hunger_reward)
     - If pet.hunger == 0 and pet.hunger_zero_since is None → set hunger_zero_since = now
     - task.is_overdue = True
   - Level is NEVER decreased
   - Commit and return count of penalized tasks
```

### Промпт 6.2 → Claude Code

```
Add the complete endpoint to backend/app/routers/task_router.py:

POST /api/tasks/{task_id}/complete (requires JWT)

Logic:
1. First call recompute_hunger and apply_exp_penalty for the user's pet
2. Then call task_service.complete_task(task_id, user_id, db)
3. Build and return TaskCompleteResponse with updated pet data

Also UPDATE these existing endpoints:

In GET /api/pet (pet_router.py):
- Before returning data, also call check_overdue_tasks(user_id, db)

In GET /api/tasks (task_router.py):
- Before returning the list, call check_overdue_tasks(user_id, db)
- Only return tasks where is_completed=False AND is_overdue=False
```

### Промпт 6.3 → Claude Code

```
Create file tests/test_overdue.py with tests for deadline penalty.

Tests:
1. test_overdue_applies_penalty — task activated, deadline=yesterday, exp_reward=30, hunger_reward=25, pet exp=100, hunger=80. After check → exp=70, hunger=55, task.is_overdue=True
2. test_overdue_not_activated — task not activated, deadline=yesterday → NO penalty
3. test_overdue_already_completed — task completed, deadline=yesterday → NO penalty
4. test_overdue_already_marked — task is_overdue=True already → NOT penalized again
5. test_overdue_exp_not_below_zero — pet exp=10, task exp_reward=50 → exp=0
6. test_overdue_hunger_not_below_zero — pet hunger=5, task hunger_reward=30 → hunger=0
7. test_overdue_multiple_tasks — 3 overdue tasks (20+30+40 exp), pet exp=100 → exp=10
8. test_overdue_deadline_today_not_penalized — deadline=today → NO penalty (strictly < today)
9. test_overdue_level_not_decreased — pet level=2, exp=0, task exp_reward=50 → level=2, exp=0

Also add to tests/test_tasks.py:
10. test_complete_activated_task — complete → exp and hunger are credited
11. test_complete_non_activated — 400 error
12. test_complete_already_completed — 400 error
13. test_streak_under_3 — 2 tasks completed today → multiplier 1.0
14. test_streak_over_3 — 4 tasks completed today → multiplier 1.25 for the 4th

Use monkeypatch or freezegun for date control.
```

### Проверка этапа 6

```bash
python -m pytest tests/ -v
# ВСЕ тесты должны пройти

# Ручная проверка полного цикла:
# 1. Зарегистрироваться
# 2. Создать 3 задачи
# 3. POST /api/tasks/activate → задачи получают награды
# 4. POST /api/tasks/1/complete → EXP и hunger увеличиваются
# 5. GET /api/pet → отображает обновлённые данные
```

### Git-коммит этапа 6

```bash
git add .
git commit -m "feat: task completion, streak bonus, level-up, overdue penalties

- Implemented complete_task with exp/hunger rewards
- Implemented streak bonus: x1.25 after 3+ tasks in 24 hours
- Implemented level-up: exp reset, max level 3, no overflow carry
- Implemented check_overdue_tasks: penalty = promised reward, one-time
- Overdue tasks hidden from task list
- Added 14 new tests (overdue + completion + streak) — all passing
- Full backend cycle works: create → activate → complete → level up"

git push origin main
```

### Сводка для куратора — Этап 6

> **Этап 6: Выполнение задач, бонус за серию, повышение уровня, штраф за просрочку.**
> Реализована полная бизнес-логика: выполнение задач с начислением наград, бонусный множитель ×1.25 при серии из 3+ выполнений за сутки, автоматическое повышение уровня питомца (0→3), штраф за пропуск дедлайна (вычет обещанной награды). Написаны 14 дополнительных тестов. Весь серверный цикл от создания задачи до повышения уровня полностью функционален.

---

## ИТОГО: состояние после всех этапов

### Реализованные файлы

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              ✅ FastAPI app, CORS, роутеры, статика
│   ├── config.py            ✅ Настройки из .env
│   ├── database.py          ✅ SQLAlchemy engine, сессии
│   ├── models.py            ✅ User, Pet, Task
│   ├── schemas.py           ✅ Все Pydantic-схемы
│   ├── auth.py              ✅ bcrypt, JWT, get_current_user
│   ├── routers/
│   │   ├── auth_router.py   ✅ register, login
│   │   ├── pet_router.py    ✅ GET pet, PUT name
│   │   ├── task_router.py   ✅ CRUD + activate + complete
│   ├── services/
│   │   ├── pet_service.py   ✅ hunger, penalty, mood, level
│   │   ├── task_service.py  ✅ complete, streak, overdue
│   │   ├── llm_service.py   ✅ LLM adapter (local/cloud/fallback)
├── requirements.txt         ✅
├── .env.example             ✅
prompts/
├── bulk_evaluate.txt        ✅ LLM prompt
tests/
├── conftest.py              ✅ Fixtures
├── test_hunger.py           ✅ 7 tests
├── test_exp.py              ✅ 10 tests
├── test_tasks.py            ✅ 10 tests
├── test_overdue.py          ✅ 9 tests
```

### Git-история (6 коммитов)

```
feat: project structure, database models, minimal FastAPI server
feat: authentication system (register, login, JWT)
feat: pet endpoints and task CRUD
feat: hunger decay, exp penalty, and unit tests
feat: LLM integration for task evaluation with fallback
feat: task completion, streak bonus, level-up, overdue penalties
```

### Полная сводка для куратора

> **Backend-разработка (недели 1–2): завершена.**
>
> Реализован полнофункциональный серверный API из 11 эндпоинтов:
> - Аутентификация: регистрация, вход, JWT-токены
> - Питомец: получение данных, изменение имени, автоматический пересчёт голода и штрафов
> - Задачи: создание, просмотр, редактирование, удаление, активация через нейросеть, выполнение с начислением наград
> - Бизнес-логика: убывание голода (48ч), штраф за нулевой голод (−10 EXP/ч), бонус за серию (×1.25), повышение уровня (0→3), штраф за пропуск дедлайна
> - Написано 36 unit-тестов, все проходят
> - Код структурирован по принципу разделения ответственности (роутеры, сервисы, модели)

---

## Навигация для Claude в новом чате

При открытии нового чата, скопируй это сообщение:

```
Прочитай файл BACKEND_DEV_GUIDE.md — это твоё основное задание. Также ознакомься с PRD.md, ARCHITECTURE.md и CLAUDE_CODE_INSTRUCTIONS.md для полного контекста.

Твоя задача — провести меня через все 6 этапов backend-разработки. На каждом этапе:
1. Объясни что мы делаем и зачем
2. Дай готовый промпт для Claude Code (на английском)
3. Скажи как проверить результат
4. Дай git-команды для коммита
5. Сформируй краткую сводку для отчёта куратору

Начнём с Этапа 1. Я уже создал виртуальное окружение и инициализировал git-репозиторий.
```
