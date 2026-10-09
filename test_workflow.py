from backend.services.assignment_analyzer import analyze_assignment
from backend.services.task_generator import generate_tasks


print("========================================")
print("        NEUROPILOT ASSIGNMENT INPUT")
print("========================================")

assignment_text = input(
    "\nEnter your assignment:\n> "
)

assignment = analyze_assignment(assignment_text)

print("\n=== WHAT NEUROPILOT UNDERSTOOD ===")

for key, value in assignment.items():
    print(f"{key}: {value}")


tasks = generate_tasks(assignment)

print("\n=== YOUR MICRO-TASKS ===")

total_minutes = 0

for i, task in enumerate(tasks, start=1):

    print(
        f"{i}. {task['title']} "
        f"({task['duration']} min)"
    )

    total_minutes += task["duration"]


print("\nTotal tasks:", len(tasks))
print("Estimated work:", total_minutes, "minutes")