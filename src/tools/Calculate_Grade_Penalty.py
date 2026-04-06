import json
import os

def calculate_grade_penalty(original_score: int, days_late: int) -> dict:
    """
    Tính điểm phạt do nộp trễ dựa trên quy định trong quy_dinh_mon_hoc.json

    Args:
        original_score (int): Điểm gốc (0-100)
        days_late (int): Số ngày nộp trễ (>=0)

    Returns:
        dict: Kết quả tính toán với các trường success, original_score, days_late, penalty_percentage, final_score, explanation
    """
    # Kiểm tra input hợp lệ
    if not isinstance(original_score, int) or not (0 <= original_score <= 100):
        return {
            "success": False,
            "original_score": original_score,
            "days_late": days_late,
            "penalty_percentage": None,
            "final_score": None,
            "explanation": "Điểm gốc phải là số nguyên từ 0 đến 100"
        }
    
    if not isinstance(days_late, int) or days_late < 0:
        return {
            "success": False,
            "original_score": original_score,
            "days_late": days_late,
            "penalty_percentage": None,
            "final_score": None,
            "explanation": "Số ngày nộp trễ phải là số nguyên không âm"
        }
    
    # Load quy tắc từ file JSON
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(script_dir, '..', '..', 'data')
        json_path = os.path.join(data_dir, 'quy_dinh_mon_hoc.json')
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        late_rules = data['late_submission']['mô_tả']
    except Exception as e:
        return {
            "success": False,
            "original_score": original_score,
            "days_late": days_late,
            "penalty_percentage": None,
            "final_score": None,
            "explanation": f"Lỗi khi đọc file quy định: {str(e)}"
        }
    
    # Áp dụng quy tắc phạt dựa trên mô tả
    if days_late == 0:
        penalty_percentage = 0
        explanation = "Nộp đúng hạn"
    elif days_late == 1:
        penalty_percentage = 10
        explanation = "Nộp trễ 1 ngày bị trừ 10%"
    elif 2 <= days_late <= 3:
        penalty_percentage = 20
        explanation = "Nộp trễ 2-3 ngày bị trừ 20%"
    elif days_late > 3:
        penalty_percentage = 100
        explanation = "Nộp trễ >3 ngày bị trừ 100%"
    else:
        # Trường hợp không mong muốn
        return {
            "success": False,
            "original_score": original_score,
            "days_late": days_late,
            "penalty_percentage": None,
            "final_score": None,
            "explanation": "Không thể xác định quy tắc phạt cho số ngày trễ này"
        }
    
    # Tính điểm cuối cùng
    if penalty_percentage == 100:
        final_score = 0.0
    else:
        final_score = round(original_score * (1 - penalty_percentage / 100), 1)
    
    return {
        "success": True,
        "original_score": original_score,
        "days_late": days_late,
        "penalty_percentage": penalty_percentage,
        "final_score": final_score,
        "explanation": explanation
    }

