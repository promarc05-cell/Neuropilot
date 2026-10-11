import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from groq import Groq
from pydantic import ValidationError

from backend.schemas import TaskPlan
from backend.services.prompts import NEUROPILOT_SYSTEM_PROMPT


MODEL_NAME = "openai/gpt-oss-20b"


def _extract_json(response_text: str) -> dict[str, Any]:
    """
    Extract a JSON object from the model response.
    Handles plain JSON and JSON wrapped in Markdown fences.
    """
    text = response_text.strip()

    # Remove Markdown code fences if the model includes them.
    text = re.sub(
        r"^\s*```(?:json)?\s*|\s*```\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        # If extra text surrounds the JSON, try to locate the object.
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end <= start:
            raise ValueError("The AI response did not contain a valid JSON object.")

        try:
            result = json.loads(text[start:end + 1])
        except json.JSONDecodeError as error:
            raise ValueError(
                f"The AI returned malformed JSON: {error}"
            ) from error

    if not isinstance(result, dict):
        raise ValueError("The AI response must be a JSON object.")

    return result


def _validate_task_ids(plan: dict[str, Any]) -> None:
    """
    Check task identifiers and dependencies before returning the plan.
    """
    tasks = plan.get("tasks")

    if not isinstance(tasks, list) or not tasks:
        raise ValueError("The AI must generate at least one task.")

    task_ids = []

    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("Every generated task must be an object.")

        task_id = task.get("task_id")

        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("Every task must have a non-empty task_id.")

        task_ids.append(task_id)

        title = task.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Every task must have a non-empty title.")

        duration = task.get("duration_minutes")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool):
            raise ValueError(
                f"Task '{task_id}' must have a numeric duration_minutes."
            )

        if duration <= 0:
            raise ValueError(
                f"Task '{task_id}' must have a positive duration."
            )

    if len(task_ids) != len(set(task_ids)):
        raise ValueError("The AI generated duplicate task IDs.")

    known_ids = set(task_ids)

    for task in tasks:
        dependencies = task.get("dependencies", [])

        if not isinstance(dependencies, list):
            raise ValueError(
                f"Dependencies for task '{task['task_id']}' must be a list."
            )

        if task["task_id"] in dependencies:
            raise ValueError(
                f"Task '{task['task_id']}' cannot depend on itself."
            )

        for dependency_id in dependencies:
            if dependency_id not in known_ids:
                raise ValueError(
                    f"Task '{task['task_id']}' references unknown dependency "
                    f"'{dependency_id}'."
                )


def generate_ai_tasks(assignment: dict) -> dict:
    """
    Generate assignment-specific tasks using Groq.

    The assignment analyzer provides the structured context.
    The AI proposes meaningful tasks.
    TaskPlan validates the resulting structure.
    The scheduler remains responsible for assigning dates.
    """
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add your valid Groq API key "
            "to the environment configuration."
        )

    raw_text = assignment.get("raw_text")

    if not isinstance(raw_text, str) or not raw_text.strip():
        raise ValueError("The assignment must contain non-empty raw_text.")

    client = Groq(api_key=api_key)

    assignment_context = {
        key: value.isoformat() if hasattr(value, "isoformat") else value
        for key, value in assignment.items()
    }

    user_prompt = f"""
Create a task plan for the following assignment in valid JSON format.

ASSIGNMENT CONTEXT:
{json.dumps(assignment_context, ensure_ascii=False, indent=2)}

IMPORTANT REQUIREMENTS:

1. Understand the actual meaning of the user's assignment.
2. Generate tasks specifically relevant to the subject and requested activity.
3. For a study, practice, or preparation assignment, provide a well-rounded progression
   of 5 to 8 concrete steps covering the essential topics (e.g., core concepts, key structures,
   algorithms, focused problem solving, and a final mock test simulation).
4. For a subject-specific request (such as DSA, Python, Math, Web Development, etc.),
   generate specific concrete topics, problem categories, and actionable exercises
   (e.g., for DSA: arrays, strings, linked lists, trees, graphs, dynamic programming,
   and mock placement test simulation). Do not output vague generic titles.
5. Respect stated quantities, such as pages, sources, slides, practice
   duration, and other deliverables.
6. Put prerequisite tasks before the tasks that depend on them.
7. Make every task a concrete action with a clear title and description.
8. Estimate each task's duration in minutes. Keep tasks bite-sized and manageable
   for neurodivergent students (typically between 15 and 45 minutes).
9. Do not create the calendar schedule. The Python scheduler handles dates.
10. Do not interpret a total duration as a daily duration unless the user
    explicitly requests a daily or recurring activity.
11. Do not invent a deadline if the user did not provide one.
12. Return only the JSON object required by the system instructions.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": NEUROPILOT_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0,
            max_completion_tokens=2500,
            response_format={"type": "json_object"},
        )
    except Exception as error:
        raise RuntimeError(
            f"Groq task generation failed: {error}"
        ) from error

    response_text = response.choices[0].message.content

    if not response_text:
        raise ValueError("The AI returned an empty response.")

    ai_plan = _extract_json(response_text)

    # Validate task IDs, task fields, and dependency references.
    _validate_task_ids(ai_plan)

    try:
        validated_plan = TaskPlan.model_validate(ai_plan)
    except ValidationError as error:
        raise ValueError(
            f"The AI-generated plan does not match TaskPlan: {error}"
        ) from error

    plan_data = validated_plan.model_dump()

    # Preserve the existing scheduler's expected duration field and normalize unicode dashes.
    for task in plan_data["tasks"]:
        if "duration_minutes" in task:
            task["duration"] = int(task["duration_minutes"])
        if "title" in task and isinstance(task["title"], str):
            task["title"] = task["title"].replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
        if "description" in task and isinstance(task["description"], str):
            task["description"] = task["description"].replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")

    return plan_data