# 📝 Project Tracker

A lightweight task tracker inspired by Jira and Yandex Tracker.  
It allows you to create projects, manage tasks, assign users, and visualize progress with a Kanban board.  

[![Python](https://img.shields.io/badge/python-3.11-blue?logo=python)](https://www.python.org/)  
[![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)](https://www.djangoproject.com/)  
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)](https://www.postgresql.org/)  
[![Docker](https://img.shields.io/badge/Docker-✔-blue?logo=docker)](https://www.docker.com/)  
[![CI/CD](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-black?logo=githubactions)](https://github.com/features/actions)  

---

## 🚀 Features
- Create and manage projects  
- Task creation with statuses and priorities  
- Kanban board for visual workflow management  
- User roles (admin, manager, contributor)  
- Search and filtering  
- Authentication & user profiles  
- REST API for integrations  

---

## 🛠️ Tech Stack
- **Backend:** Django, Django REST Framework  
- **Frontend:** Bootstrap, JavaScript  
- **Database:** PostgreSQL  
- **Containerization:** Docker, Docker Compose  
- **CI/CD:** GitHub Actions  
- **Testing:** pytest  

---

## ⚙️ Installation & Run

### Requirements
- Docker & Docker Compose  
- Git  

### Run with Docker
```bash
git clone https://github.com/username/project-tracker.git
cd project-tracker
docker-compose up --build -d
```
App will be available at:  
 http://localhost
 don't add :8000, this port is reserved  

### Local run (without Docker)
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## Project Structure
```
accounts/       # User authentication, profiles, signals
    templates/  # Register, login, reset password, profile
    static/     # CSS, JS for accounts
taskboard/      # Django project settings, URLs, WSGI/ASGI
tracker/        # Core app: projects, groups, tickets, Kanban
    templates/  # Groups, projects, tickets, base templates
    static/     # CSS, JS, images for tracker
requirements.txt
manage.py
docker/         
```

---

## API Example
```http
POST /api/tasks/
{
  "title": "Fix login bug",
  "project": 1,
  "assignee": 2,
  "status": "In Progress"
}
```

---

## TODO
- [ ] Fix project edditing
- [ ] Fix "Race condition" for ticket edditing
- [ ] Add backlog 
- [ ] Add django-redis
- [ ] Handling Ajax errors with toast-notifications
- [ ] Make loading indicators 
