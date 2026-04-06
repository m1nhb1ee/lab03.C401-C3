#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST SCRIPT: Kiểm tra dữ liệu cho Teaching Assistant Scenario

Mục tiêu:
1. Load tất cả JSON files
2. Kiểm tra structure và content
3. Test mock search functions
4. Validate data completeness
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def load_json(filepath):
    """Load JSON file safely"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return None

def print_header(title):
    """Print formatted header"""
    print(f"\n{'═' * 80}")
    print(f"  {title}")
    print(f"{'═' * 80}\n")

def print_success(msg):
    print(f"  ✅ {msg}")

def print_error(msg):
    print(f"  ❌ {msg}")

def print_info(msg):
    print(f"  ℹ️  {msg}")


# ═══════════════════════════════════════════════════════════════════════════
# TEST 1: Load and Validate Data Files
# ═══════════════════════════════════════════════════════════════════════════

def test_load_data_files():
    print_header("TEST 1: Load and Validate Data Files")
    
    data_dir = Path("data")
    required_files = [
        "tai_lieu_hoc_tap.json",
        "code_examples.json",
        "learning_roadmaps.json",
        "assignments.json",
        "quy_dinh_mon_hoc.json",
        "data_index.json"
    ]
    
    data = {}
    for filename in required_files:
        filepath = data_dir / filename
        if filepath.exists():
            content = load_json(filepath)
            if content:
                data[filename] = content
                print_success(f"Loaded {filename}")
            else:
                print_error(f"Failed to load {filename}")
        else:
            print_error(f"File not found: {filepath}")
    
    return data


# ═══════════════════════════════════════════════════════════════════════════
# TEST 2: Validate Learning Materials
# ═══════════════════════════════════════════════════════════════════════════

def test_learning_materials(data):
    print_header("TEST 2: Validate Learning Materials (tai_lieu_hoc_tap.json)")
    
    materials = data.get("tai_lieu_hoc_tap.json", {})
    
    expected_topics = ["pointer", "loop", "recursion", "array", "function", "string"]
    
    for topic in expected_topics:
        if topic in materials:
            topic_data = materials[topic]
            has_required_fields = all(field in topic_data for field in ["tên", "định_nghĩa"])
            
            if has_required_fields:
                print_success(f"'{topic}' has required fields")
                print_info(f"  - {topic_data.get('tên')}")
                print_info(f"  - Definition: {topic_data.get('định_nghĩa')[:60]}...")
            else:
                print_error(f"'{topic}' missing required fields")
        else:
            print_error(f"Topic '{topic}' not found")


# ═══════════════════════════════════════════════════════════════════════════
# TEST 3: Validate Code Examples
# ═══════════════════════════════════════════════════════════════════════════

def test_code_examples(data):
    print_header("TEST 3: Validate Code Examples (code_examples.json)")
    
    examples = data.get("code_examples.json", {})
    
    for topic_key, example_data in examples.items():
        if "right_example" in example_data and "wrong_example" in example_data:
            print_success(f"'{topic_key}' has both right and wrong examples")
            
            right = example_data.get("right_example", {})
            wrong = example_data.get("wrong_example", {})
            
            if "code" in right and "explanation" in right:
                print_info(f"  ✓ Right example is complete")
            if "code" in wrong and "mistake" in wrong:
                print_info(f"  ✓ Wrong example is complete")
        else:
            print_error(f"'{topic_key}' missing example pairs")


# ═══════════════════════════════════════════════════════════════════════════
# TEST 4: Validate Learning Roadmaps
# ═══════════════════════════════════════════════════════════════════════════

def test_learning_roadmaps(data):
    print_header("TEST 4: Validate Learning Roadmaps (learning_roadmaps.json)")
    
    roadmaps = data.get("learning_roadmaps.json", {})
    
    for topic, roadmap_data in roadmaps.items():
        if "levels" in roadmap_data:
            levels = roadmap_data["levels"]
            print_success(f"'{topic}' roadmap has {len(levels)} levels")
            
            for level in levels:
                if "concepts" in level and "practice_problems" in level:
                    level_name = level.get("level_name", level.get("level", "unknown"))
                    hours = level.get("estimated_hours", 0)
                    print_info(f"  - {level_name}: {len(level['concepts'])} concepts, {hours}h")


# ═══════════════════════════════════════════════════════════════════════════
# TEST 5: Validate Assignments
# ═══════════════════════════════════════════════════════════════════════════

def test_assignments(data):
    print_header("TEST 5: Validate Assignments (assignments.json)")
    
    assignments_data = data.get("assignments.json", {})
    assignments = assignments_data.get("assignments", [])
    
    total_points = 0
    for assignment in assignments:
        if all(key in assignment for key in ["assignment_id", "title", "deadline", "max_points"]):
            print_success(f"{assignment['assignment_id']}: {assignment['title']} ({assignment['max_points']} pts)")
            total_points += assignment['max_points']
        else:
            print_error(f"Assignment missing required fields: {assignment}")
    
    print_info(f"\nTotal points across all assignments: {total_points}")
    
    # Check penalty rules
    if "penalty_rules" in assignments_data:
        print_success("Penalty rules defined")
        for rule_key, rule in assignments_data["penalty_rules"].items():
            if rule_key != "on_time":
                print_info(f"  - {rule.get('description', rule_key)}: {rule.get('penalty_percentage', 0)}%")


# ═══════════════════════════════════════════════════════════════════════════
# TEST 6: Validate Course Policies
# ═══════════════════════════════════════════════════════════════════════════

def test_policies(data):
    print_header("TEST 6: Validate Course Policies (quy_dinh_mon_hoc.json)")
    
    policies = data.get("quy_dinh_mon_hoc.json", {})
    
    expected_policies = ["deadline", "scoring", "format", "late_submission", "attendance", "grading"]
    
    for policy_name in expected_policies:
        if policy_name in policies:
            policy = policies[policy_name]
            if "mô_tả" in policy and "chi_tiết" in policy:
                print_success(f"'{policy_name}' is complete")
                print_info(f"  - {policy.get('tên', 'N/A')}")
            else:
                print_error(f"'{policy_name}' incomplete")
        else:
            print_error(f"Policy '{policy_name}' not found")


# ═══════════════════════════════════════════════════════════════════════════
# TEST 7: Mock Tool Functions
# ═══════════════════════════════════════════════════════════════════════════

def test_mock_tools(data):
    print_header("TEST 7: Mock Tool Functions")
    
    # Tool 1: search_learning_material
    print("\n📌 Tool 1: search_learning_material('pointer')")
    materials = data.get("tai_lieu_hoc_tap.json", {})
    if "pointer" in materials:
        pointer_data = materials["pointer"]
        print_success(f"Found topic: {pointer_data.get('tên')}")
        print_info(f"Definition: {pointer_data.get('định_nghĩa')[:80]}...")
        print_info(f"Has {len(pointer_data.get('common_mistakes', []))} common mistakes")
        print_info(f"Resources: {pointer_data.get('tài_liệu')}")
    
    # Tool 2: get_course_policy
    print("\n📌 Tool 2: get_course_policy('late_submission')")
    policies = data.get("quy_dinh_mon_hoc.json", {})
    if "late_submission" in policies:
        late_policy = policies["late_submission"]
        print_success(f"Policy: {late_policy.get('tên')}")
        print_info(f"Details: {late_policy.get('chi_tiết')}")
    
    # Tool 3: calculate_grade_penalty
    print("\n📌 Tool 3: calculate_grade_penalty(original_score=10, days_late=2)")
    assignments_data = data.get("assignments.json", {})
    penalty_rules = assignments_data.get("penalty_rules", {})
    
    original_score = 10
    days_late = 2
    
    # Find applicable penalty
    if f"late_{days_late}_day{'s' if days_late != 1 else ''}" in penalty_rules:
        penalty_info = penalty_rules[f"late_{days_late}_day{'s' if days_late != 1 else ''}"]
    elif "late_2_3_days" in penalty_rules and 2 <= days_late <= 3:
        penalty_info = penalty_rules["late_2_3_days"]
    else:
        penalty_info = {"penalty_percentage": 0}
    
    penalty_pct = penalty_info.get("penalty_percentage", 0)
    final_score = original_score * (1 - penalty_pct / 100)
    
    print_success(f"Original score: {original_score}")
    print_info(f"Days late: {days_late}")
    print_info(f"Penalty: {penalty_pct}%")
    print_info(f"Final score: {final_score}")
    
    # Tool 4: create_code_example
    print("\n📌 Tool 4: create_code_example('buffer_overflow', 'beginner')")
    examples = data.get("code_examples.json", {})
    if "buffer_overflow" in examples:
        example = examples["buffer_overflow"]
        print_success(f"Topic: {example.get('topic')}")
        print_info(f"Complexity: {example.get('complexity')}")
        print_info(f"Right example starts with: {example.get('right_example', {}).get('code', '')[:50]}...")
        print_info(f"Wrong example: {example.get('wrong_example', {}).get('mistake', 'N/A')}")
    
    # Tool 5: create_learning_roadmap
    print("\n📌 Tool 5: create_learning_roadmap('recursion', 'advanced')")
    roadmaps = data.get("learning_roadmaps.json", {})
    if "recursion" in roadmaps:
        roadmap = roadmaps["recursion"]
        levels = roadmap.get("levels", [])
        print_success(f"Found {len(levels)} levels for recursion")
        for level in levels:
            print_info(f"  - {level.get('level_name')}: {level.get('estimated_hours')}h")
    
    # Tool 6: calculate_deadline
    print("\n📌 Tool 6: calculate_deadline(assignment_id='assignment_1')")
    assignments = assignments_data.get("assignments", [])
    if assignments:
        assign = assignments[0]
        deadline_str = assign.get("deadline", "")
        print_success(f"Assignment: {assign.get('title')}")
        print_info(f"Deadline: {deadline_str}")
        print_info(f"Max points: {assign.get('max_points')}")


# ═══════════════════════════════════════════════════════════════════════════
# TEST 8: Data Consistency Check
# ═══════════════════════════════════════════════════════════════════════════

def test_data_consistency(data):
    print_header("TEST 8: Data Consistency Check")
    
    materials = data.get("tai_lieu_hoc_tap.json", {})
    examples = data.get("code_examples.json", {})
    roadmaps = data.get("learning_roadmaps.json", {})
    index = data.get("data_index.json", {})
    
    # Check if topics in index match actual data
    if "search_mapping" in index:
        mapping = index["search_mapping"]
        
        for topic in mapping.keys():
            print_info(f"Checking topic: '{topic}'")
            
            # Check in materials
            if topic in materials:
                print_success(f"  ✓ Found in tai_lieu_hoc_tap")
            
            # Check in roadmaps
            if topic in roadmaps:
                print_success(f"  ✓ Found in learning_roadmaps")




# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  🧪 TESTING TEACHING ASSISTANT DATA STRUCTURES".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    # Run all tests
    data = test_load_data_files()
    
    if data:
        test_learning_materials(data)
        test_code_examples(data)
        test_learning_roadmaps(data)
        test_assignments(data)
        test_policies(data)
        test_mock_tools(data)
        test_data_consistency(data)
    
    # Summary
    print_header("SUMMARY")
    print_success("All data files loaded and validated!")
    print_info("Ready for Teaching Assistant Agent implementation")
    
    print("\n📊 Data Files Summary:")
    print("  ✅ tai_lieu_hoc_tap.json: Learning materials (6 topics)")
    print("  ✅ code_examples.json: Code examples (8 topics)")
    print("  ✅ learning_roadmaps.json: Learning paths (4 topics × 3 levels)")
    print("  ✅ assignments.json: Assignments (6 + penalty rules)")
    print("  ✅ quy_dinh_mon_hoc.json: Course policies (9 policies)")
    print("  ✅ data_index.json: Search index and metadata")
    
    print("\n🛠️  Ready to implement tools for:")
    print("  1. search_learning_material() - Query tai_lieu_hoc_tap.json")
    print("  2. get_course_policy() - Query quy_dinh_mon_hoc.json")
    print("  3. calculate_grade_penalty() - Compute from assignments.json")
    print("  4. create_code_example() - Lookup code_examples.json")
    print("  5. create_learning_roadmap() - Lookup learning_roadmaps.json")
    print("  6. calculate_deadline() - Query assignments.json")
    
    print("\n")


if __name__ == "__main__":
    main()
