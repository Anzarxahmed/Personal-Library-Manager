from fastapi import FastAPI, Depends, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, func, or_
from typing import List, Optional, Dict
from contextlib import asynccontextmanager
import json
import os
from dotenv import load_dotenv

from database import engine, init_db, get_session, Book
from schemas import (
    BookCreate, 
    BookUpdate, 
    BookStats, 
    AIRecommendRequest, 
    AIRecommendResponse, 
    AIRecommendItem,
    AISummaryRequest, 
    AISummaryResponse
)

load_dotenv()

# Setup lifespan for startup database initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Personal Library Manager API",
    description="A FastAPI backend for managing personal books with AI recommendations and summaries.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq Client
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
groq_client = None

if GROQ_API_KEY and not GROQ_API_KEY.startswith("gsk_placeholder") and len(GROQ_API_KEY.strip()) > 10:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
    except ImportError:
        print("Groq SDK is not installed or import failed.")

# --- Helper for Mock AI Responses when API key is missing ---
MOCK_RECOMMENDATIONS: Dict[str, List[Dict[str, str]]] = {
    "sci-fi": [
        {"title": "The Left Hand of Darkness", "author": "Ursula K. Le Guin", "reason": "A masterpiece of sociological science fiction examining gender and political intrigue on an icy planet."},
        {"title": "Childhood's End", "author": "Arthur C. Clarke", "reason": "A profound first-contact story detailing the peaceful invasion of Earth by the mysterious Overlords."},
        {"title": "Rendezvous with Rama", "author": "Arthur C. Clarke", "reason": "A classic hard sci-fi mystery depicting the exploration of a giant, cylindrical alien vessel entering our solar system."}
    ],
    "fantasy": [
        {"title": "The Way of Kings", "author": "Brandon Sanderson", "reason": "An epic, world-spanning fantasy boasting an intricate magic system and deep character redemption arcs."},
        {"title": "The Blade Itself", "author": "Joe Abercrombie", "reason": "A gritty, character-driven grimdark fantasy with sharp dialogue, complex morals, and dark humor."},
        {"title": "A Wizard of Earthsea", "author": "Ursula K. Le Guin", "reason": "A beautifully poetic classic exploring balance, shadow, and the heavy price of pride in magic."}
    ],
    "programming": [
        {"title": "Structure and Interpretation of Computer Programs", "author": "Harold Abelson & Gerald Jay Sussman", "reason": "A foundational text teaching computer science concepts through Lisp/Scheme."},
        {"title": "The Mythical Man-Month", "author": "Fred Brooks", "reason": "Essential software engineering essays on project management, staffing, and architecture complexity."},
        {"title": "Working Effectively with Legacy Code", "author": "Michael Feathers", "reason": "The definitive guide on testing, managing, and safely refactoring systems that lack test coverage."}
    ],
    "self help": [
        {"title": "Mindset: The New Psychology of Success", "author": "Carol S. Dweck", "reason": "Explains how adopting a growth mindset instead of a fixed mindset unlocks human potential."},
        {"title": "The War of Art", "author": "Steven Pressfield", "reason": "Identifies the creative enemy 'Resistance' and details how to break through creative barriers."},
        {"title": "Drive: The Surprising Truth About What Motivates Us", "author": "Daniel H. Pink", "reason": "Examines the three elements of true motivation: Autonomy, Mastery, and Purpose."}
    ]
}

MOCK_SUMMARIES: Dict[str, str] = {
    "dune": "Dune is a landmark science fiction novel set in a far-future space empire. The story follows young Paul Atreides, whose family inherits the rule of Arrakis, a desolate desert world. Arrakis is the only source of 'spice', the most valuable commodity in the universe that allows space travel and longevity. After a betrayal, Paul retreats into the desert, joins the native Fremen, and orchestrates a revolution to retake the planet, confronting themes of political scheming, religion, ecology, and messianic danger.",
    "atomic habits": "Atomic Habits by James Clear argues that big life changes come from the compounding effect of hundreds of small decisions. Relying on cognitive science, Clear explains the Four Laws of Behavior Change: make it obvious, make it attractive, make it easy, and make it satisfying. He details practical ways to build positive habits and systematically dismantle bad ones, asserting that we do not rise to the level of our goals, but rather fall to the level of our systems.",
    "1984": "1984 is a classic dystopian novel illustrating life under a totalitarian regime headed by Big Brother. The protagonist, Winston Smith, works for the Ministry of Truth, editing history to align with the Party's ever-changing narrative. Frustrated by the oppressive surveillance and thought control, Winston begins a secret love affair and writes in a forbidden diary. Ultimately, Winston is caught, tortured, and brainwashed, showcasing the terrifying lengths a regime will go to control thought and objective truth."
}

# --- API ENDPOINTS ---

# 1. POST /books: Add a new book
@app.post("/books", response_model=Book, status_code=201)
def create_book(book_in: BookCreate, session: Session = Depends(get_session)):
    db_book = Book.model_validate(book_in)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

# 2. GET /books: Get all books (paginated)
@app.get("/books", response_model=List[Book])
def read_books(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=100), 
    session: Session = Depends(get_session)
):
    statement = select(Book).offset(skip).limit(limit)
    results = session.exec(statement)
    return list(results.all())

# 3. GET /books/search: Search books by title/author/genre
@app.get("/books/search", response_model=List[Book])
def search_books(
    q: str = Query(..., min_length=1, description="Search term for title, author, or genre"),
    session: Session = Depends(get_session)
):
    search_term = f"%{q}%"
    statement = select(Book).where(
        or_(
            Book.title.like(search_term),
            Book.author.like(search_term),
            Book.genre.like(search_term)
        )
    )
    results = session.exec(statement)
    return list(results.all())

# 4. GET /books/stats: View library statistics
@app.get("/books/stats", response_model=BookStats)
def get_library_stats(session: Session = Depends(get_session)):
    # Total books
    total = session.exec(select(func.count(Book.id))).one()
    
    # Group by reading status
    status_statement = select(Book.reading_status, func.count(Book.id)).group_by(Book.reading_status)
    status_results = session.exec(status_statement).all()
    status_counts = {status: count for status, count in status_results}
    
    # Group by genre
    genre_statement = select(Book.genre, func.count(Book.id)).group_by(Book.genre)
    genre_results = session.exec(genre_statement).all()
    genre_counts = {genre: count for genre, count in genre_results}
    
    # Average rating (for books that have a rating)
    rating_stmt = select(func.avg(Book.rating)).where(Book.rating != None)
    avg_rating = session.exec(rating_stmt).one()
    
    return BookStats(
        total_books=total,
        status_counts=status_counts,
        genre_counts=genre_counts,
        average_rating=round(avg_rating, 2) if avg_rating is not None else None
    )

# 5. GET /books/status/{status}: Filter books by reading status
@app.get("/books/status/{status}", response_model=List[Book])
def read_books_by_status(status: str, session: Session = Depends(get_session)):
    valid_statuses = ["to read", "reading", "completed"]
    normalized_status = status.strip().lower()
    
    # Find matching capitalization in DB context
    db_status = "To Read"
    if normalized_status == "reading":
        db_status = "Reading"
    elif normalized_status == "completed":
        db_status = "Completed"
    elif normalized_status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid reading status '{status}'. Must be one of: To Read, Reading, Completed"
        )
        
    statement = select(Book).where(Book.reading_status == db_status)
    results = session.exec(statement)
    return list(results.all())

# 6. GET /books/{id}: Get a single book by ID
@app.get("/books/{id}", response_model=Book)
def read_book(id: int, session: Session = Depends(get_session)):
    db_book = session.get(Book, id)
    if not db_book:
        raise HTTPException(status_code=404, detail=f"Book with ID {id} not found")
    return db_book

# 7. PUT /books/{id}: Update book details
@app.put("/books/{id}", response_model=Book)
def update_book(id: int, book_update: BookUpdate, session: Session = Depends(get_session)):
    db_book = session.get(Book, id)
    if not db_book:
        raise HTTPException(status_code=404, detail=f"Book with ID {id} not found")
        
    update_data = book_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_book, key, value)
        
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

# 8. DELETE /books/{id}: Delete a book
@app.delete("/books/{id}")
def delete_book(id: int, session: Session = Depends(get_session)):
    db_book = session.get(Book, id)
    if not db_book:
        raise HTTPException(status_code=404, detail=f"Book with ID {id} not found")
    session.delete(db_book)
    session.commit()
    return {"message": f"Book '{db_book.title}' successfully deleted", "id": id}

# 9. POST /books/ai/recommend: AI Recommendations
@app.post("/books/ai/recommend", response_model=AIRecommendResponse)
def get_ai_recommendations(req: AIRecommendRequest, response: Response):
    genre_clean = req.genre.strip().lower()
    
    if groq_client:
        try:
            prompt = (
                f"As an expert librarian, recommend exactly 3 highly recommended books for the genre '{req.genre}'. "
                "You must return the response strictly as a JSON object containing a 'recommendations' key which maps "
                "to an array of 3 objects. Each object must have exactly these keys: 'title', 'author', 'reason'. "
                "Do not include any greeting, introduction, trailing remarks, or markdown fencing other than the JSON output. "
                "Example format: "
                "{"
                '  "recommendations": ['
                '    {"title": "Book 1", "author": "Author 1", "reason": "Why read it..."}'
                '  ]'
                "}"
            )
            
            completion = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that only responds in raw, valid JSON format matching the schema provided. Do not explain, apologize, or format with markdown code blocks."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = completion.choices[0].message.content
            data = json.loads(content)
            
            items = []
            for item in data.get("recommendations", []):
                items.append(AIRecommendItem(
                    title=item.get("title", "Unknown Title"),
                    author=item.get("author", "Unknown Author"),
                    reason=item.get("reason", "Highly recommended.")
                ))
            
            response.headers["x-ai-source"] = "groq"
            return AIRecommendResponse(genre=req.genre, recommendations=items)
            
        except Exception as e:
            # Fallback to local mock on failure
            print(f"Groq API Error: {e}. Falling back to mock data.")
            pass

    # Mock response logic
    response.headers["x-ai-source"] = "mock"
    mock_items = MOCK_RECOMMENDATIONS.get(genre_clean)
    if not mock_items:
        # Generate generic recommendations
        mock_items = [
            {"title": f"The Secrets of {req.genre.capitalize()}", "author": "A. Novelist", "reason": f"A brilliant, page-turning entry exploring the foundations of {req.genre}."},
            {"title": f"Masters of {req.genre.capitalize()}", "author": "B. Scholar", "reason": f"Provides historical context and essential lessons within the {req.genre} genre."},
            {"title": f"The Future of {req.genre.capitalize()}", "author": "C. Visionary", "reason": f"A highly praised modern classic that pushes the boundaries of {req.genre} literature."}
        ]
        
    items = [AIRecommendItem(**item) for item in mock_items]
    return AIRecommendResponse(genre=req.genre, recommendations=items)

# 10. POST /books/ai/summary: Generate AI book summary
@app.post("/books/ai/summary", response_model=AISummaryResponse)
def get_ai_summary(req: AISummaryRequest, response: Response, session: Session = Depends(get_session)):
    title_clean = req.title.strip().lower()
    
    # 1. Check if the book is in our database and already has a cached summary
    statement = select(Book).where(func.lower(Book.title) == title_clean)
    db_book = session.exec(statement).first()
    if db_book and db_book.summary:
        response.headers["x-ai-source"] = "db_cache"
        return AISummaryResponse(title=db_book.title, summary=db_book.summary)
        
    # 2. Call Groq if configured
    if groq_client:
        try:
            prompt = (
                f"Provide a concise, engaging 3-4 sentence summary of the book '{req.title}'. "
                "Focus on the main plot, core themes, and key takeaways. Do not include spoilers for the ending. "
                "Do not add introductions like 'Here is a summary...' or explanations."
            )
            
            completion = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional book reviewer. Write brief, high-level summaries without spoilers."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            summary_text = completion.choices[0].message.content.strip()
            
            # Cache the summary back to the DB if the book exists
            if db_book:
                db_book.summary = summary_text
                session.add(db_book)
                session.commit()
                session.refresh(db_book)
                
            response.headers["x-ai-source"] = "groq"
            return AISummaryResponse(title=req.title, summary=summary_text)
            
        except Exception as e:
            print(f"Groq API Error: {e}. Falling back to mock data.")
            pass
            
    # 3. Fallback to mock summaries
    response.headers["x-ai-source"] = "mock"
    summary_text = MOCK_SUMMARIES.get(title_clean)
    if not summary_text:
        summary_text = (
            f"This is a placeholder summary for '{req.title}' because the Groq API key is not configured or could not be reached. "
            "Once configured with a valid GROQ_API_KEY, this API will generate a concise, custom 3-4 sentence summary "
            "explaining the main plot, core themes, and key takeaways of the book."
        )
        
    # Cache the mock summary back to the DB if the book exists
    if db_book:
        db_book.summary = summary_text
        session.add(db_book)
        session.commit()
        session.refresh(db_book)
        
    return AISummaryResponse(title=req.title, summary=summary_text)

# Default root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Personal Library Manager API!",
        "docs_url": "/docs",
        "status": "online"
    }
