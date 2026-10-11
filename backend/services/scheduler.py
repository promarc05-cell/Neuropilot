
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
    """Schedule recurring or progressive practice across each day up to the deadline."""

    total_days = (deadline - start_date).days + 1

    if total_days <= 0 or not tasks:
        return []

    for task in tasks:
        duration = task["duration"]
        if duration > daily_minutes:
            raise ValueError(
                f"Task '{task['title']}' requires {duration} minutes, "
                f"but only {daily_minutes} minutes are available per day."
            )

    schedule = []
    current_date = start_date
    used_minutes = 0
    task_index = 0
    num_tasks = len(tasks)

    while current_date <= deadline:
        task = tasks[task_index % num_tasks]
        duration = task["duration"]

        if used_minutes + duration > daily_minutes:
            current_date += timedelta(days=1)
            used_minutes = 0
            if current_date > deadline:
                break

        schedule.append({
            **task,
            "scheduled_date": current_date.isoformat(),
        })
        used_minutes += duration
        task_index += 1

        # If a complete cycle of tasks finished on this day, advance to next day
        if task_index % num_tasks == 0:
            current_date += timedelta(days=1)
            used_minutes = 0

    return schedule


def create_assignment_schedule(
    raw_text: str,
    start_date: date,
    daily_minutes: int = 60,
) -> dict:
    """Analyze an assignment, generate tasks, and create its schedule."""

    assignment = analyze_assignment(raw_text, start_date=start_date)
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

    # Ensure individual tasks do not exceed daily capacity
    chunked_tasks = []
    for task in tasks:
        dur = task.get("duration", 0)
        if dur > schedule_minutes:
            parts = (dur + schedule_minutes - 1) // schedule_minutes
            part_dur = dur // parts
            remainder = dur % parts
            for p in range(parts):
                p_dur = part_dur + (1 if p < remainder else 0)
                chunked_tasks.append({
                    **task,
                    "title": f"{task['title']} (Part {p + 1})",
                    "duration": p_dur,
                })
        else:
            chunked_tasks.append(task)
    tasks = chunked_tasks

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
