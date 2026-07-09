"""
=============================================================================
FITNESS BUDDY - NUTRITION AGENT
=============================================================================
Generates personalised meal plans with Indian food options.
"""

from config import AGENT_INSTRUCTIONS
from services.watsonx_service import generate


class NutritionAgent:
    """Provides personalised meal plans and nutrition guidance."""

    name = "NutritionAgent"

    def run(self, user_data: dict, request_context: str = "") -> dict:
        """
        Parameters
        ----------
        user_data : dict – user fitness profile
        request_context : str – optional extra instruction
        """
        ai_cfg = AGENT_INSTRUCTIONS
        diet = user_data.get("dietary_preference", "vegetarian")
        goal = user_data.get("fitness_goal", "general_fitness")
        weight = user_data.get("weight", 70)
        target_weight = user_data.get("target_weight", 65)
        bmi_cat = user_data.get("bmi_category", "Normal weight")
        include_calories = ai_cfg["include_calorie_estimates"]
        indian_meals = ai_cfg["indian_meal_recommendations"]

        calorie_note = "Include estimated calories for each meal." if include_calories else ""
        indian_note = (
            "Prioritise Indian foods and traditional Indian dishes. "
            "Include dal, sabzi, roti, rice, idli, dosa, poha, upma, etc. "
            "Add regional variety from South Indian, North Indian, and West Indian cuisines."
        ) if indian_meals else ""

        prompt = f"""<|system|>
You are {ai_cfg["agent_name"]}, a certified nutritionist. {ai_cfg["personality"]}
<|user|>
Create a personalised daily meal plan with the following profile:

- Dietary preference: {diet}
- Fitness goal: {goal}
- Current weight: {weight} kg | Target weight: {target_weight} kg
- BMI category: {bmi_cat}

Additional request: {request_context or 'Full day meal plan'}

{indian_note}
{calorie_note}

Provide:
1. BREAKFAST (with 2 options)
2. MID-MORNING SNACK
3. LUNCH (with 2 options)
4. EVENING SNACK
5. DINNER (with 2 options)
6. HYDRATION RECOMMENDATION (daily water intake)
7. MACRONUTRIENT OVERVIEW (approximate protein/carb/fat split)

Keep it practical, affordable, and easy to prepare at home.
<|assistant|>"""

        raw = generate(prompt, max_tokens=700)
        return {"raw": raw, "agent": self.name}
