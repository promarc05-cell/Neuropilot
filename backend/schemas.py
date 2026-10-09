
from enum import Enum

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TaskItem(BaseModel):
    """
    One small piece of an assignment.

    Tasks can be grouped into a hierarchy using parent_task_id.
    """

    task_id: str = Field(
        description="Unique ID within this assignment, e.g. task_1"
    )

    parent_task_id: str | None = Field(
        default=None,
        description=(
            "ID of the parent task. Use null for a top-level task."
        ),
    )

    title: str = Field(
        min_length=1,
        description="Short, clear title for the task"
    )

    description: str = Field(
        min_length=1,
        description="Explain exactly what the student should do"
    )

    duration_minutes: int = Field(
        ge=1,
        description="Estimated effort in minutes; must be positive"
    )

    difficulty: Difficulty = Field(
        description="Estimated difficulty: easy, medium, or hard"
    )

    prerequisite_ids: list[str] = Field(
        default_factory=list,
        description=(
            "Task IDs that should be completed before this task"
        ),
    )

    completion_criteria: list[str] = Field(
        min_length=1,
        description="Observable conditions that mean the task is complete"
    )


class TaskPlan(BaseModel):
    """
    Structured task breakdown proposed by the AI.
    This is not the final schedule.
    """

    assignment_summary: str = Field(
        min_length=1,
        description="Brief explanation of what the assignment requires"
    )

    assignment_type: str = Field(
        min_length=1,
        description="Type of assignment, such as study, writing, or project"
    )

    tasks: list[TaskItem] = Field(
        min_length=1,
        description=(
            "Tasks ordered logically, with larger tasks split into subtasks"
        )
    )
