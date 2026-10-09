from datetime import date, timedelta

from backend.services.assignment_analyzer import analyze_assignment
from backend.services.task_generator import generate_tasks


def create_schedule(
    tasks: list[dict],
    start_date: date,
    deadline: date,
    daily_minutes: int = 60,
    repeat_daily: bool = False,
) -> list[dict]:
    """
    Schedule generated tasks between start_date and deadline.

    For normal assignments:
        Tasks are placed sequentially across available days.

    For repeated study:
        A progressive study plan is created for each day.
    """

    if not tasks:
        return []

    if deadline < start_date:
        raise ValueError(
            "Deadline cannot be before the start date."
        )

    if daily_minutes <= 0:
        raise ValueError(
            "Daily available time must be greater than 0."
        )

    for task in tasks:
        if "title" not in task:
            raise ValueError(
                "Every task must have a title."
            )

        duration = task.get("duration")

        if (
            not isinstance(duration, (int, float))
            or duration <= 0
        ):
            raise ValueError(
                f"Task '{task['title']}' must have "
                "a positive duration."
            )

    if repeat_daily:
        return _create_progressive_daily_schedule(
            tasks=tasks,
            start_date=start_date,
            deadline=deadline,
            daily_minutes=daily_minutes,
        )

    return _create_normal_schedule(
        tasks=tasks,
        start_date=start_date,
        deadline=deadline,
        daily_minutes=daily_minutes,
    )


def _create_normal_schedule(
    tasks: list[dict],
    start_date: date,
    deadline: date,
    daily_minutes: int,
) -> list[dict]:
    """
    Normal one-time assignment scheduling.

    Example:

        Task 1 = 30 min
        Task 2 = 30 min
        Task 3 = 30 min

    With 60 minutes/day:

        Day 1 → Task 1 + Task 2
        Day 2 → Task 3
    """

    schedule = []

    current_date = start_date
    used_minutes = 0

    for task in tasks:
        duration = task["duration"]

        if duration > daily_minutes:
            raise ValueError(
                f"Task '{task['title']}' requires "
                f"{duration} minutes, but only "
                f"{daily_minutes} minutes are "
                "available per day."
            )

        if used_minutes + duration > daily_minutes:
            current_date += timedelta(days=1)
            used_minutes = 0

        if current_date > deadline:
            raise ValueError(
                "There is not enough available time "
                "before the deadline."
            )

        scheduled_task = {
            **task,
            "scheduled_date": current_date.isoformat(),
        }

        schedule.append(scheduled_task)

        used_minutes += duration

    return schedule


def _create_progressive_daily_schedule(
    tasks: list[dict],
    start_date: date,
    deadline: date,
    daily_minutes: int,
) -> list[dict]:
    """
    Create a progressive study schedule.

    The study phases are expected to be:

        1. Fundamentals
        2. Practice
        3. Difficult areas
        4. Review

    The emphasis changes depending on which day
    of the study period the student is on.

    Example with 4 days:

        Day 1:
            Fundamentals → high
            Practice → medium
            Difficult areas → low
            Review → low

        Day 2:
            Fundamentals → medium
            Practice → high
            Difficult areas → medium
            Review → low

        Day 3:
            Fundamentals → low
            Practice → high
            Difficult areas → high
            Review → low

        Day 4:
            Fundamentals → low
            Practice → high
            Difficult areas → medium
            Review → high
    """

    total_days = (
        deadline - start_date
    ).days + 1

    if total_days <= 0:
        return []

    # We expect the study generator to provide
    # four phases in this order.
    #
    # [fundamentals, practice, difficult, review]
    if len(tasks) < 4:
        return _create_fallback_progressive_schedule(
            tasks=tasks,
            start_date=start_date,
            deadline=deadline,
            daily_minutes=daily_minutes,
        )

    fundamentals = tasks[0]
    practice = tasks[1]
    difficult = tasks[2]
    review = tasks[3]

    phases = [
        fundamentals,
        practice,
        difficult,
        review,
    ]

    schedule = []

    for day_index in range(total_days):

        current_date = start_date + timedelta(
            days=day_index
        )

        weights = _get_study_weights(
            day_index=day_index,
            total_days=total_days,
        )

        active_phases = []

        for phase, weight in zip(phases, weights):
            if weight > 0:
                active_phases.append(
                    (phase, weight)
                )

        durations = _allocate_daily_time(
            daily_minutes=daily_minutes,
            active_phases=active_phases,
        )

        for phase_index, (
            phase,
            duration,
        ) in enumerate(
            zip(
                [item[0] for item in active_phases],
                durations,
            )
        ):
            if duration <= 0:
                continue

            scheduled_task = {
                **phase,
                "duration": duration,
                "scheduled_date": (
                    current_date.isoformat()
                ),
                "title": (
                    f"Day {day_index + 1}: "
                    f"{phase['title']}"
                ),
            }

            schedule.append(
                scheduled_task
            )

    return schedule


def _get_study_weights(
    day_index: int,
    total_days: int,
) -> list[int]:
    """
    Determine how much emphasis each study phase
    receives on a particular day.

    Returns:

        [fundamentals, practice, difficult, review]
    """

    # One-day study plan.
    if total_days == 1:
        return [50, 30, 10, 10]

    # First day:
    # Build a strong foundation.
    if day_index == 0:
        return [60, 25, 5, 10]

    # Second day:
    # Start moving from learning into practice.
    if day_index == 1:
        return [40, 40, 10, 10]

    # Final day:
    # Practice + weak areas + review.
    if day_index == total_days - 1:
        return [10, 50, 20, 20]

    # Middle days:
    # Practice becomes dominant.
    return [15, 55, 20, 10]


def _allocate_daily_time(
    daily_minutes: int,
    active_phases: list[tuple[dict, int]],
) -> list[int]:
    """
    Convert phase weights into actual minutes.

    Ensures every active phase receives at least
    a small useful amount of time when possible.
    """

    if not active_phases:
        return []

    weight_total = sum(
        weight
        for _, weight in active_phases
    )

    if weight_total <= 0:
        return []

    number_of_phases = len(active_phases)

    # If the session is very short, do not create
    # several tiny tasks.
    if daily_minutes < number_of_phases * 10:
        strongest_phase = max(
            active_phases,
            key=lambda item: item[1],
        )

        return [
            daily_minutes
            if phase is strongest_phase
            else 0
            for phase, _ in active_phases
        ]

    durations = []

    for _, weight in active_phases:
        duration = round(
            daily_minutes
            * weight
            / weight_total
        )

        duration = max(10, duration)

        durations.append(duration)

    # Rounding can make the total slightly larger
    # or smaller than the requested daily time.
    difference = (
        daily_minutes
        - sum(durations)
    )

    # Add/subtract the difference from the phase
    # with the largest allocation.
    largest_index = max(
        range(len(durations)),
        key=lambda index: durations[index],
    )

    durations[largest_index] += difference

    # Prevent an invalid negative duration.
    if durations[largest_index] < 10:
        durations[largest_index] = 10

    # If fixing the minimum changed the total,
    # normalize one more time.
    current_total = sum(durations)

    if current_total != daily_minutes:
        difference = (
            daily_minutes
            - current_total
        )

        durations[largest_index] += difference

    return durations


def _create_fallback_progressive_schedule(
    tasks: list[dict],
    start_date: date,
    deadline: date,
    daily_minutes: int,
) -> list[dict]:
    """
    Fallback for study plans that contain fewer
    than four phases.
    """

    total_days = (
        deadline - start_date
    ).days + 1

    if total_days <= 0:
        return []

    schedule = []

    for day_index in range(total_days):

        current_date = start_date + timedelta(
            days=day_index
        )

        # Rotate toward later tasks as the student
        # progresses through the available days.
        if total_days == 1:
            selected_tasks = tasks

        else:
            progress = day_index / (
                total_days - 1
            )

            start_index = round(
                progress
                * max(0, len(tasks) - 1)
            )

            selected_tasks = tasks[
                start_index:
            ]

            if not selected_tasks:
                selected_tasks = [
                    tasks[-1]
                ]

        remaining_minutes = daily_minutes

        for task in selected_tasks:

            if remaining_minutes <= 0:
                break

            duration = min(
                task["duration"],
                remaining_minutes,
            )

            if duration <= 0:
                continue

            scheduled_task = {
                **task,
                "duration": duration,
                "scheduled_date": (
                    current_date.isoformat()
                ),
                "title": (
                    f"Day {day_index + 1}: "
                    f"{task['title']}"
                ),
            }

            schedule.append(
                scheduled_task
            )

            remaining_minutes -= duration

    return schedule


def create_assignment_schedule(
    raw_text: str,
    start_date: date,
    daily_minutes: int = 60,
) -> dict:
    """
    Complete NeuroPilot pipeline:

        Raw assignment
              ↓
        Assignment Analyzer
              ↓
        Task Generator
              ↓
        Personalized Scheduler
    """

    assignment = analyze_assignment(
        raw_text
    )

    deadline = assignment.get(
        "deadline"
    )

    if deadline is None:
        raise ValueError(
            "Please provide a deadline so NeuroPilot "
            "can create a schedule."
        )

    tasks = generate_tasks(
        assignment
    )

    repeat_daily = assignment.get(
        "daily",
        False,
    )

    if repeat_daily:

        requested_minutes = assignment.get(
            "requested_duration_minutes"
        )

        if requested_minutes:
            daily_schedule_minutes = (
                requested_minutes
            )
        else:
            daily_schedule_minutes = (
                daily_minutes
            )

    else:
        daily_schedule_minutes = (
            daily_minutes
        )

    schedule = create_schedule(
        tasks=tasks,
        start_date=start_date,
        deadline=deadline,
        daily_minutes=daily_schedule_minutes,
        repeat_daily=repeat_daily,
    )

    return {
        "assignment": assignment,
        "tasks": tasks,
        "schedule": schedule,
    }