"""
=============================================================================
FITNESS BUDDY - ORCHESTRATOR AGENT
=============================================================================
Central coordinator that routes user requests to the appropriate specialist
agents and assembles a unified response.
=============================================================================
"""

from __future__ import annotations
import json
import re
from config import AGENT_INSTRUCTIONS
from services.watsonx_service import generate
from agents.user_profile_agent import UserProfileAgent
from agents.workout_planning_agent import WorkoutPlanningAgent
from agents.nutrition_agent import NutritionAgent
from agents.motivation_agent import MotivationAgent
from agents.habit_tracking_agent import HabitTrackingAgent
from agents.progress_evaluation_agent import ProgressEvaluationAgent


# Intent → agent mapping
INTENT_MAP = {
    "workout":    ["workout"],
    "exercise":   ["workout"],
    "train":      ["workout"],
    "meal":       ["nutrition"],
    "food":       ["nutrition"],
    "eat":        ["nutrition"],
    "diet":       ["nutrition"],
    "nutrition":  ["nutrition"],
    "motivat":    ["motivation"],
    "inspire":    ["motivation"],
    "encourage":  ["motivation"],
    "habit":      ["habit"],
    "water":      ["habit"],
    "sleep":      ["habit"],
    "streak":     ["habit"],
    "progress":   ["progress"],
    "result":     ["progress"],
    "weight":     ["progress"],
    "analyse":    ["progress"],
    "analyze":    ["progress"],
    "profile":    ["profile"],
    "bmi":        ["profile"],
    "plan":       ["workout", "nutrition"],
}


class OrchestratorAgent:
    """Routes requests, coordinates agents, and produces a final response."""

    def __init__(self) -> None:
        self.profile_agent = UserProfileAgent()
        self.workout_agent = WorkoutPlanningAgent()
        self.nutrition_agent = NutritionAgent()
        self.motivation_agent = MotivationAgent()
        self.habit_agent = HabitTrackingAgent()
        self.progress_agent = ProgressEvaluationAgent()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def process(
        self,
        user_message: str,
        user_data: dict,
        habit_stats: dict | None = None,
        progress_stats: dict | None = None,
    ) -> dict:
        """
        Orchestrate the agent pipeline for *user_message*.

        Returns
        -------
        dict:
            response     – final combined text to show the user
            agents_used  – list of agent names that were invoked
            reasoning    – brief orchestration explanation
        """
        habit_stats = habit_stats or {}
        progress_stats = progress_stats or {}

        # 1. Determine which agents to invoke
        intents = self._classify_intents(user_message)
        agents_to_invoke = self._select_agents(intents)

        # 2. Run selected agents
        agent_outputs: list[dict] = []
        agents_used: list[str] = []

        for agent_key in agents_to_invoke:
            result = self._run_agent(
                agent_key, user_message, user_data, habit_stats, progress_stats
            )
            if result:
                agent_outputs.append(result)
                agents_used.append(result["agent"])

        # 3. If no specific agent matched, use motivation as fallback
        if not agent_outputs:
            result = self._run_agent(
                "motivation", user_message, user_data, habit_stats, progress_stats
            )
            agent_outputs.append(result)
            agents_used.append(result["agent"])

        # 4. Combine outputs
        combined = self._combine_outputs(user_message, agent_outputs, user_data)

        return {
            "response": combined,
            "agents_used": agents_used,
            "reasoning": f"Detected intents: {intents}. Invoked: {agents_used}.",
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _classify_intents(self, message: str) -> list[str]:
        """Simple keyword-based intent classification."""
        msg_lower = message.lower()
        found: list[str] = []
        for keyword, intent_list in INTENT_MAP.items():
            if keyword in msg_lower:
                found.extend(intent_list)
        # De-duplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for i in found:
            if i not in seen:
                seen.add(i)
                unique.append(i)
        return unique or ["general"]

    def _select_agents(self, intents: list[str]) -> list[str]:
        """Map intents to agent keys (limit to 2 to avoid long responses)."""
        if "general" in intents:
            return ["motivation"]
        return intents[:2]

    def _run_agent(
        self,
        agent_key: str,
        user_message: str,
        user_data: dict,
        habit_stats: dict,
        progress_stats: dict,
    ) -> dict | None:
        if agent_key == "profile":
            return self.profile_agent.run(user_data)
        if agent_key == "workout":
            return self.workout_agent.run(user_data, user_message)
        if agent_key == "nutrition":
            return self.nutrition_agent.run(user_data, user_message)
        if agent_key == "motivation":
            return self.motivation_agent.run(user_data, user_message)
        if agent_key == "habit":
            return self.habit_agent.run(user_data, habit_stats, user_message)
        if agent_key == "progress":
            return self.progress_agent.run(user_data, progress_stats, user_message)
        return None

    def _combine_outputs(
        self, user_message: str, outputs: list[dict], user_data: dict
    ) -> str:
        """If multiple agents ran, ask Granite to synthesise; otherwise pass through."""
        if len(outputs) == 1:
            return outputs[0]["raw"]

        sections = "\n\n---\n\n".join(
            [f"[{o['agent']}]\n{o['raw']}" for o in outputs]
        )
        ai_cfg = AGENT_INSTRUCTIONS
        prompt = f"""<|system|>
You are {ai_cfg["agent_name"]}. Combine the following expert agent responses into
one coherent, friendly reply. Remove duplicate advice. Keep formatting clean.
Max ~400 words. Use {ai_cfg['language_style']} style.
<|user|>
Original question: {user_message}

Agent outputs:
{sections}
<|assistant|>"""

        return generate(prompt, max_tokens=600)
