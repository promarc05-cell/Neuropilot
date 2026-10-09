from datetime import date

from backend.services.scheduler import create_schedule


# -----------------------------------
# Test 1: Basic scheduling
# -----------------------------------

tasks = [
    {"title": "Choose a topic", "duration": 15},
    {"title": "Create an outline", "duration": 20},
    {"title": "Write introduction", "duration": 25},
    {"title": "Write body section 1", "duration": 25},
    {"title": "Write body section 2", "duration": 25},
]

schedule = create_schedule(
    tasks=tasks,
    start_date=date(2026, 10, 6),
    deadline=date(2026, 10, 8),
    daily_minutes=60,
)


print("\n=== GENERATED SCHEDULE ===")

for task in schedule:
    print(
        f"{task['scheduled_date']} | "
        f"{task['title']} | "
        f"{task['duration']} min"
    )


# -----------------------------------
# Test 2: Check expected dates
# -----------------------------------

assert schedule[0]["scheduled_date"] == "2026-10-06"
assert schedule[1]["scheduled_date"] == "2026-10-06"
assert schedule[2]["scheduled_date"] == "2026-10-06"

assert schedule[3]["scheduled_date"] == "2026-10-07"
assert schedule[4]["scheduled_date"] == "2026-10-07"

print("\n✓ Basic scheduling test passed")


# -----------------------------------
# Test 3: Invalid daily capacity
# -----------------------------------

try:
    create_schedule(
        tasks=[
            {"title": "Large task", "duration": 90}
        ],
        start_date=date(2026, 10, 6),
        deadline=date(2026, 10, 8),
        daily_minutes=60,
    )

    print("✗ Error test failed")

except ValueError:
    print("✓ Invalid task duration test passed")


print("\n=== ALL SCHEDULER TESTS PASSED ===")