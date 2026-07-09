"""
=============================================================================
FITNESS BUDDY - CHAT / AI ROUTES
=============================================================================
Exposes the conversational AI endpoints that power the chat interface.
All AI calls use the active family member context so every profile gets
personalised, independent AI coaching.
"""

from datetime import date, timedelta
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func

from models.models import db, WorkoutLog, HabitLog, ProgressRecord, AIRecommendation, ChatMessage
from agents.orchestrator_agent import OrchestratorAgent
from services.member_context import get_active_member, get_family_roster

chat_bp = Blueprint("chat", __name__)
orchestrator = OrchestratorAgent()


# ---------------------------------------------------------------------------
# Chat Page  (active-member aware)
# ---------------------------------------------------------------------------
@chat_bp.route("/chat")
@login_required
def chat():
    active  = get_active_member()
    roster  = get_family_roster()
    is_managing_other = active.id != current_user.id

    # Load chat history for the active member
    history = (
        ChatMessage.query.filter_by(user_id=active.id)
        .order_by(ChatMessage.created_at.asc())
        .limit(50)
        .all()
    )
    return render_template(
        "chat/chat.html",
        history=history,
        user=active,
        account_user=current_user,
        roster=roster,
        is_managing_other=is_managing_other,
    )


# ---------------------------------------------------------------------------
# Chat API  (active-member aware)
# ---------------------------------------------------------------------------
@chat_bp.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    active = get_active_member()

    # Build context objects from the active member
    user_data      = active.to_dict()
    habit_stats    = _get_habit_stats(active.id)
    progress_stats = _get_progress_stats(active.id)

    # Invoke orchestrator
    result = orchestrator.process(
        user_message=user_message,
        user_data=user_data,
        habit_stats=habit_stats,
        progress_stats=progress_stats,
    )

    response_text = result["response"]
    agents_used   = result["agents_used"]

    # Persist chat messages under the active member's id
    db.session.add(ChatMessage(
        user_id=active.id,
        role="user",
        content=user_message,
        agent_used=", ".join(agents_used),
    ))
    db.session.add(ChatMessage(
        user_id=active.id,
        role="assistant",
        content=response_text,
        agent_used=", ".join(agents_used),
    ))

    # Save AI recommendation under the active member
    db.session.add(AIRecommendation(
        user_id=active.id,
        agent_name=", ".join(agents_used),
        recommendation=response_text[:500],
        category=_infer_category(agents_used),
    ))
    db.session.commit()

    return jsonify({
        "response": response_text,
        "agents_used": agents_used,
        "reasoning": result.get("reasoning", ""),
        "active_member": active.name,
    })


# ---------------------------------------------------------------------------
# Quick AI Actions  (active-member aware)
# ---------------------------------------------------------------------------
@chat_bp.route("/api/quick-action", methods=["POST"])
@login_required
def quick_action():
    active = get_active_member()
    data   = request.get_json(silent=True) or {}
    action = data.get("action", "motivate")

    action_prompts = {
        "workout":  "Create a complete workout plan for me today based on my fitness level and goal.",
        "meal":     "Suggest a full day healthy Indian meal plan for my fitness goal.",
        "progress": "Analyse my fitness progress and tell me how I am doing.",
        "motivate": "Give me powerful motivation and encouragement to stay on track today.",
        "habit":    "Review my habits and give me tips to improve my consistency.",
    }
    message = action_prompts.get(action, "Give me personalised fitness advice.")

    user_data      = active.to_dict()
    habit_stats    = _get_habit_stats(active.id)
    progress_stats = _get_progress_stats(active.id)

    result = orchestrator.process(
        user_message=message,
        user_data=user_data,
        habit_stats=habit_stats,
        progress_stats=progress_stats,
    )

    return jsonify({
        "response": result["response"],
        "agents_used": result["agents_used"],
    })


# ---------------------------------------------------------------------------
# Weekly Report Generation
# ---------------------------------------------------------------------------
@chat_bp.route("/api/weekly-report", methods=["GET"])
@login_required
def weekly_report():
    progress_stats = _get_progress_stats(current_user.id)
    habit_stats = _get_habit_stats(current_user.id)
    user_data = current_user.to_dict()

    message = (
        "Generate a comprehensive weekly fitness performance report including "
        "workout completion, habit consistency, progress toward my goal, "
        "and recommendations for next week."
    )
    result = orchestrator.process(
        user_message=message,
        user_data=user_data,
        habit_stats=habit_stats,
        progress_stats=progress_stats,
    )
    return jsonify({"report": result["response"], "agents_used": result["agents_used"]})


# ---------------------------------------------------------------------------
# Family AI Insights
# ---------------------------------------------------------------------------
@chat_bp.route("/api/family-insights", methods=["POST"])
@login_required
def family_insights():
    """Generate AI-powered family health insights using the FamilyAnalysisAgent."""
    from agents.family_analysis_agent import FamilyAnalysisAgent
    from models.models import User, WorkoutLog, HabitLog, ProgressRecord
    from datetime import date, timedelta

    agent = FamilyAnalysisAgent()
    members = User.query.filter_by(parent_id=current_user.id).all()
    all_members = [current_user] + members

    thirty_ago = date.today() - timedelta(days=30)
    seven_ago  = date.today() - timedelta(days=7)
    family_data = []

    for m in all_members:
        w_logs = WorkoutLog.query.filter(
            WorkoutLog.user_id == m.id,
            WorkoutLog.date >= thirty_ago,
        ).all()
        completed = [w for w in w_logs if w.workout_completed]
        completion_rate = round(len(completed) / max(len(w_logs), 1) * 100, 1) if w_logs else 0.0

        h_logs = HabitLog.query.filter(
            HabitLog.user_id == m.id,
            HabitLog.date >= seven_ago,
        ).all()
        avg_water = round(sum(h.water_intake or 0 for h in h_logs) / max(len(h_logs), 1), 1) if h_logs else 0.0
        avg_sleep = round(sum(h.sleep_hours  or 0 for h in h_logs) / max(len(h_logs), 1), 1) if h_logs else 0.0

        streak = 0
        for i in range(30):
            d = date.today() - timedelta(days=i)
            if any(w.date == d and w.workout_completed for w in w_logs):
                streak += 1
            else:
                break

        bmi = m.bmi or 25
        bmi_score = max(0, 100 - abs(bmi - 22) * 5)
        fitness_score = round(bmi_score * 0.3 + completion_rate * 0.5 + min(streak * 5, 100) * 0.2, 1)

        family_data.append({
            "name": m.name,
            "profile_type": m.profile_type or "self",
            "age": m.age,
            "bmi": m.bmi,
            "bmi_category": m.bmi_category,
            "fitness_goal": m.fitness_goal,
            "fitness_score": fitness_score,
            "workout_completion_rate": completion_rate,
            "goal_progress_pct": min(len(completed) * 5, 100),
            "avg_water": avg_water,
            "avg_sleep": avg_sleep,
            "streak": streak,
        })

    result = agent.run(family_data)

    # Persist as AI recommendation
    from models.models import AIRecommendation
    db.session.add(AIRecommendation(
        user_id=current_user.id,
        agent_name=result["agent"],
        recommendation=result["raw"][:500],
        category="family",
    ))
    db.session.commit()

    return jsonify({
        "insights": result["raw"],
        "agents_used": [
            result["agent"],
            "UserProfileAgent",
            "HabitTrackingAgent",
            "ProgressEvaluationAgent",
        ],
        "member_count": len(family_data),
    })


# ---------------------------------------------------------------------------
# Chat History Clear
# ---------------------------------------------------------------------------
@chat_bp.route("/api/chat/clear", methods=["POST"])
@login_required
def clear_chat():
    ChatMessage.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({"status": "cleared"})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _get_habit_stats(user_id: int) -> dict:
    """Aggregate last-7-day habit stats for context."""
    seven_ago = date.today() - timedelta(days=7)
    habit_logs = HabitLog.query.filter(
        HabitLog.user_id == user_id,
        HabitLog.date >= seven_ago,
    ).all()

    workout_logs = WorkoutLog.query.filter(
        WorkoutLog.user_id == user_id,
        WorkoutLog.date >= seven_ago,
    ).all()

    # Streak
    streak = 0
    for i in range(7):
        d = date.today() - timedelta(days=i)
        if any(w.date == d and w.workout_completed for w in workout_logs):
            streak += 1
        else:
            break

    return {
        "workout_streak": streak,
        "weekly_workout_count": sum(1 for w in workout_logs if w.workout_completed),
        "total_workouts": WorkoutLog.query.filter_by(
            user_id=user_id, workout_completed=True
        ).count(),
        "avg_water_intake": (
            sum(h.water_intake or 0 for h in habit_logs) / len(habit_logs)
            if habit_logs else 0.0
        ),
        "avg_sleep_hours": (
            sum(h.sleep_hours or 0 for h in habit_logs) / len(habit_logs)
            if habit_logs else 0.0
        ),
    }


def _get_progress_stats(user_id: int) -> dict:
    """Build progress comparison stats from progress records."""
    records = (
        ProgressRecord.query.filter_by(user_id=user_id)
        .order_by(ProgressRecord.date.asc())
        .all()
    )
    if not records:
        return {}

    from flask_login import current_user as cu
    return {
        "initial_weight": records[0].weight,
        "current_weight": records[-1].weight,
        "target_weight": cu.target_weight,
        "initial_bmi": records[0].bmi,
        "current_bmi": records[-1].bmi,
        "weeks_active": max(1, (records[-1].date - records[0].date).days // 7),
        "total_workouts": WorkoutLog.query.filter_by(
            user_id=user_id, workout_completed=True
        ).count(),
    }


def _infer_category(agents: list) -> str:
    if not agents:
        return "general"
    agent = agents[0].lower()
    if "workout" in agent:
        return "workout"
    if "nutrition" in agent:
        return "nutrition"
    if "motivation" in agent:
        return "motivation"
    if "habit" in agent:
        return "habit"
    return "general"
