"""
=============================================================================
FITNESS BUDDY - MOTIVATION AGENT
=============================================================================
Delivers personalised motivational messages and accountability coaching.
"""

from config import AGENT_INSTRUCTIONS
from services.watsonx_service import generate


class MotivationAgent:
    """Provides daily motivation, encouragement, and accountability coaching."""

    name = "MotivationAgent"

    def run(self, user_data: dict, request_context: str = "") -> dict:
        """
        Parameters
        ----------
        user_data : dict – user profile
        request_context : str – e.g. "I missed workout yesterday" or "motivate me"
        """
        ai_cfg = AGENT_INSTRUCTIONS
        name = user_data.get("name", "Champion")
        goal = user_data.get("fitness_goal", "general_fitness")
        level = user_data.get("fitness_level", "beginner")
        tone = ai_cfg["motivation_tone"]
        style = ai_cfg["coaching_style"]

        prompt = f"""<|system|>
You are {ai_cfg["agent_name"]}, a world-class motivational fitness coach.
Personality: {ai_cfg["personality"]}
Motivation tone: {tone}. Coaching style: {style}.
{f'Be especially family-friendly and encouraging.' if ai_cfg['family_friendly'] else ''}
<|user|>
Provide a powerful motivational message and accountability coaching for:

- Name: {name}
- Fitness goal: {goal}
- Current fitness level: {level}
- Situation: {request_context or 'General daily motivation and encouragement'}

Include:
1. DAILY MOTIVATION - An inspiring personalised message (3-4 sentences)
2. TODAY'S CHALLENGE - One small actionable challenge for today
3. QUOTE OF THE DAY - A fitness/health related quote
4. ACCOUNTABILITY TIP - How to stay consistent this week
5. CELEBRATION - Acknowledge the effort they are putting in

Make it energetic, positive, and personal to {name}.
<|assistant|>"""

        raw = generate(prompt, max_tokens=450)
        return {"raw": raw, "agent": self.name}
