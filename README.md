# semantic_product_search

A FastAPI-based Semantic Product Search system using PostgreSQL and Qdrant Vector Database.

The system allows users to search for electronic products using natural language queries instead of exact keywords. It also compares traditional SQL search with semantic vector search.

---

# Features
- FastAPI backend
- PostgreSQL keyword search
- Qdrant semantic vector search
- SQL vs Semantic search comparison
- Image search using CLIP
- Product recommendation (similar products)

---

# Quickstart (Local)

## Create virtual environment
python3 -m venv .venv  
source .venv/bin/activate  

## Install dependencies
pip install -r backend/requirements.txt  

## Start databases (PostgreSQL + Qdrant)
docker-compose up -d  

## Run FastAPI
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000  

Open API docs:  
http://localhost:8000/docs  

## Run Frontend
cd frontend  
npm install  
npm start  

Frontend: http://localhost:3000  

---

# Environment Variables
Create a `.env` file:

OPENAI_API_KEY=your_key  
POSTGRES_HOST=localhost  
POSTGRES_DB=semantic_search  
POSTGRES_USER=postgres  
POSTGRES_PASSWORD=123456  
QDRANT_HOST=localhost  
QDRANT_PORT=6333  

---

# Project Layout
semantic-product-search/
├── backend/
├── frontend/
├── report/
├── demo/
├── docker-compose.yml
├── README.md
├── requirements.txt
└── .gitignore

---

# API Endpoints
| Endpoint | Description |
|---------|-------------|
| /search/sql | SQL keyword search |
| /search/semantic | Semantic vector search |
| /search/image | Image search |
| /products | Get all products |

---

# Testing
Use Swagger:
http://localhost:8000/docs

Example:
- /search/semantic?query=laptop for students
- /search/sql?query=laptop

---

# License
Academic project only.
