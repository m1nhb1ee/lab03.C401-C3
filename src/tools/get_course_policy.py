import os
import json
from typing import Dict, Any


def get_course_policy(policy_type: str) -> Dict[str, Any]:
    try:
        # Load the JSON file
        json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'quy_dinh_mon_hoc.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            policies = json.load(f)

        # Check if policy_type exists
        if policy_type in policies:
            policy = policies[policy_type]
            return {
                "success": True,
                "policy_type": policy_type,
                "description": policy.get("description", ""),
                "details": policy.get("details", "")
            }
        else:
            return {
                "success": False,
                "policy_type": policy_type,
                "description": "",
                "details": f"Policy type '{policy_type}' not found. Available types: {', '.join(policies.keys())}"
            }

    except FileNotFoundError:
        return {
            "success": False,
            "policy_type": policy_type,
            "description": "",
            "details": "quy_dinh_mon_hoc.json file not found."
        }
    except json.JSONDecodeError:
        return {
            "success": False,
            "policy_type": policy_type,
            "description": "",
            "details": "Error parsing quy_dinh_mon_hoc.json file."
        }
    except Exception as e:
        return {
            "success": False,
            "policy_type": policy_type,
            "description": "",
            "details": f"Unexpected error: {str(e)}"
        }
    """
    Lấy quy định của môn học từ file quy_dinh_mon_hoc.json
    Trả lời câu hỏi về deadline, scoring, attendance, etc.

    Parameter:
    - policy_type: str (e.g., "deadline", "scoring", "late_submission", "grading")

    Output:
    {
        "success": bool,
        "policy_type": str,
        "description": str,
        "details": str
    }
    """