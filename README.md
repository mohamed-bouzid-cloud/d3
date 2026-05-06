# Healthcare FHIR Platform (d3)

This is a monorepo containing both the Django backend and the Angular frontend for the Healthcare FHIR Platform.

## Prerequisites
- **Node.js** (v18+)
- **Python** (3.10+)

## Quick Start

### 1. Start the Backend (Django)
Open a terminal and navigate to the `d3` directory:
```bash
cd d3
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
The API will be available at `http://127.0.0.1:8000/api/` and the Swagger Docs at `http://127.0.0.1:8000/api/docs/`.

### 2. Start the Frontend (Angular)
Open a *new* terminal and navigate to the `frontend` directory:
```bash
cd frontend
npm install
npm start
```
The application will be available at `http://localhost:4200/`.
