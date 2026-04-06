"""
Discount and membership tool
"""

from .base_tool import BaseTool
import json

class DiscountTool(BaseTool):
    """Check VIP discount for bookings"""
    
    def __init__(self):
        super().__init__(
            name="check_vip_discount",
            description="Check if user has VIP membership and get discount percentage. "
                       "Input: user_id (string, optional - if not provided, assumes no VIP). "
                       "Returns discount percentage. "
                       "Example: check_vip_discount(user_id='trung_001')"
        )
        
        # Mock VIP users database
        self.vip_users = {
            "vip_user": 20,      # 20% discount
            "premium_user": 15,  # 15% discount
            "member": 5,         # 5% discount
        }
    
    def execute(self, user_id: str = None, **kwargs) -> str:
        """
        Check VIP discount
        Returns discount percentage
        """
        try:
            if not user_id:
                return json.dumps({
                    "success": True,
                    "user_id": "anonymous",
                    "discount_percentage": 0,
                    "message": "No VIP membership found"
                })
            
            # In a real system, this would query a database
            # For demo, we'll check if user_id contains certain keywords
            user_lower = user_id.lower()
            
            discount = 0
            membership_type = "None"
            
            if "vip" in user_lower or "premium" in user_lower:
                discount = 20
                membership_type = "VIP Premium"
            elif "member" in user_lower:
                discount = 5
                membership_type = "Member"
            
            return json.dumps({
                "success": True,
                "user_id": user_id,
                "membership_type": membership_type,
                "discount_percentage": discount,
                "message": f"{discount}% discount applied" if discount > 0 else "No discount available"
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })
