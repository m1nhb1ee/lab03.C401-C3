"""
Flight search tool
"""

from .base_tool import BaseTool
from datetime import datetime
import json

class FlightBookingTool(BaseTool):
    """Search for flights between two cities"""
    
    def __init__(self):
        super().__init__(
            name="search_flights",
            description="Search for available flights between two cities on a specific date. "
                       "Returns flight options with prices. "
                       "Input: from_city (string), to_city (string), date (YYYY-MM-DD format). "
                       "Example: search_flights(from_city='TP.HCM', to_city='Hà Nội', date='2026-04-20')"
        )
        
        # Mock flight data (in real system, this would query API)
        self.flights_db = {
            ("TP.HCM", "Hà Nội"): [
                {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "10:00", "price": 1200000, "duration": "2h"},
                {"airline": "Vietjet Air", "departure": "10:30", "arrival": "12:30", "price": 800000, "duration": "2h"},
                {"airline": "Bamboo Airways", "departure": "14:00", "arrival": "16:00", "price": 950000, "duration": "2h"},
            ],
            ("Hà Nội", "TP.HCM"): [
                {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "11:00", "price": 1200000, "duration": "2h"},
                {"airline": "Vietjet Air", "departure": "11:30", "arrival": "13:30", "price": 800000, "duration": "2h"},
            ]
        }
    
    def execute(self, from_city: str, to_city: str, date: str, **kwargs) -> str:
        """
        Execute flight search
        Returns JSON string with flight options
        """
        try:
            # Validate date format
            datetime.strptime(date, "%Y-%m-%d")
            
            # Get flights (case-insensitive search)
            key = (from_city.strip(), to_city.strip())
            flights = self.flights_db.get(key, [])
            
            if not flights:
                return json.dumps({
                    "success": False,
                    "message": f"No flights found from {from_city} to {to_city} on {date}"
                })
            
            return json.dumps({
                "success": True,
                "date": date,
                "from": from_city,
                "to": to_city,
                "flights": flights,
                "cheapest_price": min(f["price"] for f in flights)
            })
        except ValueError as e:
            return json.dumps({
                "success": False,
                "error": f"Invalid date format. Use YYYY-MM-DD. Error: {str(e)}"
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })
