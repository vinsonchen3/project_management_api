# Project Management API

A Jira-style project management REST API built with **FastAPI, PostgreSQL, and SQLAlchemy**. The API provides authentication, project and task management, project membership, task assignment, and comments with resource-level authorization.

## Features

* **JWT authentication**

  * User registration and login
  * Access-token authentication
  * Protected API endpoints
  * Password hashing with Argon2
* **User management**

  * View and update the authenticated user's profile
  * Change password
* **Project management**

  * Create, update, and delete projects
  * Project ownership
  * Add and remove project members
  * Leave projects
  * View project members and tasks
* **Task management**

  * Create, update, and delete tasks
  * Task status tracking
  * Assign and remove task assignees
* **Comments**

  * Create, read, update, and delete task comments
  * Comment ownership enforcement
* **Resource-level authorization**

  * Project members can access project resources
  * Project owners control project membership and project updates
  * Users can only modify or delete their own comments
  * Task assignees must belong to the associated project
* **Database migrations**

  * Alembic-managed schema migrations
* **Automated testing**

  * Unit tests for services and authentication
  * End-to-end API tests
  * Isolated PostgreSQL test database
* **Containerized development**

  * Docker multi-stage build
  * Separate development and production Compose configurations
* **Continuous integration**

  * GitHub Actions automatically builds the application and runs the test suite on pushes and pull requests

## Tech Stack

| Category              | Technology                   |
| --------------------- | ---------------------------- |
| Language              | Python 3.14                  |
| API Framework         | FastAPI                      |
| Server                | Uvicorn                      |
| Database              | PostgreSQL                   |
| ORM                   | SQLAlchemy 2.0               |
| Database Driver       | asyncpg                      |
| Migrations            | Alembic                      |
| Authentication        | JWT / PyJWT                  |
| Password Hashing      | Argon2 / pwdlib              |
| Validation & Settings | Pydantic / Pydantic Settings |
| Testing               | pytest, HTTPX, AnyIO         |
| Containerization      | Docker, Docker Compose       |
| CI                    | GitHub Actions               |

## Architecture

The application follows a layered architecture that separates HTTP routing, business logic, and database access.

```text
Client
  │
  ▼
FastAPI Routers
  │
  ▼
Services
  │
  ▼
Repositories
  │
  ▼
SQLAlchemy / PostgreSQL
```

### Application layers

* **Routers** — Define HTTP endpoints, request validation, authentication dependencies, and response schemas.
* **Services** — Contain business logic and authorization rules.
* **Repositories** — Handle database queries and persistence.
* **Models** — Define the SQLAlchemy database schema and relationships.
* **Schemas** — Define API request and response models.
* **Auth** — Handles JWT authentication and password hashing.
* **Core** — Application configuration and exception handling.

This separation keeps API concerns, business rules, and database operations independent from one another.

## Authorization

Authentication is handled using JWT bearer tokens. Protected endpoints resolve the current user from the access token before executing the requested operation.

Authorization is enforced at the service layer based on the user's relationship to the requested resource.

For example:

* Project members can access project resources.
* Project owners can update or delete their projects.
* Project owners control project membership.
* Tasks can only be accessed by members of the associated project.
* Users can only update or delete comments they authored.
* Users assigned to tasks must belong to the corresponding project.

This ensures that authentication alone is not sufficient to access another user's project resources.

## Data Model

The core data model consists of four entities:

```text
User
 │
 ├── owns ────────────► Project
 │                       │
 │                       ├── has ─────► Task
 │                       │                │
 │                       │                └── has ───► Comment
 │                       │
 │                       └── has many ──► Users
 │
 └── can be assigned ──► Task
```

### Relationships

* A **User** can own multiple projects.
* A **User** can be a member of multiple projects.
* A **Project** contains multiple tasks.
* A **Task** belongs to one project.
* A **Task** can have multiple assignees.
* A **Task** can have multiple comments.
* A **Comment** belongs to a task and has an author.

Tasks support the following statuses:

* `To Do`
* `In Progress`
* `Under Review`
* `Completed`

## API

All application endpoints are currently versioned under:

```text
/api/v1
```

### Authentication

| Method | Endpoint         | Description                                  |
| ------ | ---------------- | -------------------------------------------- |
| `POST` | `/auth/register` | Register a new user                          |
| `POST` | `/auth/login`    | Login and receive an access token            |
| `POST` | `/auth/token`    | OAuth2-compatible token endpoint for Swagger |

### Users

| Method  | Endpoint                 | Description                             |
| ------- | ------------------------ | --------------------------------------- |
| `GET`   | `/users/me`              | Get the authenticated user              |
| `PATCH` | `/users/me`              | Update the authenticated user's profile |
| `PATCH` | `/users/change-password` | Change the user's password              |

### Projects

| Method   | Endpoint                                   | Description                        |
| -------- | ------------------------------------------ | ---------------------------------- |
| `POST`   | `/projects/`                               | Create a project                   |
| `GET`    | `/projects/`                               | Get projects available to the user |
| `GET`    | `/projects/{project_id}`                   | Get project details                |
| `PATCH`  | `/projects/{project_id}`                   | Update a project                   |
| `DELETE` | `/projects/{project_id}`                   | Delete a project                   |
| `GET`    | `/projects/{project_id}/members`           | Get project members                |
| `POST`   | `/projects/{project_id}/members`           | Add a project member               |
| `DELETE` | `/projects/{project_id}/members/me`        | Leave a project                    |
| `DELETE` | `/projects/{project_id}/members/{user_id}` | Remove a project member            |
| `POST`   | `/projects/{project_id}/tasks`             | Create a task                      |
| `GET`    | `/projects/{project_id}/tasks`             | Get project tasks                  |

### Tasks

| Method   | Endpoint                               | Description             |
| -------- | -------------------------------------- | ----------------------- |
| `GET`    | `/tasks/{task_id}`                     | Get task details        |
| `PATCH`  | `/tasks/{task_id}`                     | Update a task           |
| `DELETE` | `/tasks/{task_id}`                     | Delete a task           |
| `POST`   | `/tasks/{task_id}/assignees`           | Assign a user to a task |
| `DELETE` | `/tasks/{task_id}/assignees/{user_id}` | Remove a task assignee  |
| `GET`    | `/tasks/{task_id}/comments`            | Get task comments       |
| `POST`   | `/tasks/{task_id}/comments`            | Create a task comment   |

### Comments

| Method   | Endpoint                 | Description      |
| -------- | ------------------------ | ---------------- |
| `GET`    | `/comments/{comment_id}` | Get a comment    |
| `PATCH`  | `/comments/{comment_id}` | Update a comment |
| `DELETE` | `/comments/{comment_id}` | Delete a comment |

## API Documentation

Once the application is running, interactive API documentation is available through FastAPI:

* **Swagger UI:** http://localhost:8000/docs
* **ReDoc:** http://localhost:8000/redoc

Swagger UI can be used to authenticate and make requests directly against the API.

## Getting Started

### Prerequisites

* [Docker](https://www.docker.com/)
* Docker Compose

The recommended development setup runs the API and PostgreSQL databases inside Docker containers.

### 1. Clone the repository

```bash
git clone https://github.com/vinsonchen3/project_management_api.git
cd project_management_api
```

### 2. Configure environment variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_HASH_SCHEME=argon2id

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app
POSTGRES_TEST_DB=app_test

DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/app
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres_test:5432/app_test
```

For anything beyond local development, use a strong randomly generated secret key and secure database credentials.

### 3. Start the development environment

```bash
docker compose -f compose.yaml -f compose.dev.yaml up --build
```

The development configuration:

* Builds the development Docker image
* Starts the API
* Starts a PostgreSQL development database
* Starts a separate PostgreSQL test database
* Runs Alembic migrations
* Enables Uvicorn auto-reload
* Mounts the application and test directories into the container

The API will be available at:

```text
http://localhost:8000
```

### 4. Run the test suite

With the development containers running:

```bash
docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest
```

The test suite uses a dedicated PostgreSQL database so application data and test data remain isolated.

### 5. Stop the environment

```bash
docker compose -f compose.yaml -f compose.dev.yaml down
```

To also remove the database volumes:

```bash
docker compose -f compose.yaml -f compose.dev.yaml down -v
```

## Database Migrations

Database schema changes are managed with Alembic.

To apply pending migrations:

```bash
alembic upgrade head
```

The production Compose configuration automatically runs migrations before starting the API.

To create a new migration after modifying the SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe your change"
```

Review autogenerated migrations before applying them.

## Testing

Tests are divided into two categories:

```text
tests/
├── unit/
└── e2e/
```

### Unit tests

Unit tests cover individual services and authentication components, including:

* Authentication services
* User services
* Project services
* Task services
* Comment services
* JWT handling
* Password hashing

### End-to-end tests

End-to-end tests exercise the API through HTTP requests and cover:

* Authentication
* Users
* Projects
* Tasks
* Comments

The test configuration uses an isolated PostgreSQL database and asynchronous SQLAlchemy sessions.

## Continuous Integration

GitHub Actions runs the test workflow on pushes and pull requests targeting `main`.

The CI pipeline:

1. Checks out the repository.
2. Builds the Docker Compose environment.
3. Starts the API and PostgreSQL services.
4. Runs the pytest suite inside the API container.
5. Stops the containers and removes test volumes.

This provides an automated check that the application can build and that the test suite passes before changes are merged.

## Project Structure

```text
project_management_api/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── projects.py
│   │       ├── tasks.py
│   │       └── comments.py
│   │
│   ├── auth/
│   │   ├── dependencies.py
│   │   ├── hashing.py
│   │   └── jwt.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── exception_handlers.py
│   │
│   ├── db/
│   │   ├── models/
│   │   ├── database.py
│   │   └── enums.py
│   │
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── project_repository.py
│   │   ├── task_repository.py
│   │   └── comment_repository.py
│   │
│   ├── schemas/
│   ├── services/
│   ├── dependencies.py
│   └── main.py
│
├── alembic/
│   └── migrations
│
├── tests/
│   ├── unit/
│   ├── e2e/
│   └── conftest.py
│
├── .github/
│   └── workflows/
│       └── ci.yaml
│
├── compose.yaml
├── compose.dev.yaml
├── Dockerfile
├── requirements.txt
└── requirements-dev.txt
```

## Production

The production Docker image uses a separate production build stage and runs the application as a non-root user.

The production Compose configuration:

* Builds the production image
* Starts PostgreSQL
* Waits for PostgreSQL to become healthy
* Applies Alembic migrations
* Starts Uvicorn
* Restarts services automatically if they stop

```bash
docker compose up --build
```

## Future Improvements

Potential future additions include:

* Refresh-token rotation and revocation
* Pagination and filtering for projects and tasks
* Task priorities and due dates
* Task history / activity tracking
* Project roles and more granular permissions
* Rate limiting
* API monitoring and observability
* Deployment to a cloud platform

## License

This project is currently intended as a personal software engineering project and does not currently include an open-source license.
