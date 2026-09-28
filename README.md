# <img src="https://api.iconify.design/fa6-solid/wallet.svg?color=%232563EB" width="26" height="26" align="center" /> Personal Expense Tracker

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![JWT](https://img.shields.io/badge/Auth-JWT%20Bearer-black?logo=jsonwebtokens&logoColor=white)](https://jwt.io)

A full-stack personal finance and expense tracking application built for **Nolyth Sprint 01: Backend Foundations**. This project demonstrates practical Python engineering, RESTful API architecture with **FastAPI**, relational database persistence with **SQLite** and **SQLAlchemy**, request/response data validation with **Pydantic**, secure authentication via **JWT**, and an interactive frontend built with **Streamlit**.

---

## <img src="https://api.iconify.design/fa6-solid/circle-info.svg?color=%232563EB" width="20" height="20" align="center" /> Project Overview

Managing personal expenses is a crucial daily task. This application solves the problem by providing a clean, authenticated environment where users can:
- **Record & Categorize Expenses**: Log daily expenditures with titles, categories, dates, amounts, and custom notes.
- **Filter & Search**: Quickly find transactions using category filters, date ranges, or keyword searches.
- **Analyze Spending**: View KPI metrics (Total Spent, Transaction Counts, Average Cost, Top Category) and visual spending distributions.
- **Manage Entries (CRUD)**: Update existing expenses or delete entries with immediate database persistence.
- **Multi-User Security**: Keep user data completely isolated using JWT token-based authentication.

---

## <img src="https://api.iconify.design/fa6-solid/layer-group.svg?color=%232563EB" width="20" height="20" align="center" /> Architecture & Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance RESTful API endpoints, dependency injection, and automatic OpenAPI docs. |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) | Strict request payload validation, type hints, and response serialization. |
| **Database & ORM** | [SQLite](https://www.sqlite.org/) + [SQLAlchemy](https://www.sqlalchemy.org/) | Relational database persistence, connection pooling, and ORM model mapping. |
| **Authentication** | [PyJWT](https://pyjwt.readthedocs.io/) + PBKDF2 Hashing | Secure password salting/hashing and Bearer token session authentication. |
| **Frontend UI** | [Streamlit](https://streamlit.io/) + [Pandas](https://pandas.pydata.org/) | User-friendly dashboard with forms, data tables, metrics, and charts. |

---

## <img src="https://api.iconify.design/fa6-solid/folder-tree.svg?color=%232563EB" width="20" height="20" align="center" /> Project Structure

```text
Sprint_1_Nolyth/
│
├── backend/                        # Backend Application Package
│   ├── __init__.py
│   ├── database.py                 # SQLite engine, SessionLocal, and DB dependency
│   ├── models.py                   # SQLAlchemy ORM models (User, Expense)
│   ├── schemas.py                  # Pydantic schemas for request/response validation
│   ├── auth.py                     # Password hashing, JWT token creation & verification
│   ├── crud.py                     # Database query helper functions (CRUD logic)
│   └── routers/
│       ├── __init__.py
│       ├── auth_router.py          # /auth/register, /auth/login, /auth/me
│       └── expense_router.py       # /expenses CRUD, search, filter, and summary
│
├── frontend/                       # Frontend Application Package
│   ├── __init__.py
│   └── app.py                      # Streamlit UI with multi-view navigation & charts
│
├── test_backend.py                 # Automated end-to-end integration tests
├── main.py                         # FastAPI application entry point
├── requirements.txt                # Python project dependencies
├── expenses.db                     # SQLite database file (auto-generated)
└── README.md                       # Complete project documentation and guide
```

---

## <img src="https://api.iconify.design/fa6-solid/gears.svg?color=%232563EB" width="20" height="20" align="center" /> Setup and Installation

### 1. Prerequisites
- Python 3.10+ installed on your computer.
- Git installed.

### 2. Clone Repository & Setup Virtual Environment

```bash
# Clone the repository
git clone https://github.com/ARKhalid123/Sprint_1_Nolyth.git
cd Sprint_1_Nolyth

# Create a virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.\.venv\Scripts\activate.bat
# On macOS / Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## <img src="https://api.iconify.design/fa6-solid/play.svg?color=%232563EB" width="20" height="20" align="center" /> Running the Application

This application consists of two services: the **FastAPI Backend** and the **Streamlit Frontend**.

### Step 1: Start the FastAPI Backend

Open your **first terminal** in the project directory:

**Option A (Activate venv first):**
- In Command Prompt (`cmd`):
  ```cmd
  .venv\Scripts\activate.bat
  uvicorn main:app --reload
  ```
- In PowerShell:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  uvicorn main:app --reload
  ```

**Option B (Run directly without activating):**
```cmd
.\.venv\Scripts\python.exe main.py
```

- API Base URL: **`http://127.0.0.1:8000`**
- Interactive Swagger Docs: **`http://127.0.0.1:8000/docs`**

---

### Step 2: Start the Streamlit Frontend

Open a **second terminal window** in the same folder:

**Option A (Activate venv first):**
- In Command Prompt (`cmd`):
  ```cmd
  .venv\Scripts\activate.bat
  streamlit run frontend/app.py
  ```
- In PowerShell:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  streamlit run frontend/app.py
  ```

**Option B (Run directly using the virtual environment):**
```cmd
.\.venv\Scripts\python.exe -m streamlit run frontend/app.py
```
*(or `.\.venv\Scripts\streamlit.exe run frontend/app.py`)*

- Streamlit will open your browser at: **`http://localhost:8501`**

---

## <img src="https://api.iconify.design/fa6-solid/user-check.svg?color=%232563EB" width="20" height="20" align="center" /> User Flow & Features

1. **Register**: Go to the **Create Account** tab, enter a username, email, and password. Form validations verify input lengths and password matching.
2. **Login**: Enter your credentials in the **Sign In** tab to receive your secure JWT token.
3. **Dashboard**: View summary KPI metrics (Total Spent, Total Transactions, Average Transaction, Top Category) and breakdown charts.
4. **Add Expense**: Fill out the form with a Title, Amount (strictly > $0), Category, Date, and optional Notes.
5. **Manage Expenses**:
   - Filter by Category (Food & Dining, Transportation, Shopping, etc.).
   - Filter by Date Range (From Date -> To Date).
   - Search by keyword in Title or Notes.
   - Select any expense ID to **Edit** its details or **Delete** it permanently.

---

## <img src="https://api.iconify.design/fa6-solid/shield-halved.svg?color=%232563EB" width="20" height="20" align="center" /> Input Validation & Form Validations

| Field | Validation Rules | Implemented At |
|---|---|---|
| **Username** | Minimum 3 non-whitespace characters, unique across all users | Frontend & Pydantic Schema |
| **Email** | Valid email structure (`user@domain.com`), unique in database | Frontend & Pydantic `EmailStr` |
| **Password** | Minimum 6 characters, confirmation matching | Frontend Form & Backend Auth |
| **Expense Title** | Non-empty, 1-100 characters, whitespace stripped | Frontend & Pydantic `@field_validator` |
| **Expense Amount** | Positive float (`gt=0`), minimum $0.01 | Frontend input & Pydantic `Field(..., gt=0)` |
| **Expense Date** | Valid ISO Date (`YYYY-MM-DD`) | Streamlit date picker & Pydantic `date` |
| **Expense Category** | Non-empty, chosen from standard categories | Frontend Selectbox & Pydantic validator |

---

## <img src="https://api.iconify.design/fa6-solid/network-wired.svg?color=%232563EB" width="20" height="20" align="center" /> API Endpoints Reference

### Authentication Endpoints (`/auth`)

| Method | Endpoint | Description | Auth Required | Status Code |
|---|---|---|:---:|:---:|
| `POST` | `/auth/register` | Create a new user account | No | `201 Created` |
| `POST` | `/auth/login` | Authenticate user and receive JWT access token | No | `200 OK` |
| `GET` | `/auth/me` | Fetch currently logged-in user profile | **Yes (Bearer)** | `200 OK` |

### Expense Management Endpoints (`/expenses`)

| Method | Endpoint | Description | Auth Required | Status Code |
|---|---|---|:---:|:---:|
| `POST` | `/expenses/` | Create a new expense | **Yes (Bearer)** | `201 Created` |
| `GET` | `/expenses/` | List expenses (with category, date, search filters) | **Yes (Bearer)** | `200 OK` |
| `GET` | `/expenses/summary` | Aggregated analytics & category breakdown | **Yes (Bearer)** | `200 OK` |
| `GET` | `/expenses/categories/list` | Get list of predefined categories | No | `200 OK` |
| `GET` | `/expenses/{id}` | Get details of a single expense by ID | **Yes (Bearer)** | `200 OK` |
| `PUT` | `/expenses/{id}` | Update an existing expense by ID | **Yes (Bearer)** | `200 OK` |
| `DELETE` | `/expenses/{id}` | Delete an expense by ID | **Yes (Bearer)** | `200 OK` |

---

## <img src="https://api.iconify.design/fa6-solid/database.svg?color=%232563EB" width="20" height="20" align="center" /> Database Schema Design

The SQLite database (`expenses.db`) implements a clean relational schema using SQLAlchemy ORM:

```mermaid
erDiagram
    USERS ||--o{ EXPENSES : "creates / owns"
    USERS {
        int id PK
        string username UK
        string email UK
        string hashed_password
        datetime created_at
    }
    EXPENSES {
        int id PK
        int user_id FK
        string title
        float amount
        string category
        date date
        string description
        datetime created_at
    }
```

- **Relationships**: `User.expenses` has a one-to-many relationship with `Expense.owner`.
- **Cascade Deletion**: If a user is deleted, all their associated expenses are safely removed (`cascade="all, delete-orphan"`).
- **Data Isolation**: Each user can only view, edit, or delete expenses linked to their own `user_id`.

---


