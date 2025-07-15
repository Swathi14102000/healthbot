from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta, timezone
from models import User, Recipe, SearchHistory
from database import engine, SessionLocal
from functools import lru_cache

import models
from database import SessionLocal
from functools import lru_cache

app = Flask(__name__)
app.secret_key = "your_very_secret_key"

# Create tables

models.Base.metadata.create_all(bind=engine)



def get_ip():
    return request.remote_addr

@app.route('/')
def home():
    return render_template('index.html', results=None)

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
    session.pop('user', None)
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Cache recipe list
@lru_cache(maxsize=128)
def get_cached_recipes():
    db = SessionLocal()
    recipes = db.query(Recipe).all()
    db.close()
    return recipes

@app.route('/search')
def search():
    db = SessionLocal()
    query = request.args.get('query', '').strip().lower()
    results = []
    history = []
    today = date.today()

    try:
        if 'user_id' in session:
            user = db.query(User).filter_by(id=session['user_id']).first()

            # Reset daily search limit
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
                results = [r for r in all_recipes if query in r.title.lower()]
                all_titles = ', '.join([r.title for r in results])

                # Save history immediately without 10-second check
                now_utc = datetime.now(timezone.utc)
                history_entry = SearchHistory(
                    user_id=user.id,
                    query=query,
                    result=f"{len(results)} result(s) found",
                    all_recipes=all_titles,
                    timestamp=now_utc
                )
                db.add(history_entry)
                db.commit()

            # Fetch history for sidebar
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            history = db.query(SearchHistory).filter(
                SearchHistory.user_id == user.id,
                SearchHistory.timestamp >= seven_days_ago
            ).order_by(SearchHistory.timestamp.desc()).all()

        else:
            # Guest logic
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
                results = [r for r in all_recipes if query in r.title.lower()]

        return render_template('index.html', results=results, query=query, history=history)

    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('home'))

    finally:
        db.close()

@app.route('/history')
def history():
    db = SessionLocal()
    try:
        if 'user_id' in session:
            # Use timezone-aware UTC
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            history_data = db.query(SearchHistory).filter(
                SearchHistory.user_id == session['user_id'],
                SearchHistory.timestamp >= seven_days_ago
            ).order_by(SearchHistory.timestamp.desc()).all()
        else:
            history_data = []

        return render_template('history.html', history=history_data)

    finally:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
