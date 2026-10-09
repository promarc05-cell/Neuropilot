from datetime import date


def _task(
    title: str,
    description: str,
    duration: int,
    difficulty: str = "medium",
) -> dict:
    return {
        "title": title,
        "description": description,
        "duration": duration,
        "difficulty": difficulty,
    }


def _split_time(
    total_minutes: int,
    weights: list[int],
) -> list[int]:
    """
    Split total time according to phase weights.

    Example:
        total = 120
        weights = [50, 30, 20]

    Produces approximately:
        [60, 36, 24]
    """

    if total_minutes <= 0 or not weights:
        return []

    weight_total = sum(weights)

    durations = [
        max(10, round(total_minutes * weight / weight_total))
        for weight in weights
    ]

    difference = total_minutes - sum(durations)

    durations[-1] += difference

    return durations


def _generate_study_tasks(
    assignment: dict,
) -> list[dict]:
    """
    Create a progressive study plan.

    The plan is intentionally phase-based:

        Fundamentals
            ↓
        Practice
            ↓
        Difficult areas
            ↓
        Review

    The actual subject and available study time come
    from the student's assignment.
    """

    subject = assignment.get("subject") or "the subject"

    requested_minutes = assignment.get(
        "requested_duration_minutes"
    )

    if not requested_minutes:
        requested_minutes = int(
            assignment.get("estimated_hours", 2.0) * 60
        )

    # Very short study sessions should not be split
    # into too many tiny tasks.
    if requested_minutes <= 30:
        return [
            _task(
                f"Study {subject} fundamentals",
                (
                    f"Build or strengthen your understanding "
                    f"of the fundamentals of {subject}."
                ),
                requested_minutes,
                "medium",
            )
        ]

    if requested_minutes <= 60:
        durations = _split_time(
            requested_minutes,
            [60, 40],
        )

        return [
            _task(
                f"Build {subject} fundamentals",
                (
                    f"Learn and clarify the core concepts "
                    f"of {subject}."
                ),
                durations[0],
                "medium",
            ),
            _task(
                f"Practice {subject}",
                (
                    f"Apply the concepts you studied in "
                    f"{subject}."
                ),
                durations[1],
                "medium",
            ),
        ]

    # A normal study session contains four phases.
    durations = _split_time(
        requested_minutes,
        [40, 30, 20, 10],
    )

    return [
        _task(
            f"Build {subject} fundamentals",
            (
                f"Learn and strengthen the core concepts "
                f"of {subject}. Focus on understanding "
                "before moving heavily into practice."
            ),
            durations[0],
            "medium",
        ),
        _task(
            f"Practice {subject} concepts",
            (
                f"Use exercises or problems to apply "
                f"the {subject} concepts you studied."
            ),
            durations[1],
            "medium",
        ),
        _task(
            f"Work on difficult {subject} areas",
            (
                f"Identify concepts that feel difficult "
                f"in {subject} and spend focused time "
                "understanding them."
            ),
            durations[2],
            "medium",
        ),
        _task(
            f"Review {subject}",
            (
                f"Quickly review what you learned and "
                "identify what needs more practice."
            ),
            durations[3],
            "easy",
        ),
    ]


def _generate_writing_tasks(
    assignment: dict,
) -> list[dict]:

    pages = assignment.get("pages") or 5
    sources = assignment.get("sources_required")
    research_required = assignment.get(
        "research_required",
        False,
    )

    tasks = [
        _task(
            "Choose a topic",
            "Decide the exact topic and direction.",
            15,
            "easy",
        )
    ]

    if research_required or sources:
        source_count = sources or 3

        tasks.append(
            _task(
                f"Find {source_count} useful sources",
                "Collect relevant sources for the assignment.",
                min(30, source_count * 5),
                "medium",
            )
        )

    tasks.append(
        _task(
            "Create an outline",
            "Plan the structure before writing.",
            20,
            "medium",
        )
    )

    tasks.append(
        _task(
            "Write the introduction",
            "Write the opening section.",
            25,
            "medium",
        )
    )

    body_sections = max(
        1,
        min(5, pages // 2 + 1),
    )

    for i in range(1, body_sections + 1):
        tasks.append(
            _task(
                f"Write body section {i}",
                f"Write body section {i}.",
                25,
                "medium",
            )
        )

    tasks.append(
        _task(
            "Write the conclusion",
            "Summarize the main points.",
            20,
            "medium",
        )
    )

    tasks.append(
        _task(
            "Review the assignment",
            "Check structure, clarity and requirements.",
            20,
            "easy",
        )
    )

    return tasks


def _generate_presentation_tasks(
    assignment: dict,
) -> list[dict]:

    slides = assignment.get("slides") or 10

    tasks = [
        _task(
            "Choose the main topic",
            "Define the main message of the presentation.",
            15,
            "easy",
        ),
        _task(
            "Create the presentation outline",
            "Plan the flow of the presentation.",
            20,
            "medium",
        ),
    ]

    group_count = max(
        1,
        min(5, (slides + 3) // 4),
    )

    for i in range(1, group_count + 1):
        tasks.append(
            _task(
                f"Create slide group {i}",
                f"Create and organize slide group {i}.",
                25,
                "medium",
            )
        )

    tasks.append(
        _task(
            "Review the slides",
            "Check the presentation for clarity and consistency.",
            20,
            "easy",
        )
    )

    tasks.append(
        _task(
            "Practice the presentation",
            "Practice explaining the slides aloud.",
            20,
            "medium",
        )
    )

    return tasks


def _generate_project_tasks(
    assignment: dict,
) -> list[dict]:

    subject = assignment.get("subject") or "the project"

    tasks = [
        _task(
            "Understand the project requirements",
            f"Clarify what needs to be built for {subject}.",
            20,
            "easy",
        ),
        _task(
            "Plan the project",
            "Break the project into implementation parts.",
            25,
            "medium",
        ),
        _task(
            "Build the first part",
            f"Start implementing {subject}.",
            30,
            "medium",
        ),
    ]

    if assignment.get("testing_required"):
        tasks.append(
            _task(
                "Test the work",
                "Run tests and check whether the project works correctly.",
                30,
                "medium",
            )
        )

    if assignment.get("deployment_required"):
        tasks.append(
            _task(
                "Deploy the work",
                "Deploy or publish the completed project.",
                30,
                "medium",
            )
        )

    tasks.append(
        _task(
            "Review the project",
            "Check the completed work against the requirements.",
            20,
            "easy",
        )
    )

    return tasks


def _generate_general_tasks(
    assignment: dict,
) -> list[dict]:

    return [
        _task(
            "Understand the assignment",
            "Identify what needs to be completed.",
            15,
            "easy",
        ),
        _task(
            "Break the work into smaller parts",
            "Divide the assignment into manageable pieces.",
            15,
            "easy",
        ),
        _task(
            "Complete the first part",
            "Start working on the first meaningful part.",
            25,
            "medium",
        ),
        _task(
            "Review the remaining work",
            "Check what is left to complete.",
            15,
            "easy",
        ),
    ]


def generate_tasks(
    assignment: dict,
) -> list[dict]:

    assignment_type = assignment.get(
        "assignment_type",
        "general",
    )

    if assignment_type == "study":
        return _generate_study_tasks(assignment)

    if assignment_type == "writing":
        return _generate_writing_tasks(assignment)

    if assignment_type == "presentation":
        return _generate_presentation_tasks(assignment)

    if assignment_type == "project":
        return _generate_project_tasks(assignment)

    return _generate_general_tasks(assignment)