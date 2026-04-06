"""
Tools for Travel Booking Assistant
Each tool must have:
- name: Unique identifier
- description: Clear description for LLM
- parameters: Input schema
- execute(): Function to run
"""

from src.tools.flight_tools import FlightBookingTool
from src.tools.hotel_tools import HotelBookingTool
from src.tools.discount_tools import DiscountTool
from src.tools.calculator_tools import CostCalculatorTool

# Lazy initialization to avoid circular imports
_tools = None

def _init_tools():
    """Initialize tools registry"""
    global _tools
    if _tools is None:
        _tools = {
            "search_flights": FlightBookingTool(),
            "search_hotels": HotelBookingTool(),
            "check_vip_discount": DiscountTool(),
            "calculate_total_cost": CostCalculatorTool(),
        }
    return _tools

def get_tool(tool_name):
    """Get a tool by name"""
    tools = _init_tools()
    return tools.get(tool_name)

def get_tools_description():
    """Return description of all tools for LLM system prompt"""
    tools = _init_tools()
    descriptions = []
    for name, tool in tools.items():
        descriptions.append(f"- {name}: {tool.description}")
    return "\n".join(descriptions)

def get_all_tools():
    """Get all available tools"""
    return _init_tools()
