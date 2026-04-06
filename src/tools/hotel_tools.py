"""
Hotel search tool
"""

from .base_tool import BaseTool
import json

class HotelBookingTool(BaseTool):
    """Search for hotels in a city"""
    
    def __init__(self):
        super().__init__(
            name="search_hotels",
            description="Search for hotels in a city with specific requirements. "
                       "Input: city (string), stars (int: 3-5), nights (int), max_price_per_night (int, in VND). "
                       "Returns hotel options matching criteria. "
                       "Example: search_hotels(city='Hà Nội', stars=4, nights=3, max_price_per_night=2000000)"
        )
        
        # Mock hotel data
        self.hotels_db = {
            "Hà Nội": {
                5: [
                    {"name": "Hanoi Luxury Hotel", "price_per_night": 3500000, "stars": 5, "rating": 4.9},
                    {"name": "Grand Palace Hanoi", "price_per_night": 3200000, "stars": 5, "rating": 4.8},
                ],
                4: [
                    {"name": "Hanoi Garden Hotel", "price_per_night": 1800000, "stars": 4, "rating": 4.7},
                    {"name": "Central Hanoi Inn", "price_per_night": 1500000, "stars": 4, "rating": 4.6},
                    {"name": "Hanoi Comfort Hotel", "price_per_night": 1200000, "stars": 4, "rating": 4.5},
                ],
                3: [
                    {"name": "Budget Hanoi", "price_per_night": 600000, "stars": 3, "rating": 4.2},
                ],
            },
            "TP.HCM": {
                5: [
                    {"name": "Saigon Luxury", "price_per_night": 4000000, "stars": 5, "rating": 4.9},
                ],
                4: [
                    {"name": "Saigon Garden", "price_per_night": 2000000, "stars": 4, "rating": 4.7},
                    {"name": "Downtown Hotel", "price_per_night": 1600000, "stars": 4, "rating": 4.6},
                ],
            }
        }
    
    def execute(self, city: str, stars: int, nights: int, max_price_per_night: int, **kwargs) -> str:
        """
        Execute hotel search
        Returns JSON string with matching hotels
        """
        try:
            # Validate inputs
            if not (3 <= stars <= 5):
                return json.dumps({
                    "success": False,
                    "error": "Stars must be between 3 and 5"
                })
            
            if nights <= 0:
                return json.dumps({
                    "success": False,
                    "error": "Nights must be positive"
                })
            
            # Get hotels in city
            hotels_in_city = self.hotels_db.get(city, {})
            available_hotels = hotels_in_city.get(stars, [])
            
            # Filter by price
            matching_hotels = [
                h for h in available_hotels 
                if h["price_per_night"] <= max_price_per_night
            ]
            
            if not matching_hotels:
                # Try lower star rate
                for star_level in range(stars - 1, 2, -1):
                    available_hotels = hotels_in_city.get(star_level, [])
                    matching_hotels = [
                        h for h in available_hotels 
                        if h["price_per_night"] <= max_price_per_night
                    ]
                    if matching_hotels:
                        break
            
            if not matching_hotels:
                return json.dumps({
                    "success": False,
                    "message": f"No hotels found in {city} with {stars}-stars under {max_price_per_night} VND per night"
                })
            
            # Calculate total cost for each hotel
            hotels_with_total = [
                {**h, "total_cost": h["price_per_night"] * nights}
                for h in matching_hotels
            ]
            
            # Sort by price
            hotels_with_total.sort(key=lambda x: x["price_per_night"])
            
            return json.dumps({
                "success": True,
                "city": city,
                "nights": nights,
                "hotels": hotels_with_total,
                "cheapest_total": min(h["total_cost"] for h in hotels_with_total)
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })
