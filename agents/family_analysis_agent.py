"""
=============================================================================
FITNESS BUDDY - FAMILY ANALYSIS AGENT
=============================================================================
Generates a holistic family health summary by aggregating data from all
family members and producing AI-powered insights via IBM Granite.
"""

from config import AGENT_INSTRUCTIONS
from services.watsonx_service import generate


class FamilyAnalysisAgent:
    """Produces family-wide health summaries and comparative insights."""

    name = "FamilyAnalysisAgent"

    def run(self, family_data: list[dict]) -> dict:
        """
        Parameters
        ----------
        family_data : list[dict]
            Each dict contains keys: name, profile_type, age, bmi, bmi_category,
            fitness_goal, fitness_level, fitness_score, workout_completion_rate,
            goal_progress_pct, avg_water, avg_sleep, streak
        Returns
        -------
        dict with keys: raw (str), agent (str)
        """
        ai_cfg = AGENT_INSTRUCTIONS
        if not family_data:
            return {"raw": "No family members found. Add family members to get insights.", "agent": self.name}

        # Build a compact summary table for the prompt
        lines = []
        for m in family_data:
            lines.append(
                f"- {m['name']} ({m.get('profile_type','member')}, age {m.get('age','?')}): "
                f"BMI {m.get('bmi','?')} ({m.get('bmi_category','?')}), "
                f"Goal: {str(m.get('fitness_goal','?')).replace('_',' ')}, "
                f"Fitness Score: {m.get('fitness_score',0):.0f}/100, "
                f"Workout Completion: {m.get('workout_completion_rate',0):.0f}%, "
                f"Goal Progress: {m.get('goal_progress_pct',0):.0f}%, "
                f"Avg Water: {m.get('avg_water',0):.1f}L, "
                f"Sleep: {m.get('avg_sleep',0):.1f}h, "
                f"Streak: {m.get('streak',0)} days"
            )

        family_summary = "\n".join(lines)

        prompt = f"""<|system|>
You are {ai_cfg["agent_name"]}, a family health advisor. {ai_cfg["personality"]}
Generate concise, actionable family health insights.
{ai_cfg["health_disclaimer"]}
<|user|>
Analyse the following family fitness data and provide a comprehensive family health report:

{family_summary}

Provide exactly these sections:
1. FAMILY HEALTH SUMMARY - 2-3 sentence overview of the family's overall fitness status
2. TOP PERFORMER - Who is doing best and why (1-2 sentences)
3. NEEDS ATTENTION - Who needs the most support and what specific help (1-2 sentences)
4. FAMILY INSIGHTS - 4 specific data-driven observations (bullet points)
5. FAMILY RECOMMENDATIONS - 3 actionable tips the whole family can do together
6. HYDRATION ALERT - Family average water intake vs recommended 2.5L target
7. FAMILY FITNESS SCORE - Overall family fitness score out of 100 with justification

Keep it positive, motivating, and specific to the data provided.
<|assistant|>"""

        raw = generate(prompt, max_tokens=600)
        return {"raw": raw, "agent": self.name}
