import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent.agent import get_course_policy

# Test the function
print("Testing get_course_policy function:")

# Test valid policy
result = get_course_policy("late_submission")
print("Test 1 - late_submission:")
print(json.dumps(result, indent=2, ensure_ascii=False))

# Test invalid policy
result = get_course_policy("invalid_policy")
print("\nTest 2 - invalid_policy:")
print(json.dumps(result, indent=2, ensure_ascii=False))

# Test another valid policy
result = get_course_policy("scoring")
print("\nTest 3 - scoring:")
print(json.dumps(result, indent=2, ensure_ascii=False))