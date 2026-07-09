"""
=============================================================================
FITNESS BUDDY - WORKOUT PLANNING AGENT
=============================================================================
Generates personalised workout plans based on user profile and goals.
"""

from config import AGENT_INSTRUCTIONS
from services.watsonx_service import generate


class WorkoutPlanningAgent:
    """Creates adaptive workout plans for users."""

    name = "WorkoutPlanningAgent"

    def run(self, user_data: dict, request_context: str = "") -> dict:
        """
        Parameters
        ----------
        user_data : dict – user fitness profile
        request_context : str – optional extra instruction (e.g. "give me a 20-minute plan")
        """
        ai_cfg = AGENT_INSTRUCTIONS
        level = user_data.get("fitness_level", "beginner")
        goal = user_data.get("fitness_goal", "general_fitness")
        time_avail = user_data.get("available_workout_time", 30)
        intensity = ai_cfg["default_workout_intensity"]
        progression = ai_cfg["difficulty_progression"]
        beginner = ai_cfg["beginner_friendly"]

        prompt = f"""<|system|>
You are {ai_cfg["agent_name"]}, a certified fitness coach. {ai_cfg["personality"]}
Safety rules: {'; '.join(ai_cfg['safety_rules'][:2])}.
<|user|>
Create a personalised workout plan with the following requirements:

User profile:
- Fitness level: {level}
- Goal: {goal}
- Available time: {time_avail} minutes per session
- Intensity preference: {intensity}
- Difficulty progression: {progression}
- Beginner friendly mode: {beginner}

Additional request: {request_context or 'General daily workout plan'}

Please provide:
1. TODAY'S WORKOUT - A complete day workout with exercise names, sets/reps, and rest time
2. WEEKLY SCHEDULE - A 7-day plan overview
3. WARM-UP (5 min) and COOL-DOWN (5 min) routines
4. TIPS for this fitness level

Focus on home-friendly, no-equipment exercises wherever possible.
Format clearly with headers and bullet points.
<|assistant|>"""

        raw = generate(prompt, max_tokens=700)
        return {"raw": raw, "agent": self.name}
