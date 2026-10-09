
from pydantic import ValidationError

from backend.schemas import TaskPlan


# TEST 1: A valid task plan should be accepted.
valid_plan = {
    "assignment_summary": "Learn operating system process management",
    "assignment_type": "study",
    "tasks": [
        {
            "task_id": "task_1",
            "parent_task_id": None,
            "title": "Understand process states",
            "description": "Learn the main states of an operating system process.",
            "duration_minutes": 20,
            "difficulty": "easy",
            "prerequisite_ids": [],
            "completion_criteria": [
                "Explain the main process states in your own words."
            ],
        },
        {
            "task_id": "task_2",
            "parent_task_id": None,
            "title": "Learn process scheduling",
            "description": "Understand how the operating system schedules processes.",
            "duration_minutes": 30,
            "difficulty": "medium",
            "prerequisite_ids": ["task_1"],
            "completion_criteria": [
                "Explain how process scheduling works."
            ],
        },
    ],
}

print("\nTEST 1: Valid task plan")

try:
    plan = TaskPlan.model_validate(valid_plan)
    print("PASS: Valid task plan accepted.")
    print("Assignment:", plan.assignment_summary)
    print("Number of tasks:", len(plan.tasks))

except ValidationError as error:
    print("FAIL: Valid plan was rejected.")
    print(error)


# TEST 2: A zero-minute task should be rejected.
invalid_plan = {
    **valid_plan,
    "tasks": [
        {
            **valid_plan["tasks"][0],
            "duration_minutes": 0,
        }
    ],
}

print("\nTEST 2: Invalid task duration")

try:
    TaskPlan.model_validate(invalid_plan)
    print("FAIL: Zero-minute task was accepted.")

except ValidationError:
    print("PASS: Zero-minute task rejected.")


# TEST 3: An unsupported difficulty should be rejected.
invalid_difficulty_plan = {
    **valid_plan,
    "tasks": [
        {
            **valid_plan["tasks"][0],
            "difficulty": "extreme",
        }
    ],
}

print("\nTEST 3: Invalid difficulty")

try:
    TaskPlan.model_validate(invalid_difficulty_plan)
    print("FAIL: Unsupported difficulty was accepted.")

except ValidationError:
    print("PASS: Unsupported difficulty rejected.")


print("\nSchema validation tests finished.")
