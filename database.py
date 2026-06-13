from typing import Optional, Generator, List, Dict, Any
from sqlmodel import SQLModel, Field, create_engine, Session, select
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./library.db")

# SQLite needs connect_args={"check_same_thread": False} for FastAPI async requests
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    author: str = Field(index=True)
    genre: str = Field(index=True)
    published_year: Optional[int] = None
    reading_status: str = Field(default="To Read")  # "To Read", "Reading", "Completed"
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    review: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

# Seed Data (57 books)
SEED_BOOKS: List[Dict[str, Any]] = [
    # Fantasy
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "genre": "Fantasy", "published_year": 1937, "reading_status": "Completed", "rating": 5, "review": "A timeless classic that introduces Middle-earth.", "summary": "Bilbo Baggins, a home-loving hobbit, is swept into a quest to reclaim a treasure stolen by the dragon Smaug."},
    {"title": "The Fellowship of the Ring", "author": "J.R.R. Tolkien", "genre": "Fantasy", "published_year": 1954, "reading_status": "Reading", "rating": None, "review": None, "summary": None},
    {"title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "genre": "Fantasy", "published_year": 1997, "reading_status": "Completed", "rating": 5, "review": "Brings back wonderful childhood memories.", "summary": "An orphaned boy learns he is a wizard and begins his education at Hogwarts School of Witchcraft and Wizardry."},
    {"title": "A Game of Thrones", "author": "George R.R. Martin", "genre": "Fantasy", "published_year": 1996, "reading_status": "Completed", "rating": 4, "review": "Intricate plotting and dark themes. Very engaging.", "summary": "Noble families contend for control of the mythical land of Westeros in a massive civil war."},
    {"title": "The Way of Kings", "author": "Brandon Sanderson", "genre": "Fantasy", "published_year": 2010, "reading_status": "Reading", "rating": None, "review": None, "summary": None},
    {"title": "The Name of the Wind", "author": "Patrick Rothfuss", "genre": "Fantasy", "published_year": 2007, "reading_status": "To Read", "rating": None, "review": None, "summary": None},
    {"title": "Good Omens", "author": "Neil Gaiman & Terry Pratchett", "genre": "Fantasy", "published_year": 1990, "reading_status": "Completed", "rating": 5, "review": "Hilarious and clever adaptation of the apocalypse.", "summary": "An angel and a demon who have grown fond of earth try to prevent the Apocalypse."},
    {"title": "The Lies of Locke Lamora", "author": "Scott Lynch", "genre": "Fantasy", "published_year": 2006, "reading_status": "To Read", "rating": None, "review": None, "summary": None},
    
    # Sci-Fi
    {"title": "Dune", "author": "Frank Herbert", "genre": "Sci-Fi", "published_year": 1965, "reading_status": "Completed", "rating": 5, "review": "Masterpiece of political intrigue, ecology, and science fiction.", "summary": "Set in a far-future galactic empire, Paul Atreides' family accepts control of the desert planet Arrakis, the source of the universe's most valuable substance, spice."},
    {"title": "Neuromancer", "author": "William Gibson", "genre": "Sci-Fi", "published_year": 1984, "reading_status": "Completed", "rating": 4, "review": "The quintessential cyberpunk novel. Style over substance, but what a style!", "summary": "A washed-up computer hacker is hired by a mysterious employer for one last ultimate hack."},
    {"title": "Foundation", "author": "Isaac Asimov", "genre": "Sci-Fi", "published_year": 1951, "reading_status": "To Read", "rating": None, "review": None, "summary": None},
    {"title": "The Hitchhiker's Guide to the Galaxy", "author": "Douglas Adams", "genre": "Sci-Fi", "published_year": 1979, "reading_status": "Completed", "rating": 5, "review": "Pure fun. Absolute comedic genius.", "summary": "Arthur Dent escapes the destruction of Earth with the help of his alien friend Ford Prefect, traveling the cosmos in hilarious fashion."},
    {"title": "Snow Crash", "author": "Neal Stephenson", "genre": "Sci-Fi", "published_year": 1992, "reading_status": "Reading", "rating": None, "review": None, "summary": None},
    {"title": "Hyperion", "author": "Dan Simmons", "genre": "Sci-Fi", "published_year": 1989, "reading_status": "To Read", "rating": None, "review": None, "summary": None},
    {"title": "Ender's Game", "author": "Orson Scott Card", "genre": "Sci-Fi", "published_year": 1985, "reading_status": "Completed", "rating": 4, "review": "Great pacing and psychological depth.", "summary": "A young military genius is trained to lead the human race against an alien threat."},
    {"title": "The Martian", "author": "Andy Weir", "genre": "Sci-Fi", "published_year": 2011, "reading_status": "Completed", "rating": 5, "review": "Highly scientific yet extremely funny and fast-paced.", "summary": "An American astronaut is stranded on Mars and must use his scientific wits to survive until rescue."},
    {"title": "Project Hail Mary", "author": "Andy Weir", "genre": "Sci-Fi", "published_year": 2021, "reading_status": "Reading", "rating": None, "review": None, "summary": None},
    
    # Programming / Tech
    {"title": "Clean Code", "author": "Robert C. Martin", "genre": "Programming", "published_year": 2008, "reading_status": "Reading", "rating": 4, "review": "Essential reading for any developer, though some examples are a bit dated.", "summary": "A handbook of agile software craftsmanship that teaches how to write code that is clean, readable, and maintainable."},
    {"title": "The Pragmatic Programmer", "author": "Andrew Hunt & David Thomas", "genre": "Programming", "published_year": 1999, "reading_status": "Completed", "rating": 5, "review": "One of the best books on software development mindset.", "summary": "A collection of tips, analogies, and best practices for developing software and managing career growth as a programmer."},
    {"title": "Design Patterns", "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides", "genre": "Programming", "published_year": 1994, "reading_status": "Reading", "rating": None, "review": None, "summary": None},
    {"title": "Refactoring", "author": "Martin Fowler", "genre": "Programming", "published_year": 1999, "reading_status": "To Read", "rating": None, "review": None, "summary": None},
    {"title": "Introduction to Algorithms", "author": "Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein", "genre": "Programming", "published_year": 1990, "reading_status": "To Read", "rating": None, "review": None, "summary": None},
    {"title": "Code Complete", "author": "Steve McConnell", "genre": "Programming", "published_year": 1993, "reading_status": "Reading", "rating": None, "review": None, "summary": None},
    {"title": "You Don't Know JS", "author": "Kyle Simpson", "genre": "Programming", "published_year": 2014, "reading_status": "Completed", "rating": 4, "review": "Dives deep into JS mechanics. Highly recommended.", "summary": "A series of books diving deep into the core mechanics of the JavaScript language."},
    {"title": "Fluent Python", "author": "Luciano Ramalho", "genre": "Programming", "published_year": 2015, "reading_status": "Completed", "rating": 5, "review": "The best resource to write idiomatic Python.", "summary": "A guide to writing effective and modern Python code, leveraging its best features."},
    {"title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "genre": "Programming", "published_year": 2017, "reading_status": "Reading", "rating": None, "review": None, "summary": None},

    # Self Help / Personal Development
    {"title": "Atomic Habits", "author": "James Clear", "genre": "Self Help", "published_year": 2018, "reading_status": "Completed", "rating": 5, "review": "Extremely actionable advice with real examples.", "summary": "An easy and proven way to build good habits and break bad ones by focusing on tiny, 1% improvements daily."},
    {"title": "The 7 Habits of Highly Effective People", "author": "Stephen R. Covey", "genre": "Self Help", "published_year": 1989, "reading_status": "Completed", "rating": 4, "review": "A classic framework for personal development.", "summary": "Presents a holistic, integrated, principle-centered approach for solving personal and professional problems."},
    {"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "genre": "Self Help", "published_year": 2011, "reading_status": "Reading", "rating": None, "review": None, "summary": None},
    {"title": "Deep Work", "author": "Cal Newport", "genre": "Self Help", "published_year": 2016, "reading_status": "Completed", "rating": 5, "review": "Crucial guide for staying focused in a distracted world.", "summary": "Rules for focused success in a distracted world, arguing that cognitive depth is a superpower."},
    {"title": "Man's Search for Meaning", "author": "Viktor E. Frankl", "genre": "Self Help", "published_year": 1946, "reading_status": "Completed", "rating": 5, "review": "Deeply moving and profoundly influential.", "summary": "Psychiatrist Viktor Frankl's memoir of surviving Nazi concentration camps, detailing his psychotherapeutic method of finding meaning."},
    {"title": "Can't Hurt Me", "author": "David Goggins", "genre": "Self Help", "published_year": 2018, "reading_status": "Completed", "rating": 4, "review": "Incredible mental toughness. Highly motivating.", "summary": "David Goggins shares his life story of overcoming severe adversity to become a Navy SEAL and ultra-endurance athlete."},
    {"title": "The Subtle Art of Not Giving a F*ck", "author": "Mark Manson", "genre": "Self Help", "published_year": 2016, "reading_status": "Completed", "rating": 3, "review": "A bit repetitive but has some valid points about values.", "summary": "A counterintuitive guide to living a good life, urging readers to choose their struggles and values wisely."},
    {"title": "Mindset", "author": "Carol S. Dweck", "genre": "Self Help", "published_year": 2006, "reading_status": "To Read", "rating": None, "review": None, "summary": None},
    {"title": "Show Your Work!", "author": "Austin Kleon", "genre": "Self Help", "published_year": 2014, "reading_status": "Completed", "rating": 5, "review": "Short, visual, and highly inspiring for creatives.", "summary": "10 ways to share your creativity and get discovered, focusing on process over product."},

    # History / Biography
    {"title": "Sapiens", "author": "Yuval Noah Harari", "genre": "History", "published_year": 2011, "reading_status": "Completed", "rating": 5, "review": "Fascinating sweep of human history.", "summary": "A narrative history of humanity, from the evolution of archaic human species in the Stone Age up to the twenty-first century."},
    {"title": "Steve Jobs", "author": "Walter Isaacson", "genre": "Biography", "published_year": 2011, "reading_status": "Completed", "rating": 4, "review": "Honest and detailed account of Jobs' life.", "summary": "The biography of Apple co-founder Steve Jobs, based on hundreds of interviews with Jobs, family, and colleagues."},
    {"title": "Alexander Hamilton", "author": "Ron Chernow", "genre": "Biography", "published_year": 2004, "reading_status": "To Read", "rating": None, "review": None, "summary": None},
    {"title": "Educated", "author": "Tara Westover", "genre": "Biography", "published_year": 2018, "reading_status": "Completed", "rating": 5, "review": "Remarkable story of self-reinvention through education.", "summary": "A memoir about a young girl who leaves her survivalist family in Idaho to pursue higher education, eventually earning a PhD from Cambridge."},
    {"title": "Team of Rivals", "author": "Doris Kearns Goodwin", "genre": "History", "published_year": 2005, "reading_status": "To Read", "rating": None, "review": None, "summary": None},
    {"title": "The Guns of August", "author": "Barbara W. Tuchman", "genre": "History", "published_year": 1962, "reading_status": "To Read", "rating": None, "review": None, "summary": None},
    {"title": "Genghis Khan and the Making of the Modern World", "author": "Jack Weatherford", "genre": "History", "published_year": 2004, "reading_status": "Completed", "rating": 4, "review": "Challenged a lot of my preconceptions about the Mongols.", "summary": "An examination of how Genghis Khan's conquests and empire-building shaped modern global culture, trade, and systems."},
    {"title": "Leonardo da Vinci", "author": "Walter Isaacson", "genre": "Biography", "published_year": 2017, "reading_status": "Reading", "rating": None, "review": None, "summary": None},

    # Mystery / Thriller
    {"title": "The Da Vinci Code", "author": "Dan Brown", "genre": "Mystery", "published_year": 2003, "reading_status": "Completed", "rating": 4, "review": "A fast-paced puzzle-box thriller.", "summary": "Symbologist Robert Langdon and cryptologist Sophie Neveu investigate a murder in the Louvre, uncovering a massive religious conspiracy."},
    {"title": "Gone Girl", "author": "Gillian Flynn", "genre": "Thriller", "published_year": 2012, "reading_status": "Completed", "rating": 4, "review": "Fantastic unreliable narrators and plot twists.", "summary": "A psychological thriller about the mysterious disappearance of Amy Dunne and the media circus surrounding her husband, Nick."},
    {"title": "The Girl with the Dragon Tattoo", "author": "Stieg Larsson", "genre": "Mystery", "published_year": 2005, "reading_status": "Completed", "rating": 4, "review": "Dark and gripping mystery.", "summary": "Journalist Mikael Blomkvist and hacker Lisbeth Salander team up to solve the forty-year-old disappearance of Harriet Vanger."},
    {"title": "The Silent Patient", "author": "Alex Michaelides", "genre": "Thriller", "published_year": 2019, "reading_status": "Reading", "rating": None, "review": None, "summary": None},
    {"title": "Sherlock Holmes: A Study in Scarlet", "author": "Arthur Conan Doyle", "genre": "Mystery", "published_year": 1887, "reading_status": "Completed", "rating": 5, "review": "The iconic introduction of Sherlock and Watson.", "summary": "A detective and a doctor meet, share rooms, and solve a complex murder of revenge."},
    {"title": "And Then There Were None", "author": "Agatha Christie", "genre": "Mystery", "published_year": 1939, "reading_status": "Completed", "rating": 5, "review": "The best mystery novel ever written.", "summary": "Ten strangers are lured to an isolated island, where they are murdered one by one according to a nursery rhyme."},
    {"title": "Big Little Lies", "author": "Liane Moriarty", "genre": "Mystery", "published_year": 2014, "reading_status": "To Read", "rating": None, "review": None, "summary": None},

    # Classics
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Classics", "published_year": 1960, "reading_status": "Completed", "rating": 5, "review": "Beautifully written, morally powerful.", "summary": "Scout Finch, a young girl in Maycomb, Alabama, witnesses her lawyer father Atticus defend a Black man falsely accused of rape."},
    {"title": "1984", "author": "George Orwell", "genre": "Classics", "published_year": 1949, "reading_status": "Completed", "rating": 5, "review": "More relevant than ever.", "summary": "Winston Smith struggles against the totalitarian regime of Big Brother in a dystopian superstate."},
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Classics", "published_year": 1925, "reading_status": "Completed", "rating": 4, "review": "Brilliant critique of the American Dream.", "summary": "The mysterious millionaire Jay Gatsby attempts to reunite with his former lover, Daisy Buchanan, in Jazz Age Long Island."},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Classics", "published_year": 1813, "reading_status": "To Read", "rating": None, "review": None, "summary": None},
    {"title": "Brave New World", "author": "Aldous Huxley", "genre": "Classics", "published_year": 1932, "reading_status": "Completed", "rating": 4, "review": "Chilling vision of a genetically engineered future.", "summary": "An exploration of a future society driven by cloning, conditioning, and soma, a state-provided drug."},
    {"title": "Fahrenheit 451", "author": "Ray Bradbury", "genre": "Classics", "published_year": 1953, "reading_status": "Completed", "rating": 5, "review": "A love letter to literature and critical thinking.", "summary": "Guy Montag, a firefighter whose job is to burn books, meets a young girl who opens his eyes to the beauty of literature."},
    {"title": "Crime and Punishment", "author": "Fyodor Dostoevsky", "genre": "Classics", "published_year": 1866, "reading_status": "Reading", "rating": None, "review": None, "summary": None},
    {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "genre": "Classics", "published_year": 1951, "reading_status": "Completed", "rating": 3, "review": "Relatable angst, though Holden can be quite annoying.", "summary": "Holden Caulfield, a teenager expelled from his prep school, wanders New York City reflecting on phoniness and growth."}
]

def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Check if books already exist
        statement = select(Book)
        results = session.exec(statement)
        if results.first() is None:
            # Seed the database
            for book_data in SEED_BOOKS:
                book = Book(**book_data)
                session.add(book)
            session.commit()
