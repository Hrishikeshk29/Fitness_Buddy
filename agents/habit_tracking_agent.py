"""
=============================================================================
FITNESS BUDDY - HABIT TRACKING AGENT
=============================================================================
Analyses habit logs and generates coaching advice for consistency.
"""

from config import AGENT_INSTRUCTIONS
from services.watsonx_service import generate


class HabitTrackingAgent:
    """Tracks habits and coaches users toward consistent healthy routines."""

    name = "HabitTrackingAgent"

    def run(self, user_data: dict, habit_stats: dict, request_context: str = "") -> dict:
        """
        Parameters
        ----------
        user_data    : dict – user fitness profile
        habit_stats  : dict – aggregated habit data
            Keys: workout_streak, avg_water_intake, avg_sleep_hours,
                  weekly_workout_count, total_workouts
        request_context : str – additional user message
        """
        ai_cfg = AGENT_INSTRUCTIONS
        name = user_data.get("name", "User")
        streak = habit_stats.get("workout_streak", 0)
        water = habit_stats.get("avg_water_intake", 0.0)
        sleep = habit_stats.get("avg_sleep_hours", 0.0)
        weekly_workouts = habit_stats.get("weekly_workout_count", 0)

        prompt = f"""<|system|>
You are {ai_cfg["agent_name"]}, a habit coach. {ai_cfg["personality"]}
<|user|>
Analyse these habit stats for {name} and provide personalised coaching:

Habit Data:
- Current workout streak: {streak} days
- Average daily water intake: {water:.1f} litres (target: 2.5-3 litres)
- Average sleep: {sleep:.1f} hours/night (target: 7-8 hours)
- Workouts completed this week: {weekly_workouts}/7

Additional context: {request_context or 'General habit review'}

Provide:
1. HABIT ANALYSIS - What the data tells us (2-3 sentences)
2. TOP 3 IMPROVEMENTS - Priority areas to focus on
3. WATER CHALLENGE - Specific hydration tip for today
4. SLEEP OPTIMISATION - One actionable sleep improvement tip
5. STREAK BUILDER - How to maintain or improve the workout streak
6. WEEKLY HABIT SCORE - Score out of 10 with brief justification

Keep feedback positive and actionable, not judgmental.
<|assistant|>"""

        raw = generate(prompt, max_tokens=500)
        return {"raw": raw, "agent": self.name}
