from collections import defaultdict
from datetime import date

from backend.services.scheduler import create_assignment_schedule


def _format_duration(minutes: int) -> str:
    hours, remaining_minutes = divmod(minutes, 60)
    parts = []

    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if remaining_minutes:
        parts.append(f"{remaining_minutes} minute{'s' if remaining_minutes != 1 else ''}")

    return " ".join(parts) or "0 minutes"


def _display_result(result: dict) -> None:
    assignment = result["assignment"]

    print("\nAssignment analysis")
    print("-------------------")
    print(f"Type: {assignment['assignment_type'].replace('_', ' ').title()}")
    print(f"Subject: {assignment.get('subject') or 'Not specified'}")

    deadline = assignment.get("deadline")
    print(f"Deadline: {deadline.isoformat() if deadline else 'Not specified'}")
    print(f"Recurring: {'Yes' if assignment.get('daily') else 'No'}")

    requested_duration = assignment.get("requested_duration_minutes")
    if requested_duration is not None:
        duration_label = (
            "Requested daily duration"
            if assignment.get("daily")
            else "Requested duration"
        )
        print(f"{duration_label}: {_format_duration(requested_duration)}")

    print(f"Estimated effort: {assignment.get('estimated_hours', 0):g} hours")

    print(f"\nTask source: {result['task_source']}")
    fallback_reason = result.get("ai_fallback_reason")
    if fallback_reason:
        print(f"AI fallback reason: {fallback_reason}")

    print("\nGenerated tasks")
    print("---------------")
    for index, task in enumerate(result["tasks"], start=1):
        print(f"{index}. {task['title']} - {_format_duration(task['duration'])}")
        description = task.get("description")
        if description:
            print(f"   {description}")

    print("\nSchedule")
    print("--------")
    schedule_by_date = defaultdict(list)
    for task in result["schedule"]:
        schedule_by_date[task["scheduled_date"]].append(task)

    if not schedule_by_date:
        print("No tasks were scheduled.")
        return

    for scheduled_date, tasks in schedule_by_date.items():
        display_date = date.fromisoformat(scheduled_date).strftime("%a, %d %b %Y")
        print(display_date)
        for task in tasks:
            print(f"  * {task['title']} - {_format_duration(task['duration'])}")


def main() -> int:
    print("=" * 56)
    print("                 NeuroPilot")
    print("      Your assignment planning companion")
    print("=" * 56)

    try:
        raw_text = input("\nDescribe your assignment:\n> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")
        return 1

    if not raw_text:
        print("\nPlease enter a non-empty assignment description.")
        return 1

    try:
        result = create_assignment_schedule(
            raw_text=raw_text,
            start_date=date.today(),
        )
    except (ValueError, TypeError) as error:
        print(f"\nCould not create your plan: {error}")
        return 1
    except Exception as error:
        print(f"\nAn unexpected error occurred ({type(error).__name__}): {error}")
        return 1

    _display_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
