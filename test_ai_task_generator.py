
from backend.services.assignment_analyzer import analyze_assignment
from backend.services.ai_task_generator import generate_ai_tasks


def main():
    print("=" * 55)
    print("NEUROPILOT - AI TASK GENERATION TEST")
    print("=" * 55)

    raw_text = input("\nEnter your assignment:\n> ").strip()

    if not raw_text:
        print("Assignment cannot be empty.")
        return

    try:
        assignment = analyze_assignment(raw_text)
        result = generate_ai_tasks(assignment)

        print("\nAI task plan generated successfully.")
        print("Summary:", result["assignment_summary"])
        print("Type:", result["assignment_type"])
        print("\nSTEP-BY-STEP TASKS")

        for index, task in enumerate(result["tasks"], start=1):
            print(f"\n{index}. {task['title']}")
            print("   Description:", task["description"])
            print("   Duration:", task["duration"], "minutes")
            print("   Difficulty:", task["difficulty"])
            print("   Prerequisites:", task["prerequisite_ids"])
            print("   Completion criteria:")
            for criterion in task["completion_criteria"]:
                print("    -", criterion)

    except Exception as error:
        print("\nTask generation failed.")
        print(type(error).__name__ + ":", error)


if __name__ == "__main__":
    main()
