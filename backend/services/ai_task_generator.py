
import json
import os
import re

from dotenv import load_dotenv
from groq import Groq
from pydantic import ValidationError

from backend.schemas import TaskPlan
from backend.services.prompts import NEUROPILOT_SYSTEM_PROMPT


MODEL_NAME = "openai/gpt-oss-20b"

load_dotenv()


def generate_ai_tasks(assignment: dict) -> dict:
    """
    Generate a dynamic task plan using Groq.

    Input:
        Assignment dictionary produced by assignment_analyzer.py.

    Output:
        {
            "assignment_summary": str,
            "assignment_type": str,
            "tasks": list[dict]
        }

    Raises an error if the AI response cannot be parsed
    or does not match the TaskPlan schema.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set in this terminal."
        )

    raw_text = assignment.get("raw_text", "").strip()

    if not raw_text:
        raise ValueError(
            "The assignment must contain raw_text."
        )

    # Convert date objects and other values into JSON-safe data.
    assignment_context = {
        key: value.isoformat() if hasattr(value, "isoformat") else value
        for key, value in assignment.items()
    }

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    NEUROPILOT_SYSTEM_PROMPT
                    + """

IMPORTANT OUTPUT INSTRUCTIONS:
Return exactly one valid JSON object.
Do not use Markdown fences.
Do not include explanations outside the JSON.
Every completion_criteria field must be an array of strings.
Every prerequisite_ids field must be an array of strings.
Generate specific, manageable steps for the actual assignment.
For recurring practice, generate the steps for ONE daily session.
Do not generate calendar dates or schedule tasks.
"""
                ),
            },
            {
                "role": "user",
                "content": (
                    "Generate a task plan for this student's assignment.\n\n"
                    "RAW ASSIGNMENT:\n"
                    f"{raw_text}\n\n"
                    "EXTRACTED ASSIGNMENT INFORMATION:\n"
                    f"{json.dumps(assignment_context, ensure_ascii=False)}\n\n"
                    "Return JSON with these top-level fields:\n"
                    "assignment_summary, assignment_type, tasks.\n"
                    "Each task must contain task_id, parent_task_id, "
                    "title, description, duration_minutes, difficulty, "
                    "prerequisite_ids, completion_criteria."
                ),
            },
        ],
        temperature=0,
        max_completion_tokens=4000,
    )

    content = response.choices[0].message.content

    if not content or not content.strip():
        raise RuntimeError(
            "Groq returned an empty task plan."
        )

    # Extract JSON if the model unexpectedly adds surrounding text.
    match = re.search(r"\{.*\}", content, flags=re.DOTALL)

    if not match:
        raise ValueError(
            "Groq did not return a JSON object. "
            f"Response received: {content}"
        )

    try:
        raw_plan = json.loads(match.group(0))
        plan = TaskPlan.model_validate(raw_plan)
    except (json.JSONDecodeError, ValidationError) as error:
        raise ValueError(
            "Groq returned a task plan that failed validation. "
            f"Details: {error}\nResponse: {content}"
        ) from error

    # Validate relationships before passing tasks to the scheduler.
    task_ids = [task.task_id for task in plan.tasks]

    if len(task_ids) != len(set(task_ids)):
        raise ValueError(
            "AI generated duplicate task IDs."
        )

    valid_ids = set(task_ids)

    for task in plan.tasks:
        if task.parent_task_id and task.parent_task_id not in valid_ids:
            raise ValueError(
                f"Task '{task.task_id}' refers to a missing parent."
            )

        for prerequisite_id in task.prerequisite_ids:
            if prerequisite_id not in valid_ids:
                raise ValueError(
                    f"Task '{task.task_id}' refers to missing "
                    f"prerequisite '{prerequisite_id}'."
                )

            if prerequisite_id == task.task_id:
                raise ValueError(
                    f"Task '{task.task_id}' cannot depend on itself."
                )

    # Convert AI schema fields to the existing scheduler's format.
    tasks = []

    for task in plan.tasks:
        tasks.append(
            {
                "task_id": task.task_id,
                "parent_task_id": task.parent_task_id,
                "title": task.title,
                "description": task.description,
                "duration": task.duration_minutes,
                "difficulty": task.difficulty.value,
                "prerequisite_ids": task.prerequisite_ids,
                "completion_criteria": task.completion_criteria,
            }
        )

    return {
        "assignment_summary": plan.assignment_summary,
        "assignment_type": plan.assignment_type,
        "tasks": tasks,
    }
