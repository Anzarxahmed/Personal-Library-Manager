import streamlit as st
import httpx
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# Set Page Config
st.set_page_config(
    page_title="Personal Library Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Premium Custom CSS Injection for Glassmorphism & Sleek Design
st.markdown("""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Background styling */
    .stApp {
        background: linear-gradient(135deg, #0f0c20 0%, #15102a 50%, #06020f 100%);
        color: #e2e8f0;
    }

    /* Glassmorphic Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(139, 92, 246, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(139, 92, 246, 0.15);
    }

    /* Vibrant Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #8b5cf6 0%, #d946ef 100%);
        border: none;
        color: white;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
        transition: all 0.2s;
    }

    .stButton>button:hover {
        transform: scale(1.03);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.5);
    }

    /* Headers and Text gradients */
    .hero-text {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #f3e8ff;
        margin-bottom: 20px;
        border-bottom: 2px solid #8b5cf6;
        padding-bottom: 8px;
        display: inline-block;
    }

    /* Metric displays */
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #d946ef;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Rating Stars */
    .stars {
        color: #f59e0b;
        font-size: 1.2rem;
    }
    
    /* Status badges */
    .badge-completed {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-reading {
        background-color: rgba(59, 130, 246, 0.15);
        color: #3b82f6;
        border: 1px solid #3b82f6;
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-toread {
        background-color: rgba(107, 114, 128, 0.15);
        color: #9ca3af;
        border: 1px solid #9ca3af;
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to query FastAPI
def query_api(method: str, path: str, json_data: dict = None, params: dict = None):
    try:
        url = f"{API_URL}{path}"
        if method == "GET":
            response = httpx.get(url, params=params, timeout=10.0)
        elif method == "POST":
            response = httpx.post(url, json=json_data, timeout=15.0)
        elif method == "PUT":
            response = httpx.put(url, json=json_data, timeout=10.0)
        elif method == "DELETE":
            response = httpx.delete(url, timeout=10.0)
        
        if response.status_code in [200, 201]:
            return response.json(), response.headers
        else:
            st.error(f"Error {response.status_code}: {response.text}")
            return None, None
    except Exception as e:
        st.error(f"Failed to connect to backend API: {e}")
        return None, None

# Test Connection to Backend
backend_online = False
try:
    health_check = httpx.get(f"{API_URL}/", timeout=1.0)
    if health_check.status_code == 200:
        backend_online = True
except Exception:
    pass

if not backend_online:
    st.warning("⚠️ **Backend connection offline!** Please start your backend using: `uvicorn main:app --reload` to interact with this application.")

# App Header
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown('<div class="hero-text">Personal Library Manager</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; font-size:1.1rem;'>Track your books, view library intelligence, and generate AI recommendations & summaries.</p>", unsafe_allow_html=True)
with col2:
    status_color = "#10b981" if backend_online else "#ef4444"
    status_text = "API Online" if backend_online else "API Offline"
    st.markdown(f"""
        <div style='text-align:right; margin-top:25px;'>
            <span style='background-color:{status_color}20; color:{status_color}; border: 1px solid {status_color}; border-radius:20px; padding: 6px 12px; font-weight:bold; font-size:0.9rem;'>
                ● {status_text}
            </span>
        </div>
    """, unsafe_allow_html=True)

# Navigation
menu = ["📊 Dashboard & Analytics", "📖 My Library", "➕ Add New Book", "🤖 AI Assistant"]
choice = st.sidebar.radio("Navigation Menu", menu)

# --- DASHBOARD & ANALYTICS ---
if choice == "📊 Dashboard & Analytics":
    st.markdown('<div class="section-header">Library Dashboard</div>', unsafe_allow_html=True)
    
    if backend_online:
        stats, _ = query_api("GET", "/books/stats")
        if stats:
            # Stats Cards
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                    <div class="glass-card" style="text-align: center;">
                        <div class="metric-value">{stats['total_books']}</div>
                        <div class="metric-label">Total Books</div>
                    </div>
                """, unsafe_allow_html=True)
            with c2:
                completed = stats['status_counts'].get('Completed', 0)
                st.markdown(f"""
                    <div class="glass-card" style="text-align: center;">
                        <div class="metric-value" style="color:#10b981;">{completed}</div>
                        <div class="metric-label">Books Completed</div>
                    </div>
                """, unsafe_allow_html=True)
            with c3:
                reading = stats['status_counts'].get('Reading', 0)
                st.markdown(f"""
                    <div class="glass-card" style="text-align: center;">
                        <div class="metric-value" style="color:#3b82f6;">{reading}</div>
                        <div class="metric-label">Books Reading</div>
                    </div>
                """, unsafe_allow_html=True)
            with c4:
                avg_r = stats['average_rating'] or 0.0
                st.markdown(f"""
                    <div class="glass-card" style="text-align: center;">
                        <div class="metric-value" style="color:#f59e0b;">★ {avg_r}</div>
                        <div class="metric-label">Avg Rating</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Charts
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("### Reading Progress")
                status_df = pd.DataFrame(list(stats['status_counts'].items()), columns=['Status', 'Count'])
                if not status_df.empty:
                    st.bar_chart(status_df.set_index('Status'))
                else:
                    st.info("No reading status data available.")
                    
            with col_chart2:
                st.markdown("### Genre Distribution")
                genre_df = pd.DataFrame(list(stats['genre_counts'].items()), columns=['Genre', 'Count'])
                if not genre_df.empty:
                    st.bar_chart(genre_df.set_index('Genre'))
                else:
                    st.info("No genre data available.")
                    
            # Fun Statistics
            st.markdown("### 💡 Library Insights")
            if stats['total_books'] > 0:
                most_popular_genre = max(stats['genre_counts'], key=stats['genre_counts'].get)
                st.write(f"👉 Your library leans heavily towards **{most_popular_genre}** ({stats['genre_counts'][most_popular_genre]} books).")
                if completed > 0:
                    completion_rate = (completed / stats['total_books']) * 100
                    st.write(f"👉 You have read **{completion_rate:.1f}%** of your library's books!")
            else:
                st.info("Add some books to see insights!")
    else:
        st.info("Start the API server to view dashboard stats.")

# --- MY LIBRARY ---
elif choice == "📖 My Library":
    st.markdown('<div class="section-header">My Book Collection</div>', unsafe_allow_html=True)
    
    if backend_online:
        # Search & Filter controls
        search_col, filter_col = st.columns([2, 1])
        with search_col:
            search_query = st.text_input("🔍 Search books by title, author, or genre...")
        with filter_col:
            filter_status = st.selectbox("Filter by Status", ["All", "To Read", "Reading", "Completed"])
            
        # Fetch data based on search/filter
        books = []
        if search_query:
            books, _ = query_api("GET", "/books/search", params={"q": search_query})
        elif filter_status != "All":
            books, _ = query_api("GET", f"/books/status/{filter_status}")
        else:
            books, _ = query_api("GET", "/books")
            
        if books:
            # Render Books as grid
            for i in range(0, len(books), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(books):
                        book = books[i + j]
                        with cols[j]:
                            # Status badge color
                            status = book.get("reading_status", "To Read")
                            badge_class = "badge-toread"
                            if status == "Completed":
                                badge_class = "badge-completed"
                            elif status == "Reading":
                                badge_class = "badge-reading"
                                
                            rating_stars = "★" * book["rating"] if book.get("rating") else "Unrated"
                            
                            st.markdown(f"""
                                <div class="glass-card">
                                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                        <span class="{badge_class}">{status}</span>
                                        <span style="color:#f59e0b; font-weight:bold;">{rating_stars}</span>
                                    </div>
                                    <h3 style="margin-top:0; margin-bottom:4px; font-weight:700; color:#fff;">{book['title']}</h3>
                                    <p style="color:#94a3b8; font-style:italic; margin-bottom:8px;">by {book['author']}</p>
                                    <p style="font-size:0.9rem; color:#cbd5e1; margin-bottom:12px;">
                                        <b>Genre:</b> {book['genre']} | <b>Year:</b> {book['published_year'] or 'N/A'}
                                    </p>
                                    <p style="font-size:0.95rem; color:#a78bfa; margin-bottom:16px;">
                                        "{book['review'] or 'No review written yet.'}"
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Action expansions inside container
                            with st.expander(f"Edit/Delete: {book['title']}"):
                                edit_status = st.selectbox("Status", ["To Read", "Reading", "Completed"], index=["To Read", "Reading", "Completed"].index(status), key=f"status_{book['id']}")
                                edit_rating = st.slider("Rating (1-5)", 1, 5, value=book["rating"] or 3, key=f"rating_{book['id']}")
                                edit_review = st.text_area("Review", value=book["review"] or "", key=f"review_{book['id']}")
                                
                                c_save, c_del = st.columns(2)
                                with c_save:
                                    if st.button("Save Changes", key=f"save_{book['id']}"):
                                        payload = {
                                            "reading_status": edit_status,
                                            "rating": edit_rating if edit_status == "Completed" else None,
                                            "review": edit_review
                                        }
                                        updated, _ = query_api("PUT", f"/books/{book['id']}", json_data=payload)
                                        if updated:
                                            st.success("Updated successfully!")
                                            st.rerun()
                                with c_del:
                                    if st.button("🚨 Delete Book", key=f"del_{book['id']}"):
                                        deleted, _ = query_api("DELETE", f"/books/{book['id']}")
                                        if deleted:
                                            st.success("Deleted successfully!")
                                            st.rerun()
        else:
            st.info("No books found matching criteria.")
    else:
        st.info("Offline: Start backend server.")

# --- ADD NEW BOOK ---
elif choice == "➕ Add New Book":
    st.markdown('<div class="section-header">Add Book to Library</div>', unsafe_allow_html=True)
    
    if backend_online:
        with st.form("new_book_form"):
            title = st.text_input("Book Title *")
            author = st.text_input("Author *")
            genre = st.selectbox("Genre", ["Fantasy", "Sci-Fi", "Programming", "Self Help", "History", "Biography", "Mystery", "Thriller", "Classics", "Other"])
            custom_genre = st.text_input("Custom Genre (if 'Other' selected)")
            published_year = st.number_input("Published Year", min_value=0, max_value=2030, value=2024)
            reading_status = st.selectbox("Reading Status", ["To Read", "Reading", "Completed"])
            
            # Show rating slider only if completed
            rating = None
            if reading_status == "Completed":
                rating = st.slider("Rating (1-5)", 1, 5, 5)
                
            review = st.text_area("Personal Review / Notes")
            
            submitted = st.form_submit_button("Add Book")
            
            if submitted:
                if not title or not author:
                    st.error("Title and Author are required fields!")
                else:
                    final_genre = custom_genre if genre == "Other" and custom_genre else genre
                    payload = {
                        "title": title,
                        "author": author,
                        "genre": final_genre,
                        "published_year": int(published_year) if published_year > 0 else None,
                        "reading_status": reading_status,
                        "rating": rating,
                        "review": review if review.strip() else None
                    }
                    
                    res, _ = query_api("POST", "/books", json_data=payload)
                    if res:
                        st.success(f"🎉 '{title}' was successfully added to your library!")
    else:
        st.info("Start API backend to add books.")

# --- AI ASSISTANT ---
elif choice == "🤖 AI Assistant":
    st.markdown('<div class="section-header">AI-Powered Librarian</div>', unsafe_allow_html=True)
    
    tab_rec, tab_sum = st.tabs(["💡 Smart Recommendations", "📝 Auto-Summarizer"])
    
    with tab_rec:
        st.write("Enter a genre to receive 3 personalized book suggestions from the Groq LLM agent.")
        rec_genre = st.text_input("Target Genre (e.g., Sci-Fi, Fantasy, Psychology, Business)", "Sci-Fi")
        
        if st.button("Generate Recommendations"):
            if rec_genre:
                with st.spinner("Consulting AI Librarian..."):
                    rec_payload = {"genre": rec_genre}
                    data, headers = query_api("POST", "/books/ai/recommend", json_data=rec_payload)
                    
                    if data:
                        # Determine AI Source header
                        source = headers.get("x-ai-source", "unknown")
                        if source == "groq":
                            st.caption("⚡ recommendations generated in real-time by Groq Llama 3.")
                        else:
                            st.caption("ℹ️ Demo Mode: Showing pre-packaged recommendations (Groq API Key not configured).")
                            
                        # Display recommendations
                        for item in data.get("recommendations", []):
                            st.markdown(f"""
                                <div class="glass-card">
                                    <h4 style="margin:0; color:#c084fc; font-weight:700;">{item['title']}</h4>
                                    <p style="color:#94a3b8; font-style:italic; margin-bottom:8px;">by {item['author']}</p>
                                    <p style="color:#e2e8f0; font-size:0.95rem; line-height:1.4;">{item['reason']}</p>
                                </div>
                            """, unsafe_allow_html=True)
            else:
                st.error("Please provide a genre.")
                
    with tab_sum:
        st.write("Generate a brief, spoiler-free AI summary of any book title.")
        
        # Populate selector if online
        book_titles = []
        if backend_online:
            books, _ = query_api("GET", "/books")
            if books:
                book_titles = [b["title"] for b in books]
                
        # Allow selecting from existing or writing custom
        summary_source = st.radio("Choose source:", ["Select from Library", "Input Custom Title"])
        
        if summary_source == "Select from Library" and book_titles:
            sum_title = st.selectbox("Select a book from your library", book_titles)
        else:
            sum_title = st.text_input("Enter Book Title to Summarize (e.g. 'Dune', 'Atomic Habits')", "Dune")
            
        if st.button("Generate Summary"):
            if sum_title:
                with st.spinner("Reading book and drafting summary..."):
                    sum_payload = {"title": sum_title}
                    data, headers = query_api("POST", "/books/ai/summary", json_data=sum_payload)
                    
                    if data:
                        source = headers.get("x-ai-source", "unknown")
                        if source == "db_cache":
                            st.caption("📁 Loaded from cached database summaries.")
                        elif source == "groq":
                            st.caption("⚡ Summary generated in real-time by Groq Llama 3 and cached.")
                        else:
                            st.caption("ℹ️ Demo Mode: Showing cached/mock summary (Groq API Key not configured).")
                            
                        st.markdown(f"""
                            <div class="glass-card">
                                <h3 style="margin-top:0; color:#fff; font-weight:700;">{data['title']}</h3>
                                <p style="font-size:1.05rem; line-height:1.5; color:#e2e8f0; font-style:italic;">
                                    "{data['summary']}"
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("Please provide a book title.")
