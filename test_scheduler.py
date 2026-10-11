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

print("\n[PASS] Basic scheduling test passed")


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

    print("[FAIL] Error test failed")

except ValueError:
    print("[PASS] Invalid task duration test passed")


# -----------------------------------
# Test 4: Progressive daily scheduling
# -----------------------------------

daily_tasks = [
    {"title": "Review DSA concepts", "duration": 30},
    {"title": "Solve 5 medium problems", "duration": 45},
    {"title": "Review solutions", "duration": 20},
    {"title": "Mock simulation", "duration": 25},
]

prog_schedule = create_schedule(
    tasks=daily_tasks,
    start_date=date(2026, 10, 11),
    deadline=date(2026, 10, 26),
    daily_minutes=60,
    repeat_daily=True,
)

assert len(prog_schedule) > 0
prog_dates = sorted(set(t["scheduled_date"] for t in prog_schedule))
assert prog_dates[0] == "2026-10-11"
assert prog_dates[-1] == "2026-10-26"
assert len(prog_dates) == 16
print("[PASS] Progressive multi-day daily schedule test passed (16 days covered)")


# -----------------------------------
# Test 5: 1-2 day schedule
# -----------------------------------

two_day_tasks = [
    {"title": "Review DSA concepts", "duration": 30},
    {"title": "Solve 3 easy problems", "duration": 30},
    {"title": "Solve 2 medium problems", "duration": 30},
    {"title": "Review solutions", "duration": 30},
]

short_schedule = create_schedule(
    tasks=two_day_tasks,
    start_date=date(2026, 10, 11),
    deadline=date(2026, 10, 12),
    daily_minutes=60,
    repeat_daily=False,
)

short_dates = sorted(set(t["scheduled_date"] for t in short_schedule))
assert len(short_dates) == 2
assert short_dates[0] == "2026-10-11"
assert short_dates[1] == "2026-10-12"
print("[PASS] 1-2 day schedule test passed")


print("\n=== ALL SCHEDULER TESTS PASSED ===")