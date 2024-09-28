# 📚 Library Management System

Welcome to the Library Management System! This project provides a comprehensive solution for managing e-books, user loans, and administrative tasks in a digital library environment.

## 🌟 Features

- 👤 User authentication and role-based access control
- 📖 E-book and section management
- 📅 Loan system with automatic revocation
- 📊 Admin dashboard for monitoring library activities
- 📧 Automated email notifications and reports

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy, JWT for authentication
- **Database**: SQLite
- **Task Queue**: Celery with Redis as broker
- **Frontend**: Vue.js

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Redis server
- Node.js and npm (for frontend)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/library-management-system.git
   cd library-management-system
   ```

2. Set up a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```
   flask db upgrade
   ```

4. Start the Redis server:
   ```
   redis-server
   ```

5. Start the Celery worker:
   ```
   celery -A app.celery worker --loglevel=info
   ```

6. Start the Celery beat scheduler:
   ```
   celery -A app.celery beat --loglevel=info
   ```

7. Run the Flask application:
   ```
   flask run
   ```

8. (Optional) Set up and run the frontend application (assuming Vue.js):
   ```
   cd frontend
   npm install
   npm run serve
   ```

