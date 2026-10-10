
from datetime import date

from backend.services.scheduler import create_assignment_schedule


print("=" * 50)
print("          NEUROPILOT ASSIGNMENT INPUT")
print("=" * 50)

raw_text = input("\nEnter your assignment:\n> ").strip()

if not raw_text:
    print("Please enter an assignment.")
    raise SystemExit(1)

try:
    result = create_assignment_schedule(
        raw_text=raw_text,
        start_date=date.today(),
        daily_minutes=60,
    )

    print("\nTask source:", result["task_source"])
    print("Fallback reason:", result["ai_fallback_reason"])

    print("\nGenerated tasks:")

    for index, task in enumerate(result["tasks"], start=1):
        print(
            f"{index}. {task['title']} "
            f"- {task['duration']} minutes"
        )

    print("\nSchedule:")

    if not result["schedule"]:
        print("No tasks were scheduled.")
    else:
        for task in result["schedule"]:
            print(
                f"{task['scheduled_date']} - "
                f"{task['title']} - "
                f"{task['duration']} minutes"
            )

except (ValueError, TypeError) as error:
    print(f"\nCould not create your schedule: {error}")

except Exception as error:
    print(f"\nUnexpected error: {error}")
