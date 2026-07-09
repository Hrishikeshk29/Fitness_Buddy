"""
=============================================================================
FITNESS BUDDY - DATABASE MODELS
=============================================================================
SQLAlchemy ORM models for all application entities.
"""

from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ---------------------------------------------------------------------------
# User model
# ---------------------------------------------------------------------------
class User(UserMixin, db.Model):
    """Primary user / profile entity."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Personal info
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))          # Male | Female | Other
    height = db.Column(db.Float)               # cm
    weight = db.Column(db.Float)               # kg
    target_weight = db.Column(db.Float)        # kg

    # Fitness profile
    fitness_goal = db.Column(db.String(60))    # weight_loss | muscle_gain | …
    fitness_level = db.Column(db.String(30))   # beginner | intermediate | advanced
    dietary_preference = db.Column(db.String(30))  # vegetarian | non_vegetarian
    daily_activity_level = db.Column(db.String(40))
    available_workout_time = db.Column(db.Integer)  # minutes

    # Family support
    profile_type = db.Column(db.String(20), default="self")  # self|parent|child|spouse
    parent_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    workout_logs = db.relationship("WorkoutLog", backref="user", lazy=True, cascade="all, delete-orphan")
    habit_logs = db.relationship("HabitLog", backref="user", lazy=True, cascade="all, delete-orphan")
    progress_records = db.relationship("ProgressRecord", backref="user", lazy=True, cascade="all, delete-orphan")
    ai_recommendations = db.relationship("AIRecommendation", backref="user", lazy=True, cascade="all, delete-orphan")
    chat_history = db.relationship("ChatMessage", backref="user", lazy=True, cascade="all, delete-orphan")
    family_members = db.relationship("User", backref=db.backref("parent", remote_side=[id]), lazy=True)

    # ------------------------------------------------------------------
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def bmi(self) -> float | None:
        if self.height and self.weight and self.height > 0:
            return round(self.weight / ((self.height / 100) ** 2), 1)
        return None

    @property
    def bmi_category(self) -> str:
        b = self.bmi
        if b is None:
            return "Unknown"
        if b < 18.5:
            return "Underweight"
        if b < 25:
            return "Normal weight"
        if b < 30:
            return "Overweight"
        return "Obese"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
            "target_weight": self.target_weight,
            "fitness_goal": self.fitness_goal,
            "fitness_level": self.fitness_level,
            "dietary_preference": self.dietary_preference,
            "daily_activity_level": self.daily_activity_level,
            "available_workout_time": self.available_workout_time,
            "bmi": self.bmi,
            "bmi_category": self.bmi_category,
            "profile_type": self.profile_type,
        }


# ---------------------------------------------------------------------------
# Workout Log
# ---------------------------------------------------------------------------
class WorkoutLog(db.Model):
    __tablename__ = "workout_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    workout_completed = db.Column(db.Boolean, default=False)
    workout_type = db.Column(db.String(80))
    duration = db.Column(db.Integer)          # minutes
    calories_burned = db.Column(db.Integer)
    notes = db.Column(db.Text)
    date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "workout_completed": self.workout_completed,
            "workout_type": self.workout_type,
            "duration": self.duration,
            "calories_burned": self.calories_burned,
            "notes": self.notes,
            "date": self.date.isoformat() if self.date else None,
        }


# ---------------------------------------------------------------------------
# Habit Log
# ---------------------------------------------------------------------------
class HabitLog(db.Model):
    __tablename__ = "habit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    water_intake = db.Column(db.Float, default=0.0)    # litres
    sleep_hours = db.Column(db.Float, default=0.0)
    steps_count = db.Column(db.Integer, default=0)
    mood = db.Column(db.String(20))
    date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "water_intake": self.water_intake,
            "sleep_hours": self.sleep_hours,
            "steps_count": self.steps_count,
            "mood": self.mood,
            "date": self.date.isoformat() if self.date else None,
        }


# ---------------------------------------------------------------------------
# Progress Record
# ---------------------------------------------------------------------------
class ProgressRecord(db.Model):
    __tablename__ = "progress_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    weight = db.Column(db.Float)
    bmi = db.Column(db.Float)
    body_fat_pct = db.Column(db.Float)
    chest = db.Column(db.Float)    # cm
    waist = db.Column(db.Float)    # cm
    hips = db.Column(db.Float)     # cm
    notes = db.Column(db.Text)
    date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "weight": self.weight,
            "bmi": self.bmi,
            "date": self.date.isoformat() if self.date else None,
        }


# ---------------------------------------------------------------------------
# AI Recommendation
# ---------------------------------------------------------------------------
class AIRecommendation(db.Model):
    __tablename__ = "ai_recommendations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    agent_name = db.Column(db.String(60))
    recommendation = db.Column(db.Text)
    category = db.Column(db.String(40))     # workout | nutrition | motivation | habit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "recommendation": self.recommendation,
            "category": self.category,
            "created_at": self.created_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Family Analytics
# ---------------------------------------------------------------------------
class FamilyAnalytics(db.Model):
    """Stores computed analytics for each family member (updated on demand)."""

    __tablename__ = "family_analytics"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # head of family
    member_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    fitness_score = db.Column(db.Float, default=0.0)       # 0–100
    workout_completion_rate = db.Column(db.Float, default=0.0)  # 0–100 %
    goal_progress_pct = db.Column(db.Float, default=0.0)   # 0–100 %
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    member = db.relationship("User", foreign_keys=[member_id])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "member_id": self.member_id,
            "fitness_score": self.fitness_score,
            "workout_completion_rate": self.workout_completion_rate,
            "goal_progress_pct": self.goal_progress_pct,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# ---------------------------------------------------------------------------
# Chat Message
# ---------------------------------------------------------------------------
class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(10))   # user | assistant
    content = db.Column(db.Text)
    agent_used = db.Column(db.String(60))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "agent_used": self.agent_used,
            "created_at": self.created_at.isoformat(),
        }
