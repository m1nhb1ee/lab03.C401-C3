import json


class LearningRoadmapTool:
    def __init__(self, data):
        self.data = data

    def create_learning_roadmap(
        self,
        topic: str,
        target_level: str,
        include_assignments: bool = True
    ):
        # Validate topic
        if topic not in self.data:
            return {
                "success": False,
                "topic": topic,
                "roadmap": []
            }

        levels = self.data[topic]["levels"]

        level_order = ["beginner", "intermediate", "advanced"]

        if target_level not in level_order:
            return {
                "success": False,
                "topic": topic,
                "roadmap": []
            }

        target_index = level_order.index(target_level)

        roadmap = []

        for lvl in levels:
            current_index = level_order.index(lvl["level"])

            if current_index > target_index:
                break

            item = {
                "level": lvl["level_name"],
                "concepts": lvl["concepts"],
                "learning_resources": lvl["learning_resources"],
                "estimated_hours": lvl["estimated_hours"]
            }

            if include_assignments:
                item["practice_problems"] = lvl["practice_problems"]

            roadmap.append(item)

        return {
            "success": True,
            "topic": topic,
            "roadmap": roadmap
        }


# ===== LOAD DATA =====
def load_data():
    with open("data\\learning_roadmaps.json", "r", encoding="utf-8") as f:
        return json.load(f)


# ===== DEMO USAGE =====
def main():
    data = load_data()
    tool = LearningRoadmapTool(data)

    topic = input("Topic (pointer, recursion, string, array): ").strip()
    level = input("Target level (beginner/intermediate/advanced): ").strip()

    result = tool.create_learning_roadmap(
        topic=topic,
        target_level=level,
        include_assignments=True
    )

    if not result["success"]:
        print("❌ Invalid input")
        return

    print(f"\n=== ROADMAP: {result['topic']} ===")

    for i, stage in enumerate(result["roadmap"], 1):
        print(f"\nLevel {i}: {stage['level']}")
        print(f"⏳ Estimated: {stage['estimated_hours']} hours")

        print("\n🧠 Concepts:")
        for c in stage["concepts"]:
            print(f" - {c}")

        print("\n📖 Resources:")
        for r in stage["learning_resources"]:
            print(f" - {r}")

        if "practice_problems" in stage:
            print("\n🛠 Practice:")
            for p in stage["practice_problems"]:
                print(f" - {p}")


if __name__ == "__main__":
    main()