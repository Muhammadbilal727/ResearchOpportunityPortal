# University Research Opportunity Portal
GitHub Repository: https://github.com/Muhammadbilal727/ResearchOpportunityPortal
A web app where faculty manage research opportunities and students can browse them.
Built for Computer Networks (CN), Fall 2026.

## Tech Stack
- Frontend: HTML, CSS, JavaScript, Bootstrap
- Backend: Python (Flask) REST API
- Database: MySQL
- API testing: Postman

## Project Structure
```
ResearchOpportunityPortal/
├── Backend/        (Flask API, requirements.txt, postman_collection.json)
├── frontend/       (index.html, script.js)
├── database.sql
└── README.md
```

## Setup

### 1. Database
Open `database.sql` in MySQL Workbench and run it. It creates the `research_portal` database and the `opportunities` table.

### 2. Backend
```
cd Backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Create a file `Backend/.env` with:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=research_portal
```
Start the server:
```
python app.py
```
The API runs at http://127.0.0.1:5000

### 3. Frontend
With the backend running, open `frontend/index.html` in a browser.

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/opportunities | Create an opportunity |
| GET | /api/opportunities | Get all opportunities |
| GET | /api/opportunities/:id | Get one opportunity |
| PUT | /api/opportunities/:id | Update an opportunity |
| DELETE | /api/opportunities/:id | Delete an opportunity |

Status codes used: 200, 201, 400, 404, 500.

## Testing
Import `Backend/postman_collection.json` into Postman to test all endpoints.

## Features
- View, create, edit, close and delete opportunities
- Form validation and success/error messages
- Data stored permanently in MySQL

## Author
MUHAMMAD BILAL, 24P-0749

## Demonstration Video
[Click here to watch the  demonstration video](https://drive.google.com/file/d/1D0D0-MXhukIlW1tJfF9i-lL7JrhS7yoo/view?usp=sharing)