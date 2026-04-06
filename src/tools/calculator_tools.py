"""
Cost calculator tool
"""

from .base_tool import BaseTool
import json

class CostCalculatorTool(BaseTool):
    """Calculate total booking cost with discount"""
    
    def __init__(self):
        super().__init__(
            name="calculate_total_cost",
            description="Calculate total cost of booking (flight + hotel) with discount applied. "
                       "Input: flight_cost (int, VND), hotel_cost (int, VND), discount_percentage (int, 0-100). "
                       "Returns breakdown and total. "
                       "Example: calculate_total_cost(flight_cost=1000000, hotel_cost=3600000, discount_percentage=20)"
        )
    
    def execute(self, flight_cost: int, hotel_cost: int, discount_percentage: int = 0, **kwargs) -> str:
        """
        Calculate total cost
        Returns cost breakdown
        """
        try:
            # Validate inputs
            if flight_cost < 0 or hotel_cost < 0 or not (0 <= discount_percentage <= 100):
                return json.dumps({
                    "success": False,
                    "error": "Invalid input values"
                })
            
            # Calculate subtotal
            subtotal = flight_cost + hotel_cost
            
            # Calculate discount amount
            discount_amount = int(subtotal * discount_percentage / 100)
            
            # Calculate final total
            total_cost = subtotal - discount_amount
            
            return json.dumps({
                "success": True,
                "breakdown": {
                    "flight_cost": flight_cost,
                    "hotel_cost": hotel_cost,
                    "subtotal": subtotal,
                    "discount_percentage": discount_percentage,
                    "discount_amount": discount_amount,
                    "total_cost": total_cost
                },
                "message": f"Total cost after {discount_percentage}% discount: {total_cost:,} VND"
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })
