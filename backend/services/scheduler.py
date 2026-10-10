
from datetime import date, timedelta

from backend.services.ai_task_generator import generate_ai_tasks
from backend.services.assignment_analyzer import analyze_assignment
from backend.services.task_generator import generate_tasks


def create_schedule(
    tasks: list[dict],
    start_date: date,
    deadline: date,
    daily_minutes: int = 60,
    repeat_daily: bool = False,
) -> list[dict]:
    """Schedule tasks between the start date and deadline."""

    if not tasks:
        return []

    if deadline < start_date:
        raise ValueError("Deadline cannot be before the start date.")

    if daily_minutes <= 0:
        raise ValueError("Daily available time must be greater than 0.")

    for task in tasks:
        if not task.get("title"):
            raise ValueError("Every task must have a title.")

        duration = task.get("duration")
        if (
            not isinstance(duration, (int, float))
            or isinstance(duration, bool)
            or duration <= 0
        ):
            raise ValueError(
                f"Task '{task.get('title', 'Unknown')}' "
                "must have a positive duration."
            )

    if repeat_daily:
        return _create_progressive_daily_schedule(
            tasks, start_date, deadline, daily_minutes
        )

    return _create_normal_schedule(
        tasks, start_date, deadline, daily_minutes
    )


def _create_normal_schedule(
    tasks: list[dict],
    start_date: date,
    deadline: date,
    daily_minutes: int,
) -> list[dict]:
    """Schedule one-time tasks sequentially, preserving durations."""

    schedule = []
    current_date = start_date
    used_minutes = 0

    for task in tasks:
        duration = task["duration"]

        if duration > daily_minutes:
            raise ValueError(
                f"Task '{task['title']}' requires {duration} minutes, "
                f"but only {daily_minutes} minutes are available per day."
            )

        if used_minutes + duration > daily_minutes:
            current_date += timedelta(days=1)
            used_minutes = 0

        if current_date > deadline:
            raise ValueError(
                "There is not enough available time before the deadline."
            )

        schedule.append({
            **task,
            "scheduled_date": current_date.isoformat(),
        })
        used_minutes += duration

    return schedule


def _create_progressive_daily_schedule(
    tasks: list[dict],
    start_date: date,
    deadline: date,
    daily_minutes: int,
) -> list[dict]:
    """Repeat the same task plan each day without changing durations."""

    total_days = (deadline - start_date).days + 1

    if total_days <= 0:
        return []

    total_task_minutes = sum(task["duration"] for task in tasks)

    if total_task_minutes > daily_minutes:
        raise ValueError(
            f"Recurring tasks require {total_task_minutes} minutes per day, "
            f"but the daily limit is {daily_minutes} minutes."
        )

    schedule = []

    for day_index in range(total_days):
        current_date = start_date + timedelta(days=day_index)

        for task in tasks:
            schedule.append({
                **task,
                "scheduled_date": current_date.isoformat(),
                "title": f"Day {day_index + 1}: {task['title']}",
            })

    return schedule


def create_assignment_schedule(
    raw_text: str,
    start_date: date,
    daily_minutes: int = 60,
) -> dict:
    """Analyze an assignment, generate tasks, and create its schedule."""

    assignment = analyze_assignment(raw_text)
    deadline = assignment.get("deadline")

    if deadline is None:
        raise ValueError(
            "Please provide a deadline so NeuroPilot can create a schedule."
        )

    repeat_daily = assignment.get("daily", False)
    ai_fallback_reason = None

    try:
        ai_plan = generate_ai_tasks(assignment)
        ai_tasks = ai_plan.get("tasks", [])

        if not ai_tasks:
            raise ValueError("AI returned an empty task list.")

        tasks = [
            {
                **task,
                "duration": task.get(
                    "duration",
                    task.get("duration_minutes"),
                ),
            }
            for task in ai_tasks
        ]

        if any(task.get("duration") is None for task in tasks):
            raise ValueError("AI returned a task without a duration.")

        task_source = "ai"

    except Exception as error:
        tasks = generate_tasks(assignment)
        task_source = "template_fallback"
        ai_fallback_reason = str(error)

    requested_minutes = assignment.get("requested_duration_minutes")

    if repeat_daily:
        schedule_minutes = (
            requested_minutes if requested_minutes else daily_minutes
        )
    else:
        schedule_minutes = daily_minutes

    schedule = create_schedule(
        tasks=tasks,
        start_date=start_date,
        deadline=deadline,
        daily_minutes=schedule_minutes,
        repeat_daily=repeat_daily,
    )

    return {
        "assignment": assignment,
        "tasks": tasks,
        "schedule": schedule,
        "task_source": task_source,
        "ai_fallback_reason": ai_fallback_reason,
    }
