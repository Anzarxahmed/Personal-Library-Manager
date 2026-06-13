# 📚 Personal Library Manager (FastAPI + SQLModel + Groq AI)

## 📌 Project Overview

The Personal Library Manager is a full-stack backend project built using FastAPI, SQLModel, and Pydantic, with AI-powered features using Groq LLM.

It allows users to manage their personal book collection, track reading progress, and get AI-powered book recommendations and summaries.

---

## 🚀 Features

### 📖 Book Management
- Add new books
- View all books (50+ seeded books)
- Get a single book by ID
- Update book details
- Delete books

### 🔎 Advanced Features
- Filter books by reading status
- Search books by title/author/genre
- View library statistics

### 🤖 AI Features (Groq LLM)
- Get book recommendations by genre
- Generate AI book summaries

### 🗄️ Database
- SQLite database

### 🧪 API Testing
- Fully tested using Swagger UI (/docs)

### 🎨 Optional UI
- Streamlit frontend (simple interface)
- Fully functional API integration

### ☁️ Deployment
- Backend deployed on Render/Railway
- Frontend deployable on Streamlit Cloud/Vercel

---

## 🏗️ Project Structure

your-project/
├── main.py              # FastAPI app + endpoints
├── schemas.py          # Pydantic models (Input/Output)
├── database.py         # SQLModel engine + session
├── requirements.txt    # Dependencies
├── .env                # Groq API key (NOT committed)
├── .env.example       # Sample env file
├── .gitignore         # Ignore sensitive files
└── README.md          # Documentation

---

## 🧠 Tech Stack

- FastAPI
- SQLModel
- SQLite
- Pydantic
- Groq API (LLM)
- Python-dotenv
- Streamlit (Frontend)

---

## 📦 Installation Guide

1. Clone Repository
git clone https://github.com/your-username/library-manager.git
cd library-manager

2. Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Setup Environment Variables
GROQ_API_KEY=your_api_key_here

---

## ▶️ Run Project

uvicorn main:app --reload

http://127.0.0.1:8000
http://127.0.0.1:8000/docs

---

## 🔗 API Endpoints

CRUD:
POST /books
GET /books
GET /books/{id}
PUT /books/{id}
DELETE /books/{id}

Extras:
GET /books/status/{status}
GET /books/search
GET /books/stats

AI:
POST /books/ai/recommend
POST /books/ai/summary

---

## 🤖 AI Features

Recommendations:
Input: genre
Output: 3 suggested books

Summary:
Input: book title
Output: AI generated summary

---

## 📊 Dataset

50 Books seeded in SQLite covering:
Fantasy, Sci-Fi, Programming, Self Help, History, etc.

---

## 🎨 Streamlit UI

streamlit run app.py

---

## ☁️ Deployment

Render / Railway:
uvicorn main:app --host 0.0.0.0 --port 10000

---

## 🧠 Learning Outcomes

- FastAPI REST API
- SQLModel database
- Pydantic validation
- AI integration (Groq)
- Full stack project design

---

## 🏁 Conclusion

AI-powered personal library system with CRUD + AI + UI + Deployment.
