# Custom Exception Handling Pattern

This document outlines the standard pattern for handling application-specific errors in this FastAPI project. The goal
is to create a robust, scalable, and maintainable error-handling system that keeps endpoint logic clean and follows
the "Don't Repeat Yourself" (DRY) principle.

## Core Concept

The pattern relies on three main components:

1. **A Base Exception (`AppError`)**: A central `AppError` class located in `src/exceptions.py` serves as the parent for
   all custom application errors.

2. **A Global Exception Handler**: A single function in `main.py` decorated with `@app.exception_handler(AppError)` acts
   as a global "safety net." It catches any exception that inherits from `AppError`, no matter where it's raised from.
3. **Module-Specific Exceptions**: Each module (e.g., `users`, `bookings`) has its own `exceptions.py` file. These files
   contain specific exception classes (like `UserNotFoundError`) that inherit from `AppError` and define their own HTTP
   status code and message format.

This setup allows service-layer code to raise specific, meaningful exceptions without worrying about HTTP details. The
global handler automatically converts these exceptions into clean, consistent JSON error responses.

---

## Full Example Walkthrough

Here is a complete, step-by-step example of how to implement and use this pattern.

### 1. The Base Exception

This is the foundation. All other custom errors will inherit from this class.

**File: `src/exceptions.py`**

```python
class AppError(Exception):
    """Base class for all application errors."""
    status_code: int = 500

    def __init__(self, message: str = "An unexpected application error occurred."):
        super().__init__(message)

```

### 2. The Global Exception Handler

This handler is defined once in `main.py`. It catches any `AppError` and formats the HTTP response.

**File: `main.py`**

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.exceptions import AppError

app = FastAPI()


@app.exception_handler(AppError)
async def app_exception_handler(request: Request, exc: AppError):
    """Global handler to catch all AppError exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )

# ... your endpoints will go here

```

### 3. A Module-Specific Exception

Let's create a specific error for when a user cannot be found. Note how it inherits from `AppError`, sets a
`status_code`, and has a custom `__init__` to format its message.

**File: `src/users/exceptions.py`**

```python
from src.exceptions import AppError


class UserNotFoundError(AppError):
    """Custom exception raised when a user is not found."""
    status_code = 404  # HTTP 404 Not Found

    def __init__(self, user_id: int | str):
        message = f"User with ID '{user_id}' was not found."
        super().__init__(message)

```

### 4. The Service Layer

The service layer contains the business logic. It raises the specific exception when a business rule is violated. It
does **not** deal with `HTTPException`.

**File: `src/users/services.py`**

```python
from .exceptions import UserNotFoundError

# This is a dummy database to simulate data access.
DUMMY_USERS_DB = {
    1: {"id": 1, "name": "Alice"},
    2: {"id": 2, "name": "Bob"},
}


async def find_user_by_id(user_id: int) -> dict:
    """
    Finds a user in the database or raises an error if not found.
    """
    user = DUMMY_USERS_DB.get(user_id)
    if not user:
        # Raise the specific, custom exception. FastAPI will catch this.
        raise UserNotFoundError(user_id=user_id)
    return user

```

### 5. The Endpoint (Router Layer)

Finally, the endpoint code is clean and simple. It calls the service and returns the result, without any `try/except`
blocks for application errors.

**File: `main.py` (updated)**

```python
# ... (imports and handler from above)
from src.users.services import find_user_by_id


@app.get("/users/{user_id}", tags=["Users"])
async def get_user(user_id: int):
    """
    Retrieves a user by their ID.
    This endpoint remains clean thanks to the global exception handler.
    """
    user = await find_user_by_id(user_id=user_id)
    return user

```

### How it Works in Practice

* **Request to `GET /users/1`**: The service finds the user and returns the data with a `200 OK`.
* **Request to `GET /users/99`**: The service raises `UserNotFoundError`. The global handler catches it and
  automatically returns a `404 Not Found` with the JSON body: `{"detail": "User with ID '99' was not found."}`.