"""
=============================================================================
FITNESS BUDDY - MAIN APPLICATION ROUTES
=============================================================================
Handles dashboard, profile, habit logging, progress tracking, and analytics.
All data-fetching routes use get_active_member() so every family profile
gets its own independent dashboard, logs and analytics.
"""

from datetime import date, timedelta, datetime
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, jsonify, session
)
from flask_login import login_required, current_user
from sqlalchemy import func

from models.models import db, User, WorkoutLog, HabitLog, ProgressRecord, AIRecommendation
from services.member_context import get_active_member, get_family_roster, set_active_member

main_bp = Blueprint("main", __name__)


# ---------------------------------------------------------------------------
# Landing Page
# ---------------------------------------------------------------------------
@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Profile Switcher  (POST + GET)
# ---------------------------------------------------------------------------
@main_bp.route("/switch-member", methods=["POST", "GET"])
@login_required
def switch_member():
    mid = request.form.get("member_id", type=int) or request.args.get("member_id", type=int)
    if mid:
        set_active_member(mid)
    next_page = request.form.get("next") or request.args.get("next") or url_for("main.dashboard")
    return redirect(next_page)


# ---------------------------------------------------------------------------
# Member Dashboard  /member/<id>/dashboard
# ---------------------------------------------------------------------------
@main_bp.route("/member/<int:member_id>/dashboard")
@login_required
def member_dashboard(member_id: int):
    """Load dashboard for any family member by switching active context."""
    if set_active_member(member_id):
        return redirect(url_for("main.dashboard"))
    flash("Family member not found.", "danger")
    return redirect(url_for("main.dashboard"))


# ---------------------------------------------------------------------------
# Member-specific logging endpoints
# ---------------------------------------------------------------------------
@main_bp.route("/member/<int:member_id>/log-workout", methods=["POST"])
@login_required
def member_log_workout(member_id: int):
    member = User.query.filter(
        User.id == member_id,
        db.or_(User.id == current_user.id, User.parent_id == current_user.id)
    ).first_or_404()
    log = WorkoutLog(
        user_id=member.id,
        workout_completed=True,
        workout_type=request.form.get("workout_type", "General"),
        duration=request.form.get("duration", type=int, default=30),
        calories_burned=request.form.get("calories_burned", type=int, default=0),
        notes=request.form.get("notes", ""),
        date=date.today(),
    )
    db.session.add(log)
    db.session.commit()
    flash(f"Workout logged for {member.name}! 🔥", "success")
    return redirect(request.referrer or url_for("main.family"))


@main_bp.route("/member/<int:member_id>/log-habit", methods=["POST"])
@login_required
def member_log_habit(member_id: int):
    member = User.query.filter(
        User.id == member_id,
        db.or_(User.id == current_user.id, User.parent_id == current_user.id)
    ).first_or_404()
    today = date.today()
    existing = HabitLog.query.filter_by(user_id=member.id, date=today).first()
    log = existing or HabitLog(user_id=member.id, date=today)
    if not existing:
        db.session.add(log)
    log.water_intake = request.form.get("water_intake", type=float, default=0.0)
    log.sleep_hours  = request.form.get("sleep_hours",  type=float, default=0.0)
    log.steps_count  = request.form.get("steps_count",  type=int,   default=0)
    log.mood         = request.form.get("mood", "good")
    db.session.commit()
    flash(f"Habits logged for {member.name}! 💧", "success")
    return redirect(request.referrer or url_for("main.family"))


@main_bp.route("/member/<int:member_id>/log-progress", methods=["POST"])
@login_required
def member_log_progress(member_id: int):
    member = User.query.filter(
        User.id == member_id,
        db.or_(User.id == current_user.id, User.parent_id == current_user.id)
    ).first_or_404()
    weight = request.form.get("weight", type=float)
    if not weight:
        flash("Please enter a weight value.", "warning")
        return redirect(request.referrer or url_for("main.family"))
    member.weight = weight
    height = member.height
    bmi = round(weight / ((height / 100) ** 2), 1) if height else None
    db.session.add(ProgressRecord(
        user_id=member.id, weight=weight, bmi=bmi,
        waist=request.form.get("waist", type=float),
        notes=request.form.get("notes", ""),
        date=date.today(),
    ))
    db.session.commit()
    flash(f"Progress updated for {member.name}! 📈", "success")
    return redirect(request.referrer or url_for("main.family"))


# ---------------------------------------------------------------------------
# Profile Setup
# ---------------------------------------------------------------------------
@main_bp.route("/setup-profile", methods=["GET", "POST"])
@login_required
def setup_profile():
    if request.method == "POST":
        current_user.age = request.form.get("age", type=int)
        current_user.gender = request.form.get("gender")
        current_user.height = request.form.get("height", type=float)
        current_user.weight = request.form.get("weight", type=float)
        current_user.target_weight = request.form.get("target_weight", type=float)
        current_user.fitness_goal = request.form.get("fitness_goal")
        current_user.fitness_level = request.form.get("fitness_level")
        current_user.dietary_preference = request.form.get("dietary_preference")
        current_user.daily_activity_level = request.form.get("daily_activity_level")
        current_user.available_workout_time = request.form.get(
            "available_workout_time", type=int, default=30
        )

        # Save initial progress record
        if current_user.weight:
            record = ProgressRecord(
                user_id=current_user.id,
                weight=current_user.weight,
                bmi=current_user.bmi,
                date=date.today(),
            )
            db.session.add(record)

        db.session.commit()
        flash("Profile saved! Your personalised fitness journey begins now. 🚀", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("profile/setup.html")


@main_bp.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.name = request.form.get("name", current_user.name).strip()
        current_user.age = request.form.get("age", type=int)
        current_user.gender = request.form.get("gender")
        current_user.height = request.form.get("height", type=float)
        current_user.weight = request.form.get("weight", type=float)
        current_user.target_weight = request.form.get("target_weight", type=float)
        current_user.fitness_goal = request.form.get("fitness_goal")
        current_user.fitness_level = request.form.get("fitness_level")
        current_user.dietary_preference = request.form.get("dietary_preference")
        current_user.daily_activity_level = request.form.get("daily_activity_level")
        current_user.available_workout_time = request.form.get(
            "available_workout_time", type=int
        )
        db.session.commit()
        flash("Profile updated successfully! ✅", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("profile/edit.html")


# ---------------------------------------------------------------------------
# Dashboard  (member-context aware)
# ---------------------------------------------------------------------------
@main_bp.route("/dashboard")
@login_required
def dashboard():
    if not current_user.fitness_goal:
        return redirect(url_for("main.setup_profile"))

    # Resolve the active member (may be current_user or a family member)
    active = get_active_member()
    roster = get_family_roster()
    is_managing_other = active.id != current_user.id

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    # All stats use active member's user_id
    weekly_workouts = WorkoutLog.query.filter(
        WorkoutLog.user_id == active.id,
        WorkoutLog.date >= week_start,
        WorkoutLog.workout_completed == True,
    ).count()

    total_workouts = WorkoutLog.query.filter_by(
        user_id=active.id, workout_completed=True
    ).count()

    streak = _calculate_streak(active.id)

    today_habit = HabitLog.query.filter_by(
        user_id=active.id, date=today
    ).first()

    latest_progress = (
        ProgressRecord.query.filter_by(user_id=active.id)
        .order_by(ProgressRecord.date.desc())
        .first()
    )

    recent_recs = (
        AIRecommendation.query.filter_by(user_id=active.id)
        .order_by(AIRecommendation.created_at.desc())
        .limit(3)
        .all()
    )

    # Weight chart — seed from profile weight when no records exist
    weight_records = (
        ProgressRecord.query.filter_by(user_id=active.id)
        .order_by(ProgressRecord.date.asc())
        .limit(30)
        .all()
    )
    if weight_records:
        weight_chart_data = {
            "labels": [r.date.strftime("%b %d") for r in weight_records],
            "values": [r.weight for r in weight_records],
        }
    elif active.weight:
        weight_chart_data = {
            "labels": [today.strftime("%b %d")],
            "values": [active.weight],
        }
    else:
        weight_chart_data = {"labels": [], "values": []}

    # Weekly consistency
    weekly_days = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        log = WorkoutLog.query.filter_by(
            user_id=active.id, date=d, workout_completed=True
        ).first()
        weekly_days.append({"date": d.strftime("%a"), "done": bool(log)})

    return render_template(
        "dashboard/dashboard.html",
        user=active,               # active member's profile
        account_user=current_user, # always the logged-in account owner
        roster=roster,
        is_managing_other=is_managing_other,
        weekly_workouts=weekly_workouts,
        total_workouts=total_workouts,
        streak=streak,
        today_habit=today_habit,
        latest_progress=latest_progress,
        recent_recs=recent_recs,
        weight_chart_data=weight_chart_data,
        weekly_days=weekly_days,
        now_hour=datetime.now().hour,
    )


# ---------------------------------------------------------------------------
# Habit Logging  (active-member aware)
# ---------------------------------------------------------------------------
@main_bp.route("/log-habit", methods=["POST"])
@login_required
def log_habit():
    active = get_active_member()
    today = date.today()
    existing = HabitLog.query.filter_by(user_id=active.id, date=today).first()
    log = existing or HabitLog(user_id=active.id, date=today)
    if not existing:
        db.session.add(log)
    log.water_intake = request.form.get("water_intake", type=float, default=0.0)
    log.sleep_hours  = request.form.get("sleep_hours",  type=float, default=0.0)
    log.steps_count  = request.form.get("steps_count",  type=int,   default=0)
    log.mood         = request.form.get("mood", "good")
    db.session.commit()
    name = f"for {active.name}" if active.id != current_user.id else ""
    flash(f"Habit log updated {name}! Keep it consistent! 💧", "success")
    return redirect(url_for("main.dashboard"))


# ---------------------------------------------------------------------------
# Workout Logging  (active-member aware)
# ---------------------------------------------------------------------------
@main_bp.route("/log-workout", methods=["POST"])
@login_required
def log_workout():
    active = get_active_member()
    log = WorkoutLog(
        user_id=active.id,
        workout_completed=True,
        workout_type=request.form.get("workout_type", "General"),
        duration=request.form.get("duration", type=int, default=30),
        calories_burned=request.form.get("calories_burned", type=int, default=0),
        notes=request.form.get("notes", ""),
        date=date.today(),
    )
    db.session.add(log)
    db.session.commit()
    name = f"for {active.name}" if active.id != current_user.id else ""
    flash(f"Workout logged {name}! Amazing effort today! 🔥", "success")
    return redirect(url_for("main.dashboard"))


# ---------------------------------------------------------------------------
# Progress Recording  (active-member aware)
# ---------------------------------------------------------------------------
@main_bp.route("/log-progress", methods=["POST"])
@login_required
def log_progress():
    active = get_active_member()
    weight = request.form.get("weight", type=float)
    if not weight:
        flash("Please enter your current weight.", "warning")
        return redirect(url_for("main.dashboard"))
    active.weight = weight
    height = active.height
    bmi = round(weight / ((height / 100) ** 2), 1) if height else None
    db.session.add(ProgressRecord(
        user_id=active.id, weight=weight, bmi=bmi,
        waist=request.form.get("waist", type=float),
        notes=request.form.get("notes", ""),
        date=date.today(),
    ))
    db.session.commit()
    name = f"for {active.name}" if active.id != current_user.id else ""
    flash(f"Progress recorded {name}! You're making great strides! 📈", "success")
    return redirect(url_for("main.dashboard"))


# ---------------------------------------------------------------------------
# Analytics Page  (active-member aware)
# ---------------------------------------------------------------------------
@main_bp.route("/analytics")
@login_required
def analytics():
    active  = get_active_member()
    roster  = get_family_roster()
    is_managing_other = active.id != current_user.id

    thirty_ago = date.today() - timedelta(days=30)
    workout_logs = WorkoutLog.query.filter(
        WorkoutLog.user_id == active.id,
        WorkoutLog.date >= thirty_ago,
    ).order_by(WorkoutLog.date.asc()).all()

    habit_logs = HabitLog.query.filter(
        HabitLog.user_id == active.id,
        HabitLog.date >= thirty_ago,
    ).order_by(HabitLog.date.asc()).all()

    progress_records = ProgressRecord.query.filter_by(
        user_id=active.id
    ).order_by(ProgressRecord.date.asc()).all()

    total_workouts = len([w for w in workout_logs if w.workout_completed])
    total_duration = sum(w.duration or 0 for w in workout_logs if w.workout_completed)
    avg_water = (
        sum(h.water_intake or 0 for h in habit_logs) / len(habit_logs)
        if habit_logs else 0
    )
    avg_sleep = (
        sum(h.sleep_hours or 0 for h in habit_logs) / len(habit_logs)
        if habit_logs else 0
    )

    return render_template(
        "dashboard/analytics.html",
        user=active,
        account_user=current_user,
        roster=roster,
        is_managing_other=is_managing_other,
        workout_logs=workout_logs,
        habit_logs=habit_logs,
        progress_records=progress_records,
        progress_records_json=[r.to_dict() for r in progress_records],
        workout_logs_json=[w.to_dict() for w in workout_logs],
        habit_logs_json=[h.to_dict() for h in habit_logs],
        total_workouts=total_workouts,
        total_duration=total_duration,
        avg_water=round(avg_water, 1),
        avg_sleep=round(avg_sleep, 1),
    )


# ---------------------------------------------------------------------------
# Family Profiles + Health Dashboard
# ---------------------------------------------------------------------------
@main_bp.route("/family")
@login_required
def family():
    from models.models import WorkoutLog, HabitLog, ProgressRecord, FamilyAnalytics

    members = User.query.filter_by(parent_id=current_user.id).all()

    # Build enriched data for every family member (including the current user)
    all_members = [current_user] + members
    family_data = []
    thirty_ago = date.today() - timedelta(days=30)
    seven_ago  = date.today() - timedelta(days=7)

    for m in all_members:
        # Workout stats (last 30 days)
        w_logs = WorkoutLog.query.filter(
            WorkoutLog.user_id == m.id,
            WorkoutLog.date >= thirty_ago,
        ).all()
        completed = [w for w in w_logs if w.workout_completed]
        total_done = len(completed)
        completion_rate = round(total_done / max(len(w_logs), 1) * 100, 1) if w_logs else 0.0

        # Habit stats (last 7 days)
        h_logs = HabitLog.query.filter(
            HabitLog.user_id == m.id,
            HabitLog.date >= seven_ago,
        ).all()
        avg_water = round(sum(h.water_intake or 0 for h in h_logs) / max(len(h_logs), 1), 1) if h_logs else 0.0
        avg_sleep = round(sum(h.sleep_hours  or 0 for h in h_logs) / max(len(h_logs), 1), 1) if h_logs else 0.0

        # Streak
        streak = 0
        for i in range(30):
            d = date.today() - timedelta(days=i)
            if any(w.date == d and w.workout_completed for w in w_logs):
                streak += 1
            else:
                break

        # Progress records for weight chart
        p_recs = (
            ProgressRecord.query.filter_by(user_id=m.id)
            .order_by(ProgressRecord.date.asc())
            .limit(10)
            .all()
        )
        weight_history = [{"date": r.date.strftime("%b %d"), "weight": r.weight} for r in p_recs]
        if not weight_history and m.weight:
            weight_history = [{"date": date.today().strftime("%b %d"), "weight": m.weight}]

        # Fitness score: composite of BMI normalisation + completion + streak
        bmi = m.bmi or 25
        bmi_score = max(0, 100 - abs(bmi - 22) * 5)          # best at BMI 22
        fitness_score = round((bmi_score * 0.3 + completion_rate * 0.5 + min(streak * 5, 100) * 0.2), 1)

        # Goal progress: weight-based where applicable
        goal_pct = 0.0
        if m.weight and m.target_weight and m.weight != m.target_weight:
            initial = p_recs[0].weight if p_recs else m.weight
            total_needed = abs(initial - m.target_weight)
            achieved = abs(initial - m.weight)
            goal_pct = round(min(achieved / max(total_needed, 0.01) * 100, 100), 1)
        elif total_done > 0:
            goal_pct = min(total_done * 5, 100)

        # Persist / update FamilyAnalytics row
        fa = FamilyAnalytics.query.filter_by(
            owner_id=current_user.id, member_id=m.id
        ).first()
        if not fa:
            fa = FamilyAnalytics(owner_id=current_user.id, member_id=m.id)
            db.session.add(fa)
        fa.fitness_score = fitness_score
        fa.workout_completion_rate = completion_rate
        fa.goal_progress_pct = goal_pct

        family_data.append({
            "id": m.id,
            "name": m.name,
            "profile_type": m.profile_type or "self",
            "age": m.age,
            "gender": m.gender,
            "bmi": m.bmi,
            "bmi_category": m.bmi_category,
            "weight": m.weight,
            "target_weight": m.target_weight,
            "fitness_goal": m.fitness_goal or "general_fitness",
            "fitness_level": m.fitness_level or "beginner",
            "fitness_score": fitness_score,
            "workout_completion_rate": completion_rate,
            "goal_progress_pct": goal_pct,
            "avg_water": avg_water,
            "avg_sleep": avg_sleep,
            "streak": streak,
            "total_workouts": total_done,
            "weight_history": weight_history,
            "is_self": m.id == current_user.id,
        })

    db.session.commit()

    # Aggregate family stats
    valid_bmi    = [f["bmi"] for f in family_data if f["bmi"]]
    avg_bmi      = round(sum(valid_bmi) / len(valid_bmi), 1) if valid_bmi else 0.0
    avg_score    = round(sum(f["fitness_score"] for f in family_data) / len(family_data), 1)
    total_workouts_fam = sum(f["total_workouts"] for f in family_data)
    avg_water_fam = round(sum(f["avg_water"] for f in family_data) / len(family_data), 1)
    consistency  = round(sum(f["workout_completion_rate"] for f in family_data) / len(family_data), 1)
    active_goals = len([f for f in family_data if f["fitness_goal"] and f["fitness_goal"] != "general_fitness"])

    family_stats = {
        "member_count":   len(family_data),
        "avg_bmi":        avg_bmi,
        "avg_score":      avg_score,
        "total_workouts": total_workouts_fam,
        "avg_water":      avg_water_fam,
        "consistency":    consistency,
        "active_goals":   active_goals,
    }

    return render_template(
        "profile/family.html",
        members=members,
        family_data=family_data,
        family_stats=family_stats,
    )


@main_bp.route("/family/add", methods=["GET", "POST"])
@login_required
def add_family_member():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        profile_type = request.form.get("profile_type", "spouse")
        username = f"{current_user.username}_{profile_type}_{name.lower().replace(' ', '_')}"

        if User.query.filter_by(username=username).first():
            username = username + "_1"

        height = request.form.get("height", type=float)
        weight = request.form.get("weight", type=float)

        member = User(
            name=name,
            username=username,
            email=f"{username}@family.local",
            parent_id=current_user.id,
            profile_type=profile_type,
            age=request.form.get("age", type=int),
            gender=request.form.get("gender"),
            height=height,
            weight=weight,
            target_weight=request.form.get("target_weight", type=float),
            fitness_goal=request.form.get("fitness_goal", "general_fitness"),
            fitness_level=request.form.get("fitness_level", "beginner"),
            dietary_preference=request.form.get("dietary_preference", "vegetarian"),
            available_workout_time=request.form.get("available_workout_time", type=int, default=30),
        )
        member.set_password("family123")
        db.session.add(member)
        db.session.commit()

        # Seed initial progress record so BMI chart works immediately
        if weight and height:
            bmi = round(weight / ((height / 100) ** 2), 1)
            db.session.add(ProgressRecord(
                user_id=member.id, weight=weight, bmi=bmi, date=date.today()
            ))
            db.session.commit()

        flash(f"Family member {name} added! BMI: {member.bmi or '—'} 👨‍👩‍👧", "success")
        return redirect(url_for("main.family"))

    return render_template("profile/add_family.html")


# ---------------------------------------------------------------------------
# Edit Family Member
# ---------------------------------------------------------------------------
@main_bp.route("/family/edit/<int:member_id>", methods=["GET", "POST"])
@login_required
def edit_family_member(member_id: int):
    member = User.query.filter_by(id=member_id, parent_id=current_user.id).first_or_404()

    if request.method == "POST":
        member.name              = request.form.get("name", member.name).strip()
        member.age               = request.form.get("age", type=int)
        member.gender            = request.form.get("gender")
        member.height            = request.form.get("height", type=float)
        member.target_weight     = request.form.get("target_weight", type=float)
        member.fitness_goal      = request.form.get("fitness_goal")
        member.fitness_level     = request.form.get("fitness_level")
        member.dietary_preference= request.form.get("dietary_preference")
        member.available_workout_time = request.form.get("available_workout_time", type=int)
        member.profile_type      = request.form.get("profile_type", member.profile_type)

        # Update weight and add progress record if changed
        new_weight = request.form.get("weight", type=float)
        if new_weight and new_weight != member.weight:
            member.weight = new_weight
            height = member.height
            bmi = round(new_weight / ((height / 100) ** 2), 1) if height else None
            db.session.add(ProgressRecord(
                user_id=member.id, weight=new_weight, bmi=bmi, date=date.today()
            ))

        db.session.commit()
        flash(f"{member.name}'s profile updated! ✅", "success")
        return redirect(url_for("main.family"))

    return render_template("profile/edit_family.html", member=member)


# ---------------------------------------------------------------------------
# API – Dashboard Data
# ---------------------------------------------------------------------------
@main_bp.route("/api/dashboard-stats")
@login_required
def api_dashboard_stats():
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    streak = _calculate_streak(current_user.id)

    weekly_workouts = WorkoutLog.query.filter(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.date >= week_start,
        WorkoutLog.workout_completed == True,
    ).count()

    today_habit = HabitLog.query.filter_by(
        user_id=current_user.id, date=today
    ).first()

    return jsonify({
        "streak": streak,
        "weekly_workouts": weekly_workouts,
        "water_intake": today_habit.water_intake if today_habit else 0,
        "sleep_hours": today_habit.sleep_hours if today_habit else 0,
        "bmi": current_user.bmi,
        "bmi_category": current_user.bmi_category,
    })


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------
def _calculate_streak(user_id: int) -> int:
    """Calculate consecutive days with at least one completed workout."""
    streak = 0
    check_date = date.today()
    for _ in range(365):
        log = WorkoutLog.query.filter_by(
            user_id=user_id, date=check_date, workout_completed=True
        ).first()
        if log:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak
