from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, date, timedelta, timezone
from models import User, Recipe, SearchHistory, HealthTip
from database import engine, SessionLocal
from functools import lru_cache
import models

app = Flask(__name__)
app.secret_key = "your_very_secret_key"

# Create tables
models.Base.metadata.create_all(bind=engine)

# Cache recipes and tips for performance
@lru_cache(maxsize=128)
def get_cached_recipes():
    db = SessionLocal()
    recipes = db.query(Recipe).all()
    db.close()
    return recipes

@lru_cache(maxsize=128)
def get_cached_tips():
    db = SessionLocal()
    tips = db.query(HealthTip).all()
    db.close()
    return tips

def get_ip():
    return request.remote_addr

@app.route('/')
def home():
    return render_template('index.html',
        results=[],
        health_tips=[],
        history=[],
        query='',
        page=1,
        total_pages=1,
        total_results=0,
        total_tips=0,
        show_count=False
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    db = SessionLocal()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if db.query(User).filter_by(email=email).first():
            flash('User already exists. Please log in.', 'error')
            return redirect(url_for('login'))

        new_user = User(
            username=username,
            email=email,
            password=password,
            is_registered=True,
            search_count=0,
            last_search_date=date.today()
        )
        db.add(new_user)
        db.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    db = SessionLocal()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = db.query(User).filter_by(email=email).first()
        if user and user.password == password:
            session['user'] = user.username
            session['user_id'] = user.id
            flash('Successfully logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/search')
def search():
    db = SessionLocal()
    query = request.args.get('query', '').strip().lower()
    results = []
    health_tips = []
    history = []
    today = date.today()

    try:
        if 'user_id' in session:
            user = db.query(User).filter_by(id=session['user_id']).first()

            if user.last_search_date != today:
                user.search_count = 0
                user.last_search_date = today

            if user.search_count >= 20:
                flash("Registered users can only search 20 times per day.", "error")
                return redirect(url_for('home'))

            user.search_count += 1
            db.commit()

            if query:
                all_recipes = get_cached_recipes()
                all_tips = get_cached_tips()

                results = [r for r in all_recipes if query in r.title.lower()]
                health_tips = [t for t in all_tips if query in t.title.lower() or query in t.content.lower()]

                now_utc = datetime.now(timezone.utc)
                db.add(SearchHistory(
                    user_id=user.id,
                    query=query,
                    timestamp=now_utc
                ))
                db.commit()

            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            history = db.query(SearchHistory).filter(
                SearchHistory.user_id == user.id,
                SearchHistory.timestamp >= seven_days_ago
            ).order_by(SearchHistory.timestamp.desc()).all()

        else:
            ip = get_ip()
            guest = db.query(User).filter_by(email=ip, is_registered=False).first()

            if not guest:
                guest = User(
                    username="Unknown",
                    email=ip,
                    password="unknown",
                    is_registered=False,
                    search_count=0,
                    last_search_date=today
                )
                db.add(guest)
                db.commit()

            if guest.last_search_date != today:
                guest.search_count = 0
                guest.last_search_date = today
                db.commit()

            if guest.search_count >= 10:
                flash("You’ve reached the limit of 10 searches today. Please login.", "error")
                return redirect(url_for('login'))

            guest.search_count += 1
            db.commit()

            if query:
                all_recipes = get_cached_recipes()
                all_tips = get_cached_tips()
                results = [r for r in all_recipes if query in r.title.lower()]
                health_tips = [t for t in all_tips if query in t.title.lower() or query in t.content.lower()]

        # Pagination logic
        page = int(request.args.get('page', 1))
        per_page = 3

        total_results = len(results)
        total_tips = len(health_tips)

        start = (page - 1) * per_page
        end = start + per_page

        paginated_results = results[start:end]
        paginated_tips = health_tips[start:end]

        total_pages = max((max(total_results, total_tips) + per_page - 1) // per_page, 1)

        return render_template("index.html", 
            query=query,
            results=paginated_results,
            health_tips=paginated_tips,
            history=history,
            page=page,
            total_pages=total_pages,
            total_results=total_results,
            total_tips=total_tips,
            show_count=True
        )

    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        print("Search error:", e)
        return redirect(url_for('home'))

    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)
