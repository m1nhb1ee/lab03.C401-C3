

import json
import os
from typing import Optional, Dict, List, Any
from pathlib import Path


class SearchLearningMaterialTool:
    """Tool tìm kiếm tài liệu học tập"""

    def __init__(self, data_dir: str = None):
        """
        Khởi tạo tool với đường dẫn đến folder data
        
        Args:
            data_dir: Đường dẫn đến folder data, mặc định tìm theo relative path
        """
        if data_dir is None:
            # Tìm folder data relative từ vị trí script
            current_dir = Path(__file__).parent.parent.parent
            data_dir = current_dir / "data"
        
        self.data_dir = Path(data_dir)
        self.learning_material_file = self.data_dir / "tai_lieu_hoc_tap.json"
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load dữ liệu từ file JSON"""
        try:
            with open(self.learning_material_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Không tìm thấy file: {self.learning_material_file}")
        except json.JSONDecodeError:
            raise ValueError(f"File JSON không hợp lệ: {self.learning_material_file}")
    
    def search(
        self,
        keyword: str,
        include_examples: bool = True,
        include_mistakes: bool = True
    ) -> Dict[str, Any]:
        """
        Search tài liệu theo keyword
        
        Args:
            keyword: Từ khóa cần tìm (e.g., "pointer", "recursion", "string", "array")
            include_examples: Bao gồm ví dụ code (mặc định True)
            include_mistakes: Bao gồm common mistakes (mặc định True)
        
        Returns:
            Dict với cấu trúc:
            {
                "success": bool,
                "topic": str,
                "definition": str,
                "examples": list,
                "common_mistakes": list,
                "resources": str
            }
        """
        # Normalize keyword: lowercase và remove spaces
        keyword = keyword.lower().strip()
        
        # Tìm topic trong data
        found_topic = None
        for topic_key in self.data.keys():
            if topic_key.lower() == keyword:
                found_topic = topic_key
                break
        
        if not found_topic:
            return {
                "success": False,
                "error": f"Không tìm thấy topic '{keyword}'. "
                        f"Các topic có sẵn: {list(self.data.keys())}",
                "available_topics": list(self.data.keys())
            }
        
        topic_data = self.data[found_topic]
        
        # Build response
        response = {
            "success": True,
            "topic": topic_data.get("tên", found_topic),
            "definition": topic_data.get("định_nghĩa", "")
        }
        
        # Add examples nếu được yêu cầu
        if include_examples:
            examples = []
            if "ví_dụ_1" in topic_data:
                examples.append({
                    "number": 1,
                    "code": topic_data["ví_dụ_1"].get("code", ""),
                    "explanation": topic_data["ví_dụ_1"].get("giải_thích", "")
                })
            if "ví_dụ_2" in topic_data:
                examples.append({
                    "number": 2,
                    "code": topic_data["ví_dụ_2"].get("code", ""),
                    "explanation": topic_data["ví_dụ_2"].get("giải_thích", "")
                })
            response["examples"] = examples
        
        # Add common mistakes nếu được yêu cầu
        if include_mistakes:
            response["common_mistakes"] = topic_data.get("common_mistakes", [])
        
        # Add resources
        response["resources"] = topic_data.get("tài_liệu", "")
        
        return response
    
    def list_all_topics(self) -> List[str]:
        """Liệt kê tất cả các topic có sẵn"""
        return list(self.data.keys())
    
    def get_all_data(self, keyword: str = None) -> Dict:
        """
        Lấy toàn bộ dữ liệu của một topic
        
        Args:
            keyword: Topic cần lấy
        
        Returns:
            Toàn bộ dữ liệu của topic
        """
        if keyword is None:
            return self.data
        
        keyword = keyword.lower().strip()
        for topic_key in self.data.keys():
            if topic_key.lower() == keyword:
                return self.data[topic_key]
        
        return {}


# Tạo instance global cho sử dụng dễ dàng
_search_tool = None

def get_search_tool(data_dir: str = None) -> SearchLearningMaterialTool:
    """Lấy instance của SearchLearningMaterialTool (singleton pattern)"""
    global _search_tool
    if _search_tool is None:
        _search_tool = SearchLearningMaterialTool(data_dir)
    return _search_tool


# Functions tiện lợi cho direct use
def search_learning_material(
    keyword: str,
    include_examples: bool = True,
    include_mistakes: bool = True,
    data_dir: str = None
) -> Dict[str, Any]:
    """
    Hàm tiện lợi để search tài liệu học tập
    
    Ví dụ:
        result = search_learning_material(
            keyword="pointer",
            include_examples=True,
            include_mistakes=True
        )
    """
    tool = get_search_tool(data_dir)
    return tool.search(keyword, include_examples, include_mistakes)


def list_all_topics(data_dir: str = None) -> List[str]:
    """Liệt kê tất cả các topic"""
    tool = get_search_tool(data_dir)
    return tool.list_all_topics()


def get_all_data(keyword: str = None, data_dir: str = None) -> Dict:
    """Lấy toàn bộ dữ liệu của một topic"""
    tool = get_search_tool(data_dir)
    return tool.get_all_data(keyword)


if __name__ == "__main__":
    # Test tool
    print("=" * 60)
    print("SEARCH LEARNING MATERIAL TOOL - TEST")
    print("=" * 60)
    
    # Test 1: List all topics
    print("\n1. Danh sách tất cả topics:")
    topics = list_all_topics()
    for topic in topics:
        print(f"   - {topic}")
    
    # Test 2: Search single topic
    print("\n2. Search 'pointer':")
    result = search_learning_material("pointer", include_examples=True, include_mistakes=True)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # Test 3: Search with only definition
    print("\n3. Search 'recursion' (chỉ definition):")
    result = search_learning_material("recursion", include_examples=False, include_mistakes=False)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # Test 4: Invalid keyword
    print("\n4. Search invalid keyword:")
    result = search_learning_material("invalid_topic")
    print(json.dumps(result, ensure_ascii=False, indent=2))
