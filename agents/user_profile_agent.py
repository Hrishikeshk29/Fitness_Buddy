"""
=============================================================================
FITNESS BUDDY - USER PROFILE AGENT
=============================================================================
Analyses user biometric and goal data; returns a structured fitness profile.
"""

from config import AGENT_INSTRUCTIONS
from services.watsonx_service import generate


class UserProfileAgent:
    """Builds a personalised fitness profile from raw user data."""

    name = "UserProfileAgent"

    def run(self, user_data: dict) -> dict:
        """
        Parameters
        ----------
        user_data : dict
            Keys: name, age, gender, height, weight, target_weight,
                  fitness_goal, fitness_level, dietary_preference,
                  daily_activity_level, available_workout_time, bmi, bmi_category
        Returns
        -------
        dict with keys: summary (str), insights (list[str]), profile_score (int)
        """
        ai_cfg = AGENT_INSTRUCTIONS
        name = user_data.get("name", "User")
        age = user_data.get("age", "unknown")
        gender = user_data.get("gender", "unknown")
        height = user_data.get("height", "unknown")
        weight = user_data.get("weight", "unknown")
        target_weight = user_data.get("target_weight", "unknown")
        bmi = user_data.get("bmi", "unknown")
        bmi_cat = user_data.get("bmi_category", "unknown")
        goal = user_data.get("fitness_goal", "general_fitness")
        level = user_data.get("fitness_level", "beginner")
        diet = user_data.get("dietary_preference", "vegetarian")
        activity = user_data.get("daily_activity_level", "moderate")
        time_avail = user_data.get("available_workout_time", 30)

        prompt = f"""<|system|>
You are {ai_cfg["agent_name"]}, a {ai_cfg["personality"]}.
Coaching style: {ai_cfg["coaching_style"]}. Language: {ai_cfg["language_style"]}.
Disclaimer: {ai_cfg["health_disclaimer"]}
<|user|>
Analyse this fitness profile and provide:
1. A short personalised summary (2-3 sentences)
2. Three key fitness insights based on the data
3. A profile completeness score out of 10

User data:
- Name: {name}
- Age: {age} | Gender: {gender}
- Height: {height} cm | Weight: {weight} kg | Target: {target_weight} kg
- BMI: {bmi} ({bmi_cat})
- Goal: {goal} | Level: {level}
- Diet: {diet} | Activity: {activity}
- Available workout time: {time_avail} minutes/day

{'Indian meal and fitness cultural preferences should be considered.' if ai_cfg['indian_fitness_preferences'] else ''}
Reply in plain text with sections: SUMMARY, INSIGHTS (3 bullet points), PROFILE_SCORE.
<|assistant|>"""

        raw = generate(prompt, max_tokens=400)
        return {"raw": raw, "agent": self.name}
