import os
import re
import json
from typing import List, Dict, Any
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

# tool get_course_policy
def get_course_policy(policy_type: str) -> Dict[str, Any]:
    """
    Lấy quy định của môn học từ quy_dinh_mon_hoc.json
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


class ReActAgent:
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join([
            f"- {t['name']}: {t['description']}" for t in self.tools
        ])

        return f"""
You are a ReAct Agent.

You MUST follow this loop:
Thought: reasoning
Action: {{"tool": "...", "args": {{...}}}}

After tool execution, you will receive:
Observation: result

Repeat until you can answer.

Available tools:
{tool_descriptions}

Rules:
- Action MUST be valid JSON
- DO NOT use markdown
- If you have enough info → Final Answer

Format strictly:
Thought: ...
Action: {{"tool": "...", "args": {{...}}}}

OR

Final Answer: ...
"""

    def run(self, user_input: str) -> str:
        logger.log_event("AGENT_START", {
            "input": user_input,
            "model": self.llm.model_name
        })

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": user_input}
        ]

        steps = 0

        while steps < self.max_steps:
            # 🔹 Call LLM
            result = self.llm.generate(messages)
            logger.log_event("LLM_RESPONSE", {"step": steps, "output": result})

            print(f"\nSTEP {steps}\n{result}")

            # 🔹 Check Final Answer
            if "Final Answer:" in result:
                final = result.split("Final Answer:")[-1].strip()

                logger.log_event("AGENT_END", {
                    "steps": steps,
                    "status": "success"
                })
                return final

            # 🔹 Parse Action JSON
            action_match = re.search(r'Action:\s*(\{.*\})', result)

            if not action_match:
                logger.log_event("PARSING_ERROR", {"output": result})
                return "Error: Cannot parse action."

            try:
                action_json = json.loads(action_match.group(1))
                tool_name = action_json.get("tool")
                args = action_json.get("args", {})

            except Exception as e:
                logger.log_event("JSON_ERROR", {"error": str(e)})
                return f"JSON parse error: {e}"

            # 🔹 Execute Tool
            observation = self._execute_tool(tool_name, args)

            logger.log_event("TOOL_CALL", {
                "tool": tool_name,
                "args": args,
                "observation": observation
            })

            # 🔹 Append to messages (ReAct loop)
            messages.append({"role": "assistant", "content": result})
            messages.append({
                "role": "user",
                "content": f"Observation: {observation}"
            })

            steps += 1

        logger.log_event("AGENT_END", {
            "steps": steps,
            "status": "max_steps_exceeded"
        })

        return "Error: Max steps reached."

    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """
        Execute tool dynamically
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                try:
                    func = tool.get("func")

                    if func:
                        return str(func(**args))
                    else:
                        return f"Tool {tool_name} has no function."

                except Exception as e:
                    return f"Tool execution error: {str(e)}"

        return f"Tool {tool_name} not found."