# Taskish - Team Task Management System

A production-ready MVP for private and team task management with a kanban board.

## Features

- **User Authentication**: Email/password login with JWT tokens
- **Private Todos**: Personal tasks visible only to the owner
- **Team Tasks**: Shared tasks visible to all team members
- **Kanban Board**: Drag-and-drop task management with TODO, IN_PROGRESS, BLOCKED, DONE columns
- **Task Hierarchy**: Main tasks with sub-tasks, each assignable to team members
- **Role-Based Access**: ADMIN (managers) and MEMBER roles with appropriate permissions

## Tech Stack

- **Backend**: Python Flask REST API with SQLAlchemy
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Authentication**: JWT with secure password hashing (bcrypt)
- **Frontend**: React + Vite + TypeScript + Tailwind CSS
- **API Client**: Axios

## Project Structure

```
taskish/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── config.py            # Configuration
│   │   ├── models/              # SQLAlchemy models
│   │   ├── routes/              # API routes
│   │   ├── services/            # Business logic
│   │   └── utils/               # Utilities
│   ├── tests/                   # Pytest tests
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── hooks/               # Custom hooks
│   │   ├── services/            # API services
│   │   ├── types/               # TypeScript types
│   │   └── utils/               # Utilities
│   ├── package.json
│   └── vite.config.ts
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
cp .env.example .env
# Edit .env with your settings

# Initialize database
flask db upgrade

# Run development server
flask run --debug
```

The backend will be available at `http://localhost:5000`.

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables (create .env file)
cp .env.example .env

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

### Environment Variables

#### Backend (.env)

```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
DATABASE_URL=sqlite:///taskish.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/taskish
```

#### Frontend (.env)

```
VITE_API_URL=http://localhost:5000/api
```

## Running Tests

### Backend Tests

```bash
cd backend
pytest -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

## API Documentation

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Login user |
| POST | /api/auth/logout | Logout user |
| GET | /api/auth/me | Get current user |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/teams/:teamId/users | Get team members |

### Private Todos

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/private-todos | List user's private todos |
| POST | /api/private-todos | Create private todo |
| GET | /api/private-todos/:id | Get private todo |
| PUT | /api/private-todos/:id | Update private todo |
| DELETE | /api/private-todos/:id | Delete private todo |

### Team Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/team-tasks | List team tasks |
| POST | /api/team-tasks | Create team task (Admin) |
| GET | /api/team-tasks/:id | Get team task |
| PUT | /api/team-tasks/:id | Update team task |
| PATCH | /api/team-tasks/:id/status | Update task status |
| PATCH | /api/team-tasks/:id/assign | Assign task (Admin) |
| DELETE | /api/team-tasks/:id | Delete team task (Admin) |

### Sub-Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/team-tasks/:id/sub-tasks | List sub-tasks |
| POST | /api/team-tasks/:id/sub-tasks | Create sub-task (Admin) |
| PUT | /api/team-tasks/:id/sub-tasks/:subId | Update sub-task |
| PATCH | /api/team-tasks/:id/sub-tasks/:subId/status | Update sub-task status |
| DELETE | /api/team-tasks/:id/sub-tasks/:subId | Delete sub-task (Admin) |

## Role Permissions

### ADMIN
- Create, edit, delete team tasks
- Assign tasks to team members
- Create, edit, delete sub-tasks
- Assign sub-tasks to team members
- Update any task/sub-task status
- Full access to own private todos

### MEMBER
- View team tasks
- Update status on tasks assigned to them
- Update status on sub-tasks assigned to them
- Full access to own private todos

## License

MIT
