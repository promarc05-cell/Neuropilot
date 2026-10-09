
from datetime import date

from backend.services.scheduler import create_assignment_schedule


print("\n========================================")
print("           NEUROPILOT")
print("========================================")

print("\nEnter your assignment.")
print("Example: Write a 5-page history paper by 20/10/2026")
print()

raw_text = input("> ").strip()


# -----------------------------------
# Check user input
# -----------------------------------

if not raw_text:
    print("\nError: Assignment cannot be empty.")
    raise SystemExit


# -----------------------------------
# Get user's assignment
# -----------------------------------

try:

    result = create_assignment_schedule(
        raw_text=raw_text,
        start_date=date.today(),
        daily_minutes=60,
    )

except ValueError as error:

    print("\nNeuroPilot could not create the schedule.")
    print(f"Reason: {error}")
    raise SystemExit


# -----------------------------------
# Assignment Understanding
# -----------------------------------

assignment = result["assignment"]

print("\n========================================")
print("        ASSIGNMENT UNDERSTANDING")
print("========================================")

print(f"Raw assignment: {assignment['raw_text']}")
print(f"Assignment type: {assignment['assignment_type']}")
print(f"Deadline: {assignment['deadline']}")
print(f"Estimated hours: {assignment['estimated_hours']}")


# -----------------------------------
# Generated Micro-Tasks
# -----------------------------------

print("\n========================================")
print("        GENERATED MICRO-TASKS")
print("========================================")

for number, task in enumerate(result["tasks"], start=1):

    print(
        f"{number}. "
        f"{task['title']} | "
        f"{task['duration']} min | "
        f"{task['difficulty']}"
    )


# -----------------------------------
# Generated Schedule
# -----------------------------------

print("\n========================================")
print("        PERSONALIZED SCHEDULE")
print("========================================")

for task in result["schedule"]:

    print(
        f"{task['scheduled_date']} | "
        f"{task['title']} | "
        f"{task['duration']} min"
    )


# -----------------------------------
# Finished
# -----------------------------------

print("\n========================================")
print("       NEUROPILOT PLAN CREATED")
print("========================================")