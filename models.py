from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base  # Base should be from your `database.py`

# ---------- User Model ----------
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_registered = Column(Boolean, default=True)
    search_count = Column(Integer, default=0)
    last_search_date = Column(Date, nullable=True)

    # Relationship to SearchHistory
    searches = relationship('SearchHistory', back_populates='user')


# ---------- Recipe Model ----------
class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    ingredients = Column(Text, nullable=False)
    instruction = Column(Text, nullable=False)
    calories = Column(String(50), nullable=True)


# ---------- Search History Model ----------
class SearchHistory(Base):
    __tablename__ = 'search_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    query = Column(String(255), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Back-reference to User
    user = relationship('User', back_populates='searches')


# ---------- Health Tip Model ----------
class HealthTip(Base):
    __tablename__ = 'health_tips'

    tip_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    tip_type = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
