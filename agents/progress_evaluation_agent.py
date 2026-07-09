"""
=============================================================================
FITNESS BUDDY - PROGRESS EVALUATION AGENT
=============================================================================
Evaluates user progress over time and generates adaptive recommendations.
"""

from config import AGENT_INSTRUCTIONS
from services.watsonx_service import generate


class ProgressEvaluationAgent:
    """Analyses progress records and adapts fitness plans accordingly."""

    name = "ProgressEvaluationAgent"

    def run(self, user_data: dict, progress_stats: dict, request_context: str = "") -> dict:
        """
        Parameters
        ----------
        user_data      : dict – current user profile
        progress_stats : dict – aggregated progress data
            Keys: initial_weight, current_weight, target_weight,
                  initial_bmi, current_bmi, weeks_active,
                  total_workouts, weight_change
        request_context : str – optional user message
        """
        ai_cfg = AGENT_INSTRUCTIONS
        name = user_data.get("name", "User")
        goal = user_data.get("fitness_goal", "general_fitness")
        level = user_data.get("fitness_level", "beginner")

        init_w = progress_stats.get("initial_weight", user_data.get("weight", 70))
        curr_w = progress_stats.get("current_weight", user_data.get("weight", 70))
        tgt_w = progress_stats.get("target_weight", user_data.get("target_weight", 65))
        init_bmi = progress_stats.get("initial_bmi", user_data.get("bmi", 25))
        curr_bmi = progress_stats.get("current_bmi", user_data.get("bmi", 25))
        weeks = progress_stats.get("weeks_active", 1)
        total_workouts = progress_stats.get("total_workouts", 0)
        weight_change = round(curr_w - init_w, 2)

        prompt = f"""<|system|>
You are {ai_cfg["agent_name"]}, a data-driven fitness progress evaluator. {ai_cfg["personality"]}
<|user|>
Evaluate the fitness progress for {name} and provide a detailed analysis:

Progress Summary:
- Fitness goal: {goal}
- Current fitness level: {level}
- Starting weight: {init_w} kg | Current weight: {curr_w} kg | Target: {tgt_w} kg
- Weight change: {weight_change:+.1f} kg
- BMI change: {init_bmi} → {curr_bmi}
- Weeks active: {weeks}
- Total workouts completed: {total_workouts}

Additional context: {request_context or 'Weekly progress review'}

Provide:
1. PROGRESS SUMMARY - Key achievements and current status
2. GOAL ACHIEVEMENT SCORE - Out of 100 with reasoning
3. POSITIVE HIGHLIGHTS - What is working well
4. AREAS TO IMPROVE - 2-3 specific focus areas
5. PLAN ADJUSTMENT - Should the current plan be modified? How?
6. NEXT WEEK'S TARGETS - 3 specific measurable targets
7. ESTIMATED GOAL TIMELINE - When will they reach their goal at current pace?

Be encouraging but honest. Use data to back every point.
<|assistant|>"""

        raw = generate(prompt, max_tokens=600)
        return {"raw": raw, "agent": self.name}
