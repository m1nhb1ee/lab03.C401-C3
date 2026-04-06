"""
Agent v1 - ReAct Implementation
Implements the Thought-Action-Observation loop
"""

import os
import sys
import json
import time
import re
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.gemini_provider import GeminiProvider
from src.tools import get_tool, get_tools_description

class AgentV1:
    """
    ReAct Agent with Thought-Action-Observation loop
    
    Loop Flow:
    1. Thought: LLM thinks about what to do
    2. Action: LLM chooses a tool and parameters
    3. Observation: Execute tool and get result
    4. Repeat until "Final Answer"
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        max_steps: int = 10,
        log_dir: str = "logs"
    ):
        """Initialize agent"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.provider = GeminiProvider(model_name, self.api_key)
        self.max_steps = max_steps
        self.log_dir = log_dir
        
        # Setup logging
        Path(log_dir).mkdir(exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("agent_v1")
        
        # Add file handler
        log_file = Path(log_dir) / f"agent_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.logger.addHandler(file_handler)
        
        # Build system prompt with tool descriptions
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with tool descriptions"""
        return f"""You are an expert travel booking agent.
You have access to the following tools:

{get_tools_description()}

IMPORTANT: You MUST follow this exact format for your thoughts and actions:

When you need to use a tool, respond EXACTLY like this:
Thought: [what you need to do]
Action: [tool_name]
Input: {{"param1": value1, "param2": value2}}

When you have the final answer, respond EXACTLY like this:
Final Answer: [your complete answer]

Rules:
1. Always think before acting
2. Use tools to get real data (don't guess)
3. Extract specific values from tool responses
4. Calculate totals based on actual data
5. Apply discounts correctly
6. When done, give a clear Final Answer with all calculations

Example flow for complex query:
Thought: I need to search for flights first
Action: search_flights
Input: {{"from_city": "TP.HCM", "to_city": "Hà Nội", "date": "2026-04-20"}}

Then based on results, proceed to next step.
"""
    
    def _parse_action(self, response: str) -> Optional[tuple]:
        """
        Parse LLM response to extract Thought, Action, and Input
        
        Returns:
        (action_name, input_dict) or None if parse fails
        """
        try:
            # Pattern to match: Action: <name> and Input: <json>
            action_match = re.search(r'Action:\s*(\w+)', response, re.IGNORECASE)
            input_match = re.search(r'Input:\s*(\{.*?\})', response, re.DOTALL)
            
            if not action_match or not input_match:
                return None
            
            action_name = action_match.group(1).strip()
            input_str = input_match.group(1).strip()
            
            # Try to parse JSON
            input_dict = json.loads(input_str)
            
            return (action_name, input_dict)
        except (json.JSONDecodeError, AttributeError) as e:
            self.logger.error(f"Parse error: {str(e)}")
            return None
    
    def _execute_tool(self, tool_name: str, input_dict: Dict) -> str:
        """
        Execute a tool and return result
        
        Returns:
        JSON string result from tool
        """
        try:
            tool = get_tool(tool_name)
            if not tool:
                return json.dumps({
                    "success": False,
                    "error": f"Tool '{tool_name}' not found"
                })
            
            # Execute tool with unpacked kwargs
            result = tool.execute(**input_dict)
            return result
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Run the agent with ReAct loop
        
        Returns:
        {
            "success": bool,
            "query": str,
            "final_answer": str,
            "steps": int,
            "latency_ms": int,
            "tokens": {...},
            "trace": [...]  # Full trace of all steps
        }
        """
        start_time = time.time()
        trace = []
        step_count = 0
        
        try:
            self.logger.info(f"[START] Query: {query}")
            
            # Build initial prompt with user query
            full_prompt = f"{self.system_prompt}\n\nUser Query: {query}"
            
            while step_count < self.max_steps:
                step_count += 1
                self.logger.info(f"[STEP {step_count}]")
                
                # Call LLM
                llm_result = self.provider.generate(full_prompt, None)
                llm_response = llm_result["content"]
                
                self.logger.debug(f"LLM Response:\n{llm_response}")
                
                # Record step in trace
                step_trace = {
                    "step": step_count,
                    "llm_response": llm_response[:200],  # First 200 chars
                    "action": None,
                    "observation": None
                }
                trace.append(step_trace)
                
                # Check for Final Answer
                if "Final Answer:" in llm_response:
                    final_answer = llm_response.split("Final Answer:")[-1].strip()
                    self.logger.info(f"[FINAL] {final_answer[:100]}")
                    
                    return {
                        "success": True,
                        "query": query,
                        "final_answer": final_answer,
                        "steps": step_count,
                        "latency_ms": int((time.time() - start_time) * 1000),
                        "tokens": llm_result["usage"],
                        "trace": trace
                    }
                
                # Try to parse action
                action_result = self._parse_action(llm_response)
                
                if not action_result:
                    self.logger.warning(f"[STEP {step_count}] Failed to parse action")
                    step_trace["error"] = "Parse failed"
                    
                    # Add error to prompt for next iteration
                    full_prompt += f"\n\n{llm_response}\n\nPlease follow the exact format: Action: <name>, Input: <json>"
                    continue
                
                action_name, input_dict = action_result
                step_trace["action"] = f"{action_name}({json.dumps(input_dict)})"
                
                self.logger.info(f"[ACTION] {action_name} with input: {input_dict}")
                
                # Execute tool
                observation = self._execute_tool(action_name, input_dict)
                step_trace["observation"] = observation[:200] if observation else "No response"
                
                self.logger.info(f"[OBSERVATION] {observation[:100]}")
                
                # Add observation to prompt for next step
                full_prompt += f"\n\n{llm_response}\n\nObservation: {observation}"
            
            # Max steps exceeded
            self.logger.error(f"Exceeded max steps ({self.max_steps})")
            return {
                "success": False,
                "query": query,
                "error": f"Exceeded max steps: {self.max_steps}",
                "steps": step_count,
                "latency_ms": int((time.time() - start_time) * 1000),
                "trace": trace
            }
            
        except Exception as e:
            self.logger.error(f"[ERROR] {str(e)}")
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "steps": step_count,
                "latency_ms": int((time.time() - start_time) * 1000),
                "trace": trace
            }

# Backward compatibility with old skeleton
class ReActAgent(AgentV1):
    """Backward compatibility wrapper"""
    pass
